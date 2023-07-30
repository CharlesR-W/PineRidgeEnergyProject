class PowerSystemController:
    '''
    Model of a control panel which controls plant outptut levels
    battery dis/charge, and load servicing
    '''
    def __init__(self,hydro_plant, battery_storage):
        self.hydro_plant = hydro_plant
        self.battery_storage = battery_storage
    
    def update_targets(self):
        #control logic: do as much as possible with solar
        
        #if the battery is capable of being charged, this is an available (optional) load
        bat_load_kW = self.battery_storage.max_charge_rate_unsigned_kW if not self.battery_storage.is_full() else 0
        
        #if battery is above this SoC, start slowing down the hydro
        battery_prorate_start= 0.8
        interp = (1-self.battery_storage.get_SoC()) / (1-battery_prorate_start)
        hydro_prorate_factor = 1 if self.battery_storage.get_SoC() < battery_prorate_start else interp
        
        target_hydro_power_kW = clamp(
            val = self.load_power_kW + bat_load_kW - self.solar_power_kW,
            lower = 0,
            upper = self.hydro_plant.rated_capacity_kW * hydro_prorate_factor,
            )
        
        target_battery_power_out_kW = clamp(
            val = self.load_power_kW - (self.solar_power_kW + self.hydro_power_kW),
            lower = -1*self.battery_storage.max_charge_rate_unsigned_kW,
            upper = self.battery_storage.max_charge_rate_unsigned_kW,
            )

        if ( #if this would draw when empty or charge the battery when full,
            target_battery_power_out_kW > 0 and self.battery_storage.is_empty()
            ) or (
            target_battery_power_out_kW < 0 and self.battery_storage.is_full()
            ):
            target_battery_power_out_kW = 0
        
        #remainder is dumped to grid
        target_power_dumped_kW = self.solar_power_kW + self.hydro_power_kW + target_battery_power_out_kW - self.load_power_kW
        
        self.target_hydro_power_kW = target_hydro_power_kW
        self.target_battery_power_out_kW = target_battery_power_out_kW
        self.target_power_dumped_kW = target_power_dumped_kW
        
    def update_inputs(self,load_power_kW, solar_power_kW, hydro_power_kW):
        self.load_power_kW = load_power_kW
        self.solar_power_kW = solar_power_kW
        self.hydro_power_kW = hydro_power_kW
        

def clamp(val,lower,upper):
    val = min(val,upper)
    val = max(lower,val)
    return val