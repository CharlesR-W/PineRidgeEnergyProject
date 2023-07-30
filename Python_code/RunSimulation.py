import numpy as np
import matplotlib.pyplot as plt
PLOT=False

from LoadProfile import LoadProfile
load_param_dict={
    'weekday_peak_base_ratio' :450/350,
    'weekend_peak_weekend_base_ratio': 410/340,
    'weekend_base_weekday_base_ratio': 1.0,
    'reservation_weekly_electricity_consumption_kWh': 72274.1696252156,
    'voltage_demanded_V': 220,
    'fluctuation_scale': 0.01,
    'fluctuation_period': 10
    }
#myLoadProfile = LoadProfile(load_param_dict)
#%% Load Profile Plotting

if PLOT:
    plt.figure()
    plt.plot(myLoadProfile.load_profile_kW_seconds)
    plt.title("Sample Weekly Load Profile")
    plt.ylabel("Demanded Power (kW)")
    plt.xlabel("Time (s)")
    #plt.legend(["Noiseless Profile","Noisy Profile"])


#%% Hydro plant creation
from HydroPlant import HydroPlant

hydro_scaleup = 1.5

hydro_param_dict = {
    'rated_capacity_kW' : 322.65*hydro_scaleup, #calculated
    'ramp_rate_percent_per_min': 10, # https://www.hydroreview.com/technology-and-equipment/hydroelectric-plants-have-fastest-start-up-time-of-u-s-electric-generators/
    'output_voltage_V' : 220, # TODO
    }
myHydroPlant = HydroPlant(hydro_param_dict)
#%% Hydro plant test curve
"""
test_time = 60*60

hydro_plant_set_point_curve = np.zeros([test_time,1])
hydro_plant_power_curve = np.zeros([test_time,1])
lv_t = 0
while lv_t < test_time:
    if lv_t < 10*60:
        tmp = 0.5
    elif lv_t < 30*60:
        tmp = 0.1
    else:
        tmp = 1.0
    
    set_point_kW = tmp * myHydroPlant.rated_capacity_kW
    hydro_plant_set_point_curve[lv_t] = set_point_kW
    
    #set the new output
    myHydroPlant.set_target_output_kW(set_point_kW)
    
    time_step_s=1
    myHydroPlant.step(time_step_s)
    plant_power_kW = myHydroPlant.get_power_kW()
    hydro_plant_power_curve[lv_t] = plant_power_kW
    
    lv_t+=1
   
if PLOT:
    plt.figure()
    plt.plot(hydro_plant_set_point_curve)
    plt.plot(hydro_plant_power_curve)
    plt.title("Hydro Plant Response Curve")
    plt.xlabel("Time (s)")
    plt.ylabel("Power (kW)")
    plt.legend(["Set Point Signal","Actual Plant Output"])
"""
#%%
from SolarPlantInputProfile import SolarPlantInputProfile
GHI_csv_loc = r"/home/crw/Programming/SIP2022/PineRidgeSolarHourlyData.csv"
mySolarPlantInputProfile = SolarPlantInputProfile(GHI_csv_loc)

solar_scaleup = 0.5

solar_param_dict = {
    "temperature_coefficient_percent_per_C": -0.36,
    "NMOT_C": 42,
    "panel_temperature_offset_C": 22.,
    "installed_capacity_Wp": 921.86*1000. * solar_scaleup,
    "num_parallel_panels_per_array":18,
    "num_series_panels_per_array":2,
    #"num_arrays":305.7593, #calculated in matlab, currently WRONG
    "rated_output_current_A": -1,
    "rated_output_voltage_V": -1,
}

from SolarPlant import SolarPlant
mySolarPlant = SolarPlant(input_profile = mySolarPlantInputProfile, param_dict = solar_param_dict)


test_time = 3600*24*7
solar_GHI_Wm2 = np.zeros([test_time,1])
solar_temperature_C = np.zeros([test_time,1])
solar_power_kW = np.zeros([test_time,1])
lv_t = 0
dt=1

t0 = 30*3.5*24*3600

mySolarPlant.step(t0)

while lv_t < test_time:    
    
    solar_GHI_Wm2[lv_t] = mySolarPlantInputProfile.get_GHI_Wm2()
    solar_temperature_C[lv_t] = mySolarPlantInputProfile.get_ambient_temperature_C()
    solar_power_kW[lv_t] = mySolarPlant.get_power_kW()
    
    lv_t+=dt
    mySolarPlant.step(dt)
    
if PLOT:
    plt.figure()
    fig,ax = plt.subplots(nrows=3,ncols=1)

    ax[0].set_title("Weekly Solar Data")
    
    ax[0].plot(solar_GHI_Wm2)
    ax[0].set_ylabel("GHI (W/m2)")
    ax[0].set_xticks([])
    
    ax[1].plot(solar_temperature_C)
    ax[1].set_ylabel("Temperature (C)")
    ax[1].set_xticks([])
    
    ax[2].plot(solar_power_kW)
    ax[2].set_ylabel("Power (kW)")
    ax[2].set_xlabel("Time (s)")


#%%
battery_scaleup=1.0
battery_param_dict = {
    "charge_efficiency_percent" : np.sqrt(0.90)*100,
    "discharge_efficiency_percent" : np.sqrt(0.90)*100, #https://researchinterfaces.com/lithium-ion-batteries-grid-energy-storage/
    #"usable_energy_capacity_percent":96.4,
    "usable_energy_capacity_kWh":1032.5*battery_scaleup, #USABLE energy
    'max_charge_rate_unsigned_kW': 540.83*battery_scaleup,
    'max_discharge_rate_unsigned_kW':540.83*battery_scaleup,
    }

from BatteryStorage import BatteryStorage
myBatteryStorage = BatteryStorage(battery_param_dict)

#%%
from PowerSystem import PowerSystem
#myPowerSystem = PowerSystem(myLoadProfile, mySolarPlant, myHydroPlant, myBatteryStorage)


def run_simulation(myPowerSystem,suptitle):
    myPowerSystem.restart_at_time_s(0)
    time_step_s = 1
    test_time_final_s = 3600*24*7
    time_now_s = 0
    while time_now_s < test_time_final_s:
        myPowerSystem.step(time_step_s)
        time_now_s += time_step_s
        if time_now_s % 3600 == 0:
            print(time_now_s // 3600)
            
    vars_to_plot = ["load_power_kW","solar_power_kW","hydro_power_kW", "battery_SoC", "target_power_dumped_kW"]
    data_dict = myPowerSystem.data_arrs_dict
    y_arr = [data_dict[v] for v in vars_to_plot]
    y_titles = vars_to_plot

    plot_multiple(y_arr,y_titles,suptitle)
    return data_dict
#%%
def plot_multiple(y_arr,y_titles,suptitle):
    plt.figure()
    nrows=len(y_arr)
    scale= len(y_arr)*2
    fig,ax = plt.subplots(nrows=nrows,ncols=1, sharex=True, figsize=(scale, scale),constrained_layout=True)
    
    seconds_per_day = 3600*24
    days_per_week = 7
    xtick_values = [seconds_per_day*n for n in range(0,days_per_week+1)]
    xtick_labels = [n for n in range(0,days_per_week+1)]
    
    for lv in range(len(y_arr)):
        ax[lv].plot(y_arr[lv])
        ax[lv].set_title(y_titles[lv].replace("_"," "))
        ax[lv].set_xticks(ticks=xtick_values, labels=xtick_labels)
        #ax[lv].grid()
    fig.supxlabel("Time (days)")
    fig.suptitle(suptitle)

    
    

