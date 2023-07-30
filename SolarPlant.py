class SolarPlant:
    '''
    Model of the solar plant.
    '''
    def __init__(self, input_profile, param_dict):
        self.input_profile = input_profile
        self.rated_output_voltage_V = param_dict['rated_output_voltage_V']
        self.rated_output_current_A = param_dict['rated_output_current_A']
        self.temperature_coefficient_percent_per_C = param_dict['temperature_coefficient_percent_per_C']
        self.NMOT_C = param_dict["NMOT_C"]
        self.installed_capacity_Wp = param_dict["installed_capacity_Wp"]
        self.panel_temperature_offset_C = param_dict["panel_temperature_offset_C"]
        
        
        #initialise
        self.step(0)
        
    def get_power_kW(self):
        GHI_STC = 1000
        GHI_factor = self.GHI_Wm2 / GHI_STC
        panel_temperature_C = self.panel_temperature_offset_C + self.ambient_temperature_C
        
        if panel_temperature_C > self.NMOT_C:
            #percent of Pmax lost to temperature
            tmp = (panel_temperature_C - self.NMOT_C) * self.temperature_coefficient_percent_per_C
            
            assert tmp < 0
            
            temperature_factor = 1 + tmp/100
            
        else:
            temperature_factor = 1.0
            
        power_out_W = self.installed_capacity_Wp * GHI_factor * temperature_factor
        W_to_kW = 1/1000
        power_out_kW = power_out_W * W_to_kW
        
        return power_out_kW
    
    def get_voltage_V(self):
        pass
    def get_current_A(self):
        pass
    
    def step(self,time_step_s):
        self.input_profile.step(time_step_s)
        
        self.GHI_Wm2 = self.input_profile.GHI_Wm2
        self.ambient_temperature_C = self.input_profile.ambient_temperature_C