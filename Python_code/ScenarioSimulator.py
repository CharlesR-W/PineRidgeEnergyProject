#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 19 11:23:57 2023

@author: crw
"""

#from RunSimulation import myPowerSystem, run_simulation
import numpy as np
import matplotlib.pyplot as plt
import scipy

from RunSimulation import mySolarPlant, myHydroPlant, myBatteryStorage, run_simulation
from LoadProfile import LoadProfile
from PowerSystem import PowerSystem

def create_load_from_sample_points(xp,yp):

    num_weekdays=5
    days_per_week = 7
    load_x=[]
    load_y=[]
    for lv in range(days_per_week):
        load_x += list( np.array(xp) + lv)
        
        load_scale = 1 if lv < num_weekdays else 0.9
        load_y += list( np.array(yp) * load_scale)
    
    #rescale so that integral(load_y) over the week = 1
    acc = 0
    for lv in range(len(load_x)-1):
        dy = ( load_y[lv] + load_y[lv+1] ) /2
        dx = load_x[lv+1] - load_x[lv]
        acc += dy * dx
    
    #seconds_per_day = 24*60*60
    #acc /= seconds_per_day
    #kWhpd_per_kWhps = 3600*24
    load_y = list(np.array(load_y) / np.mean(load_y))
    
    #plt.plot(load_x,load_y)
    
    ret = scipy.interpolate.interp1d(load_x, load_y)
    return ret

load_param_dict={
    'reservation_weekly_electricity_consumption_kWh': 72274.1696252156,
    'voltage_demanded_V': 220,
    'fluctuation_scale': 0.01,
    'fluctuation_period': 10,
    #'normalised_load_function': normalised_load_function
    }

#%% Scenario 1: WINTER
tmp_load_x = [0/24,4/24,6/24,9/24,17/24,19/24,24/24]
tmp_load_y = [110,100,110,125,115,125,110]

#create new load function
tmp = create_load_from_sample_points(tmp_load_x,tmp_load_y)
seconds_per_day = 60*60*24

normalised_load_function_s = lambda t: tmp(t / seconds_per_day)

#replace this in the dict
load_param_dict["normalised_load_function_s"] = normalised_load_function_s


myLoadProfile = LoadProfile(load_param_dict)
myPowerSystem = PowerSystem(myLoadProfile, mySolarPlant, myHydroPlant, myBatteryStorage)
myPowerSystem.restart_at_time_s(0)
dd1 = run_simulation(myPowerSystem, suptitle="Scenario 1: Winter")
#%% Scenario 2: SUMMER
tmp_load_x = [0/24,4/24,6/24,9/24, 12/24, 17/24,19/24,24/24]
tmp_load_y = [110,100,110,125, 145,155,150,110]

#create new load function
tmp = create_load_from_sample_points(tmp_load_x,tmp_load_y)
seconds_per_day = 60*60*24

normalised_load_function_s = lambda t: tmp(t / seconds_per_day) * 1.15

#replace this in the dict
load_param_dict["normalised_load_function_s"] = normalised_load_function_s


myLoadProfile = LoadProfile(load_param_dict)
myPowerSystem = PowerSystem(myLoadProfile, mySolarPlant, myHydroPlant, myBatteryStorage)
myPowerSystem.restart_at_time_s(0)

solar_start_offset = 30*6*24
mySolarPlant.input_profile.initial_row_idx = 4 + solar_start_offset

run_simulation(myPowerSystem, suptitle="Scenario 2: Summer")

#%% Scenario 3: The Third Angel sounds his trumpet, breaking the third seal; the earth is consumed by flame, and the sun is made dark to the eyes of man

tmp_load_x = [0/24,4/24,6/24,9/24, 12/24, 17/24,19/24,24/24]
tmp_load_y = [110,100,110,125, 145,155,150,110]

#create new load function
tmp = create_load_from_sample_points(tmp_load_x,tmp_load_y)
seconds_per_day = 60*60*24

normalised_load_function_s = lambda t: tmp(t / seconds_per_day) * 1.15

#replace this in the dict
load_param_dict["normalised_load_function_s"] = normalised_load_function_s


myLoadProfile = LoadProfile(load_param_dict)
myPowerSystem = PowerSystem(myLoadProfile, mySolarPlant, myHydroPlant, myBatteryStorage)
myPowerSystem.restart_at_time_s(0)

solar_start_offset = 30*6*24
mySolarPlant.input_profile.initial_row_idx = 4 + solar_start_offset
mySolarPlant.installed_capacity_Wp = 0

solar_failure_data_dict = run_simulation(myPowerSystem, suptitle = "Scenario 3: Solar-Failure (Summer)")

#%%
max_draw = min(solar_failure_data_dict["target_power_dumped_kW"])
print(f"Maximum Grid Draw kW: {abs(max_draw)}")

total_draw_kWs = sum(solar_failure_data_dict["target_power_dumped_kW"])
hours_per_second = 1/3600

total_draw_kWh = total_draw_kWs * hours_per_second
print(f"Maximum Grid Draw kW: {abs(total_draw_kWh)}")