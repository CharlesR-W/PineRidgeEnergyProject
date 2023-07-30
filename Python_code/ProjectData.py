
## Relevant data and sources
#News article describing shortages in Oglala Lakota county
#https://www.theguardian.com/environment/2020/aug/12/native-americans-energy-inequality-electricity

#South Dakota energy review:
#https://www.eia.gov/state/analysis.php?sid=SD

reservation_population = 28787
#https://en.wikipedia.org/wiki/Pine_Ridge_Indian_Reservation
#End of second paragraph

SD_total_annual_energy_percapita_MBTU = 447
#https://www.eia.gov/state/rankings/?sid=SD#/series/12

kWh_per_MBTU = 0.29307
SD_total_annual_energy_percapita_kWh = SD_total_annual_energy_percapita_MBTU * kWh_per_MBTU

fraction_of_energy_as_electricity = 1.0
#assumed since main other sources are fossil fuel, which we want to
#replace

SD_annual_electricity_percapita_kWh = SD_total_annual_energy_percapita_kWh * fraction_of_energy_as_electricity

SD_total_energy_expenditures_percapita_USD = 4187
#https://www.eia.gov/state/rankings/?sid=SD#/series/225

SD_CO2_emissions_MMT = 16
#https://www.eia.gov/state/rankings/?sid=SD#/series/226

#How much energy must be produced annually in kWh for the reservation
reservation_annual_electricity_requirement_kWh = reservation_population * SD_annual_electricity_percapita_kWh
days_per_year = 365.25
reservation_daily_electricity_requirement_kWh  = reservation_annual_electricity_requirement_kWh / days_per_year

## Sizing of the solar array system
#cost and model data:
#https://www.solarreviews.com/solar-panel-cost/south-dakota#brand
#re: parallel vs series connection of panels
#https://www.literoflightusa.org/solar-panels-in-series-vs-parallel-advantages-and-disadvantages/
#US DoE on community Solar
#https://www.energy.gov/eere/solar/community-solar-basics

hours_per_day =24
#print(f"Reservation's average daily electricity consumption: #.2f kWh/day, #.2f kW \n", reservation_daily_electricity_requirement_kWh, reservation_daily_electricity_requirement_kWh/hours_per_day)

#reservation_avg_GHI_kWh_m2_day = 3.5
# https://nsrdb.nrel.gov/data-viewer
# "Equivalent sun hours" - this accounts for the difference in intensity
# above in a more straightforward way
reservation_ESH = 4
#CHECK

#include tilt-angle factor to account for the fact that we do not use
#sun-trackers.  Assume panels always set to Winter angle see source.
tilt_angle_factor = 0.7
#Tilt angle data (reservation is at 43degrees North latitude):
#https://www.solarpaneltilt.com/

#If we were to use solar ONLY to power the community
required_solar_rated_kWp = reservation_daily_electricity_requirement_kWh / reservation_ESH / tilt_angle_factor
print(f"Installed rated solar capacity:\t#.2f kWp\n", required_solar_rated_kWp)

'''
#create the solar profile for the weeklong simulink test
[GHI_week_profile_Wm2_seconds, GHI_annual_hourly_Wm2] = solar_irradiance_data_reader()
#plot GHI profile
GHI_fig = figure
hold on
plot(GHI_week_profile_Wm2_seconds,'LineWidth',5)
title("Solar Irradiance Over a Sample Week")
xlabel("Time (s)")
ylabel("Solar Irradiance (W/m^2)")
fontsize(GHI_fig,fig_font_size,"points")
saveas(GHI_fig,"GHI_plot.jpg",'png')
hold off
'''
# Now determine the number of panels we need
#selected panel with spec sheet:
#https://www.solarreviews.com/manufacturers/lg-solar/solar-panels/lgsol51617lgneon2lg335n1kv5
selected_module_Wp = 335
selected_module_Vmpp_V = 34.1
selected_module_Impp_A = 9.83
price_per_panel_USD = 320
#MPPT tracker
# https://www.solarpanelstore.com/collections/large-charge-controllers/products/midnite-classic-150
MPPT_Vmax_V = 100
MPPT_Imax_A = 180

max_panel_series = floor(MPPT_Vmax_V / selected_module_Vmpp_V)
max_panel_parallel = floor(MPPT_Imax_A / selected_module_Impp_A)

panels_per_array = max_panel_parallel*max_panel_series
power_per_array_Wp = panels_per_array*selected_module_Wp
W_per_kW = 1000
num_arrays_required = required_solar_rated_kWp * W_per_kW / power_per_array_Wp
num_panels_required = num_arrays_required * max_panel_series * max_panel_parallel

num_panels_required = ceil(num_panels_required)
total_panel_cost_USD = num_panels_required * price_per_panel_USD

num_MPPTs_required = ceil(num_arrays_required)
price_per_MPPT = 700
total_MPPT_cost_USD = price_per_MPPT * num_MPPTs_required

print(f"This corresponds to #.2f installed panels and #.2f MPPTs\n",num_panels_required,num_MPPTs_required)
print(f"Each array has #.2f panels in series by #.2f in parallel\n",max_panel_series,max_panel_parallel)
#Selected battery data for TeslaPowerPack
#https://en.wikipedia.org/wiki/Tesla_Powerpack#Powerpack_specifications
#idk where wikipedia got that table from since it seems not to be cited
single_battery_discharge_capacity_kW = 55
single_battery_usable_energy_kWh = 210
single_battery_VDC_max_V = 960
single_battery_IDC_max_A = 66
price_per_battery_USD = 172000
#NB that this battery seems to be pretty proprietary so I'm just going to
#assume that whatever magic is happening inside, I can charge it with my
#solar DC

## Specification and creation of the weekly load profile
#Data about load-curves over a week
#https://www.eia.gov/todayinenergy/detail.php?id=42915

# parameters for load generator - taken from website above for April
# (low solar-power month)
weekday_base = 1.0
weekday_peak_base_ratio = 450/350
weekend_peak_weekend_base_ratio = 410/340
weekend_base_weekday_base_ratio = 1.0

load_week_profile_unitless_seconds = load_data_generator(weekday_peak_base_ratio, weekend_base_weekday_base_ratio, weekend_peak_weekend_base_ratio)
#returns a load_profile scaled so that its SUM is 1.0 - must be scaled

weeks_per_year = 365.25 / 7
reservation_weekly_electricity_consumption_kWh = SD_annual_electricity_percapita_kWh / weeks_per_year * reservation_population

seconds_per_hour = 3600
#scale the profile to match weekly consumption
load_week_profile_kWhps_seconds = load_week_profile_unitless_seconds *reservation_weekly_electricity_consumption_kWh
#now convert units to from kWh/s to kW
load_week_profile_kW_seconds = load_week_profile_kWhps_seconds * seconds_per_hour

seconds_per_year = 365.25*24*3600
#just check that I'm doing things roughly right
test_val = mean(load_week_profile_kW_seconds)*(seconds_per_year/seconds_per_hour) / reservation_annual_electricity_requirement_kWh
#print(f"Load profile avg vs reservation annual consumptions (should be ~1.0 if I'm not screwing up): #.2f\n",test_val)
'''
Load_fig = figure
hold on
plot(load_week_profile_kW_seconds,'LineWidth',5)
xlabel("Time (s)")
ylabel("Consumption (kWh/s)")
title("Representative weekly load")
fontsize(Load_fig,fig_font_size,"points")
saveas(Load_fig,"Load_plot.jpg",'png')
hold off
'''

print(f"\nReservation's average daily electricity consumption: #.2f kWh/day, #.2f kW \n", reservation_daily_electricity_requirement_kWh, reservation_daily_electricity_requirement_kWh/hours_per_day)
print(f"Peak electricity consumption \t#.2f kW\n",max(load_week_profile_kW_seconds))
## Hydropower generation profile
#Size the amount of hydropower for now based on its rated capacity vs. the
#primary

#For sizing purposes, we assume the turbines have a capacity factor
hydropower_capacity_factor = 0.8
fraction_of_consumption_met_by_secondary = 0.5
hours_per_year = 365.25 * 24
hydropower_rated_kW = reservation_annual_electricity_requirement_kWh / hours_per_year / hydropower_capacity_factor * fraction_of_consumption_met_by_secondary

#estimate flow rate
hydropower_efficiency = 0.8
hydropower_head_m = 1
rho=1000
g=9.81
hydropower_flowrate_m3s = hydropower_rated_kW * W_per_kW / (rho * g * hydropower_head_m)
#
hydropower_cost_per_kW_USD = 340e6 / 786e3 #from the Oahe dam
total_hydropower_cost_USD = hydropower_cost_per_kW_USD * hydropower_rated_kW

print(f"\nInstalled hydro capacity to meet #.2f percent of average consumption: #.2f kW\n",fraction_of_consumption_met_by_secondary*100, hydropower_rated_kW)
print(f"Estimated flowrate required:\t#.2f m3/s", hydropower_flowrate_m3s)
## Battery sizing
#We size the battery for two separate objectives - overnight storage and
#days-of-autonomy

#N.B. All of this is rough, but need only be right on average, as the
#community is still connected to the grid - especially if this means lower
#investment costs

nighttime_consumption_kW = min(load_week_profile_kW_seconds)
nighttime_generation_deficit_kW = nighttime_consumption_kW - hydropower_rated_kW
#as a rough estimate, say night is ~7 hours
night_length_hours = 7

#by how much do we want to overshoot?
#since we are connected to grid still, no need for extra
safety_factor_daily = 1.0

#For the purpose of having enough power overnight, how big batteries do we
#need?
battery_daily_capacity_kWh = night_length_hours * nighttime_generation_deficit_kW
battery_daily_discharge_kW = nighttime_generation_deficit_kW

#assuming that the kWh is what is required, not the kW capacity
#I do NOT take the ceil of this number, since these batteries are bespoke
#and I'm sure can be divided into smaller ones with no problem.
num_batteries_required_daily = battery_daily_capacity_kWh / single_battery_usable_energy_kWh
total_battery_cost_daily_USD = num_batteries_required_daily*price_per_battery_USD

# In the absence of grid-connection, how long should the system last?
#days_of_autonomy = 3.0

#redo the calculations for this big-boi battery pack
#battery_autonomy_capacity_kWh = reservation_daily_electricity_requirement_kWh * days_of_autonomy
#peak_consumption_kW = max(load_week_profile_kW_seconds)
#battery_autonomy_discharge_kW = peak_consumption_kW - hydropower_rated_kW
#num_batteries_required_autonomy = battery_autonomy_capacity_kWh / single_battery_usable_energy_kWh
#total_battery_cost_autonomy_USD = num_batteries_required_autonomy * price_per_battery_USD

print(f"\nFor overnight autonomy, battery-size:\nBattery Energy Capacity\t#.2f kWh\nBattery Discharge\t#.2f kWh\n",battery_daily_capacity_kWh,battery_daily_discharge_kW)
print(f"This corresponds to #.2f batteries\n", num_batteries_required_daily)
#print(f"\nFor #.1f days of autonomy from the grid, battery-size:\nBattery Energy Capacity #.2f kWh\nBattery Discharge #.2f kWh\n",days_of_autonomy,battery_autonomy_capacity_kWh,battery_autonomy_discharge_kW)

## Print cost breakdown
total_cost_USD = total_panel_cost_USD + total_hydropower_cost_USD + total_battery_cost_daily_USD + total_MPPT_cost_USD
print(f"\nCost Breakdown:\n\tCost\tItem\tPercentage of Budget\n")
print(f"\t#.2f$ Panel cost\t#.2f\n",total_panel_cost_USD,total_panel_cost_USD/total_cost_USD*100)
print(f"\t#.2f$   Hydropower cost\t#.2f\n",total_hydropower_cost_USD,total_hydropower_cost_USD/total_cost_USD*100)
print(f"\t#.2f$   MPPT cost\t#.2f\n",total_MPPT_cost_USD,total_MPPT_cost_USD/total_cost_USD*100)
print(f"\t#.2f$   Battery cost\t#.2f\n",total_battery_cost_daily_USD,total_battery_cost_daily_USD/total_cost_USD*100)