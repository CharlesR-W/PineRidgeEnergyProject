class BatteryStorage:
    '''
    Model of the battery storage system
    '''
    def __init__(self,param_dict):
        self.usable_energy_capacity_kWh = param_dict["usable_energy_capacity_kWh"]
        
        self.charge_efficiency_percent = param_dict["charge_efficiency_percent"]
        self.discharge_efficiency_percent = param_dict["discharge_efficiency_percent"]
        
        self.max_charge_rate_unsigned_kW = param_dict['max_charge_rate_unsigned_kW']
        self.max_discharge_rate_unsigned_kW = param_dict['max_discharge_rate_unsigned_kW']
        
        self.usable_energy_remaining_kWh = self.usable_energy_capacity_kWh
        self.requested_output_power_kW = 0
    
    def set_requested_output_power_kW(self, requested_output_power_kW):
        self.requested_output_power_kW = requested_output_power_kW
        # assert output power is within limits
        assert requested_output_power_kW <= self.max_discharge_rate_unsigned_kW
        assert requested_output_power_kW >= -self.max_charge_rate_unsigned_kW
        
        # assert that it can't draw power if empty or v.v.
        if requested_output_power_kW > 0:
            assert self.get_SoC() >= 0
        elif requested_output_power_kW < 0:
            assert self.get_SoC() <= 1.0
    
    def step(self, time_step_s):
        #p_remaining_kWh = self.SoC * self.usable_energy_capacity_kWh
        s_per_hour = 3600

        p_yielded_kWh = self.requested_output_power_kW * time_step_s / s_per_hour
        
        #if discharging:
        if self.requested_output_power_kW > 0:            
            #actual power consumed is higher
            p_consumed_kWh = p_yielded_kWh / (self.discharge_efficiency_percent/100)
        #if charging
        else:
            #actual power consumed is higher
            p_consumed_kWh = p_yielded_kWh / (self.charge_efficiency_percent/100)
            assert p_consumed_kWh <= 0
        
        self.usable_energy_remaining_kWh -= p_consumed_kWh
        
        
    def get_power_out_kW(self):
        return self.requested_output_power_kW
    
    def is_empty(self):
        return self.get_SoC() <= 0.0
    
    def is_full(self):
        return self.get_SoC() >= 1.0
    
    def get_SoC(self):
        SoC = self.usable_energy_remaining_kWh / self.usable_energy_capacity_kWh
        TOL = 1e-3
        assert SoC >= -1*TOL
        assert SoC <= 1.0 + TOL
        return SoC