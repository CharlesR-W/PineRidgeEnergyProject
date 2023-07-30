import numpy as np
import matplotlib.pyplot as plt
class LoadProfile:
    '''
    Provides the total load as a function of time
    '''
    def __init__(self,load_param_dict):
        
        #set parameters for the profile
        weekday_base = 1.0
        weekday_peak_base_ratio = load_param_dict['weekday_peak_base_ratio']
        weekend_peak_weekend_base_ratio = load_param_dict['weekend_peak_weekend_base_ratio']
        weekend_base_weekday_base_ratio = load_param_dict['weekend_base_weekday_base_ratio']
        fluctuation_scale = load_param_dict["fluctuation_scale"]

        #generate the array
        load_week_profile_unitless_seconds = load_data_generator(weekday_peak_base_ratio, weekend_base_weekday_base_ratio, weekend_peak_weekend_base_ratio, fluctuation_scale)
        
        # get some other parameters
        reservation_weekly_electricity_consumption_kWh = load_param_dict['reservation_weekly_electricity_consumption_kWh']

        voltage_demanded_V = load_param_dict['voltage_demanded_V']
        
        kWhs_to_kW=3600
        self.load_profile_kW_seconds = load_week_profile_unitless_seconds * reservation_weekly_electricity_consumption_kWh * kWhs_to_kW
        self.load_profile_kW_seconds = self.load_profile_kW_seconds[:,0]
        
        #print(np.shape(load_week_profile_unitless_seconds))
        
        self.voltage_demanded_V = voltage_demanded_V
        
        self.current_time_s = 0
        
    
    def get_voltage_V(self):
        return self.voltage_demanded_V
    
    def get_power_kW(self):
        idx = np.floor(self.current_time_s)
        idx = int(idx)
        if idx < len(self.load_profile_kW_seconds):
            return self.load_profile_kW_seconds[idx]
        else:
            print("[WARNING] exceeding load profile length")
            return self.load_profile_kW_seconds[-1]
    
    def get_current_A(self):
        kW_to_W = 1000
        current_A = self.get_power_kW() * kW_to_W / self.get_voltage_V()
        return current_A
    
    def step(self,time_step_s):
        self.current_time_s += time_step_s
    

"""
def representative_daily_load(baseline_consumption, peak_consumption):
    seconds_per_day = 24*3600
    seconds_per_hour = 3600
    load_curve = np.zeros([seconds_per_day,1])
    	
    morning_ramp_start_hr = 6 #am
    morning_ramp_end_hr = 9 #am
    evening_ramp_start_hr = 21 #PM
    evening_ramp_end_hr = 24 #PM
	
    for lv in range ( seconds_per_day ):
        hr = lv / seconds_per_hour
        if hr < morning_ramp_start_hr:
            cons =  baseline_consumption
        elif hr < morning_ramp_end_hr:
            cons = baseline_consumption + (hr-morning_ramp_start_hr)/(morning_ramp_end_hr - morning_ramp_start_hr) * (peak_consumption - baseline_consumption)
        elif hr < evening_ramp_start_hr:
            cons = peak_consumption
        elif hr < evening_ramp_end_hr:
            cons = peak_consumption + (hr-evening_ramp_start_hr)/(evening_ramp_end_hr - evening_ramp_start_hr) * (baseline_consumption- peak_consumption)

        load_curve[lv] = cons

    return load_curve
"""
    

def load_data_generator(weekday_peak_base_ratio, weekend_base_weekday_base_ratio, weekend_peak_weekend_base_ratio, fluctuation_scale):
    #generates a per-second profile of load for a single week
    #the output curve is normalised so that average consumption is 1
    #in all calculations below, the baseline weekday consumption is the
    #reference
    #e.g., weekday_peak_base_ratio specifies the ratio of peak consumption to
    #baseline within a weekday.  Others function analogously.

    #https://www.eia.gov/todayinenergy/detail.php?id=42915
    #data for load
    
    #run SIP_data.m
    seconds_per_day = 24*3600
    seconds_per_week=seconds_per_day*7
    days_per_week =7
    
    weekday_base=1.0
    #set the baseline load for the weekdays
    daily_load_base = np.ones([days_per_week,1]) * weekday_base
    daily_load_peak= np.ones([days_per_week,1]) * weekday_base * weekday_peak_base_ratio
    
    #now alter those for the weekends as well
    weekend_days = [6,7]
    for lv_day in weekend_days:
	    daily_load_base[lv_day-1] = weekday_base * weekend_base_weekday_base_ratio
	    daily_load_peak[lv_day-1] = weekday_base * weekend_base_weekday_base_ratio * weekend_peak_weekend_base_ratio
    
    # initialise load curve before populating
    load_week_profile_seconds = np.zeros([seconds_per_week, 1])
    #load_week_profile_seconds = squeeze(load_week_profile_seconds)
    
    
    
    #loop over weekdays
    for lv_day in range( days_per_week ):
	    #retrieve the characteristic base and peak loads for the day
	    base = daily_load_base[lv_day]
	    peak = daily_load_peak[lv_day]
	    
	    #use the generic shape function to generate the profile for today
	    day_curve = representative_daily_load(base, peak)
    
	    start_idx = seconds_per_day * (lv_day)
	    stop_idx = seconds_per_day * (lv_day+1)
	    
	    #put this daily-curve into the larger week-long curve
	    load_week_profile_seconds[start_idx : stop_idx] = day_curve
    

    #Now we will 'smooth' the curve to get rid of the sharp changes
    tmp = np.zeros([seconds_per_week,1])
    window_half_width = 7200
    
    lv=0
    acc = sum(load_week_profile_seconds[1:window_half_width]) + sum(load_week_profile_seconds[-window_half_width:])
    tmp[lv] = acc/(window_half_width*2)
    
    while lv < seconds_per_week:
	    idx1 = lv -window_half_width
	    idx2 = lv + window_half_width
	    if idx1 < 0:
		    idx1 = idx1 + seconds_per_week
        
	    if idx2 >= seconds_per_week:
		    idx2 = idx2 - seconds_per_week
        
	    acc = acc + load_week_profile_seconds[idx2] - load_week_profile_seconds[idx1]
	    tmp[lv] = acc/(window_half_width*2)
	    lv = lv + 1
    
    load_week_profile_seconds = tmp

    #normalise result to have area-under-curve = 1
    load_week_profile_seconds = load_week_profile_seconds / sum(load_week_profile_seconds)
    
    #plt.plot(load_week_profile_seconds)
    
    #now to add some noise
    fluctuation_scale = 0.01
    fluctuation_period_s = 10 #every few minutes
    num_periods = seconds_per_week / fluctuation_period_s
    num_periods = int(num_periods)
    idx=-1
    fluctuation_factor = 1.00
    for lv_pd in range(num_periods):
        tmp = np.random.uniform(low=-fluctuation_scale, high = fluctuation_scale)
        fluctuation_factor += tmp
        fluctuation_factor += (1-fluctuation_factor)*0.01
        #fluctuation_factor = min(fluctuation_factor,1.1)
        #fluctuation_factor = max(0.9,fluctuation_factor)
        for lv_s in range(fluctuation_period_s):
            idx+=1
            load_week_profile_seconds[idx] *= fluctuation_factor
    
    return load_week_profile_seconds

