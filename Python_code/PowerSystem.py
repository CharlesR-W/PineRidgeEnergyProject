from PowerSystemController import PowerSystemController
class PowerSystem:
    '''
    Container class for the whole power system.  Contains and manages interaction
    between all component systems, as well as recording data for variables of interest
    '''
    def __init__(self,load_profile_kW, solar_plant, hydro_plant, battery_storage):
        self.load_profile_kW = load_profile_kW
        self.solar_plant = solar_plant
        self.hydro_plant = hydro_plant
        self.battery_storage = battery_storage
        self.controller = PowerSystemController(hydro_plant, battery_storage)
        
        record_variables = ["load_power_kW", "solar_power_kW", "hydro_power_kW", "target_hydro_power_kW", "target_battery_power_out_kW","target_power_dumped_kW", "battery_SoC"]
        self.data_arrs_dict = { k:[] for k in record_variables}
    
    def step(self,time_step_s):
        for tmp in [self.load_profile_kW, self.solar_plant, self.hydro_plant, self.battery_storage]:
            tmp.step(time_step_s)
        
        self.update_controller()
        
    
    def update_controller(self):
        
        #Get load demands
        load_power_kW = self.load_profile_kW.get_power_kW()
        
        #update generation amounts
        solar_power_kW = self.solar_plant.get_power_kW()
        hydro_power_kW = self.hydro_plant.get_power_kW()
        
        #feed inputs into the controller
        self.controller.update_inputs(load_power_kW, solar_power_kW, hydro_power_kW)
        #ask controller to calculate new targets
        self.controller.update_targets()
        
        #set new hydro target
        target_hydro_power_kW = self.controller.target_hydro_power_kW
        self.hydro_plant.set_target_output_kW(target_hydro_power_kW)
        
        #set new battery target
        target_battery_power_out_kW = self.controller.target_battery_power_out_kW
        self.battery_storage.set_requested_output_power_kW(target_battery_power_out_kW)
        
        
        #set new dump target
        target_power_dumped_kW = self.controller.target_power_dumped_kW

        battery_SoC = self.battery_storage.get_SoC()

        current_variables = {
            "load_power_kW":load_power_kW,
            "solar_power_kW":solar_power_kW,
            "hydro_power_kW":hydro_power_kW,
            "target_hydro_power_kW":target_hydro_power_kW,
            "target_battery_power_out_kW":target_battery_power_out_kW,
            "target_power_dumped_kW":target_power_dumped_kW,
            "battery_SoC":battery_SoC
            }

        self.record(current_variables)
        
    def restart_at_time_s(self, start_time_s):
        self.solar_plant.input_profile.current_time_s = start_time_s
        self.load_profile_kW.current_time_s = start_time_s
        
        self.hydro_plant.current_output_kW = 0
        self.battery_storage.usable_energy_remaining_kWh = self.battery_storage.usable_energy_capacity_kWh
        
        self.data_arrs_dict = { k:[] for k in self.data_arrs_dict.keys()}
        
    def record(self, variables):
        for k in self.data_arrs_dict.keys():
            self.data_arrs_dict[k].append( variables[k] )