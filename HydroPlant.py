import numpy as np
class HydroPlant:
    '''
    Model of the hydro plant
    '''
    
    def __init__(self, param_dict):
        #self.time_constant_s = param_dict['time_constant_s']
        self.rated_capacity_kW = param_dict['rated_capacity_kW']
        ramp_rate_percent_per_min = param_dict['ramp_rate_percent_per_min']
        
        min_to_s = 1/60
        self.ramp_rate_kW_per_s = (ramp_rate_percent_per_min/100) * self.rated_capacity_kW * min_to_s
        
        #NB We assume that the generator can vary electric field to keep the output voltage fixed
        self.output_voltage_V = param_dict['output_voltage_V']
        
        self.current_output_kW = 0
        self.target_output_kW = 0
    
    def set_target_output_kW(self,target_output_kW):
        self.target_output_kW = target_output_kW
    
    def update_current_output_kW(self, time_step_s):
        #calculate the error between target and current output
        error_kW = self.target_output_kW - self.current_output_kW
        
        max_ramp_kW = time_step_s * self.ramp_rate_kW_per_s
        
        #if we have enough ramp to fully match, do it
        if max_ramp_kW > abs(error_kW):
            self.current_output_kW = self.target_output_kW
        #else if not, move as much as possible
        else:
            #if error positive, ramp up, else down
            self.current_output_kW += max_ramp_kW * np.sign(error_kW)
    
    def get_power_kW(self):
        return self.current_output_kW
    
    def get_voltage_V(self):
        return self.output_voltage_V
    
    def get_current_A(self):
        kW_to_W = 1000
        current_A = self.current_output_kW * kW_to_W / self.output_voltage_V
        return current_A
    
    def step(self, time_step_s):
        # update the current output power and voltage (current is calculated on request)
        self.update_current_output_kW(time_step_s)