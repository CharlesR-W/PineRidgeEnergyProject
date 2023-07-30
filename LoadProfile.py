import numpy as np
import matplotlib.pyplot as plt
class LoadProfile:
    '''
    Provides the total load as a function of time
    '''
    def __init__(self, load_param_dict):
        
        #set parameters for the profile
        self.fluctuation_scale = load_param_dict["fluctuation_scale"]
        self.fluctuation_period = load_param_dict["fluctuation_period"]
        
        self.fluctuation_factor = 1.00
        
        #should be a FUNCTION of time t (t from 0 to end of week, not absolute)
        self.normalised_load_function_s = load_param_dict["normalised_load_function_s"]
        
        # get some other parameters
        self.reservation_weekly_electricity_consumption_kWh = load_param_dict['reservation_weekly_electricity_consumption_kWh']

        voltage_demanded_V = load_param_dict['voltage_demanded_V']
        
        
        
        self.voltage_demanded_V = voltage_demanded_V
        
        self.current_time_s = 0
        
    
    def get_voltage_V(self):
        return self.voltage_demanded_V
    
    def get_power_kW(self):
        hours_per_week = 24*7
        scale = self.reservation_weekly_electricity_consumption_kWh / hours_per_week
        return self.get_noisy_load_unitless() * scale
        
    
    def get_current_A(self):
        kW_to_W = 1000
        current_A = self.get_power_kW() * kW_to_W / self.get_voltage_V()
        return current_A
    
    def step(self,time_step_s):
        self.current_time_s += time_step_s
    


    def get_noisy_load_unitless(self):
        base_load = self.normalised_load_function_s(self.current_time_s)
        
        #update fluctuation factor if necessary
        if self.current_time_s % self.fluctuation_period < 1:
    
            tmp = np.random.uniform(low=-1*self.fluctuation_scale, high = self.fluctuation_scale)
    
            self.fluctuation_factor += tmp
            self.fluctuation_factor += (1 - self.fluctuation_factor)*0.01

        
        return base_load * self.fluctuation_factor