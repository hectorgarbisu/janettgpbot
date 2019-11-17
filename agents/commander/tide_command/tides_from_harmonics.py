import time, datetime
import math
import os

_script_dir = os.path.dirname(__file__)

def get_current_args_from_file(file, current_year):
    lines = [line.split() for line in file]
    current_year_column = current_year % 10
    current_year_row = (current_year-1970)//10
    rows = [8*x+current_year_row+1 for x in range(37)]
    args = [float(lines[row][current_year_column]) for row in rows]
    return args

def get_params():
    now = datetime.datetime.now()

    # meters , degrees
    with open(os.path.join(_script_dir, "./data/casablanca-moroco_harmonics.txt")) as file:
        amps, phases = zip(*[(float(x[1]), float(x[2])) for x in
                            [line.split() for line in file]])
    # degrees / solar_hour
    with open(os.path.join(_script_dir, "./data/speeds.txt")) as file:
        speeds = [float(line.split()[1]) for line in file]

    # degrees    
    with open(os.path.join(_script_dir, "./data/equilibrium.txt")) as file:
        current_year_equilibrium_arguments = get_current_args_from_file(file, now.year)

    # factor
    with open(os.path.join(_script_dir, "./data/node_factors.txt")) as file:
        current_node_factor_arguments = get_current_args_from_file(file, now.year)

    return zip(amps, phases, speeds, current_year_equilibrium_arguments, current_node_factor_arguments)


def tide_point(t):   
    # A difference of 1 in t should correlate to 1 hour
    avg = 0.9
    params = get_params()
    return avg + sum([amplitude*node_factor*math.cos((speed*t + equilibrium_argument - phase)*math.pi/180)
                       for (amplitude, phase, speed, equilibrium_argument, node_factor) in params])

def get_last_midnight():
    yhours = datetime.datetime.utcnow().timetuple().tm_yday * 24 +2
    return yhours
    # if in summer daylight saving time, midnight was actually 1h "later" 

def get_current_day_forecast(number_of_10_minute_increments):
    # Equation uses hours from CURRENT_YEAR/01/01-00:00
    last_midnight = get_last_midnight()
    waves = [tide_point(last_midnight + t/6.) for t in range(number_of_10_minute_increments)]
    return waves

def get_now_index():
    now = datetime.datetime.now()
    now_index = int((now.hour*60 + now.minute)/10)
    return now_index

