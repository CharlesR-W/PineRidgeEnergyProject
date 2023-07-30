class SolarPlantInputProfile:
    '''
    Provides the temperature and GHI profile for solar plant operation
    '''
    def __init__(self, GHI_csv_loc):
        file = open(GHI_csv_loc)
        self.data = file.readlines()
        
        #current row of spreadsheet to read from
        self.initial_row_idx = 4
        self.current_row_idx = 4
        self.row_frequency_s = 60 * 60 #3600 s between data points
        self.current_time_s = 0
        
        self.step(time_step_s=0)
    
    def row_idx_at_time_s(self,time_s):
        tmp = self.initial_row_idx + (time_s // self.row_frequency_s)
        return int(tmp)
    
    def parse_row(self):
        
        current_row_idx = self.row_idx_at_time_s(self.current_time_s)
        
        row = self.data[current_row_idx]
        try:
            row2 = self.data[current_row_idx+1]
        except IndexError:
            row2 = row
        row = row.split(',')
        row2 = row2.split(',')
        #print(row)
        
        #indices of the table in which the data is stored
        
        GHI_idx = 6
        temperature_idx = GHI_idx-1
    
        #make sure the row we're using is for the correct time
        time_left_s = (current_row_idx - self.initial_row_idx) * self.row_frequency_s
        time_right_s = time_left_s + self.row_frequency_s
        
        #make sure something isn't behaving unexpectedly
        #assert abs(time_right_s - self.current_time_s) <= self.row_frequency_s
        
        GHI_left = float(row[GHI_idx].strip())
        try:
            GHI_right = float(row2[GHI_idx].strip())
        except IndexError:
            GHI_right = GHI_left
        secs_per_hour = 3600
        interp = (self.current_time_s - time_left_s) / (time_right_s - time_left_s)
        
        GHI_hourly_Wm2 = GHI_left*(1-interp) + GHI_right*(interp)
                    
        ambient_temperature_hourly_C = row[temperature_idx]
        ambient_temperature_hourly_C = float(ambient_temperature_hourly_C.strip())

        
        self.GHI_Wm2 = GHI_hourly_Wm2
        self.ambient_temperature_C = ambient_temperature_hourly_C

    
    def get_ambient_temperature_C(self):
        return self.ambient_temperature_C
    
    def get_GHI_Wm2(self):
        return self.GHI_Wm2
    
    def step(self, time_step_s):
        #update the time
        self.current_time_s += time_step_s
        
        #update the input data
        self.parse_row()