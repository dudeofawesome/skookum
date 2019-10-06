#!/usr/bin/env python3

# Attribution: /u/jiggly_wigglers_69
# https://www.reddit.com/r/klippers/comments/dczd7y/i_cobbled_together_a_very_customizable_pressure/

# Use this script at your own risk
# This script is designed for klipper, but can probably be easily modified for
# other firmwares. This script generates gcode for a square that has features
# and speed changes to help calibrate pressure advance values. This script does
# not include any commands for a heated bed, but they can be added easily, just
# add the `print('M140 S(bed_temp_goes_here)')` and
# `print('M190 S(bed_temp_goes_here)')` commands to the start of the code on
# seperate lines.

# To use this script on windows, download and install python,  use control panel
# to navigate to "Control Panel\System and Security\System", click
# "advanced system settings", in the new window, find and click on
# "enviromental variables", under "system variables" click on "path", click
# "edit", click "new", paste in your file path to your python installation
# (eg: "C:\Users\your_username\AppData\Local\Programs\Python\Python37-32")
# click "ok." After you have modified the parameters in this script to your
# liking and saved your changes, open command prompt, navigate to the directory
# where this script is saved on your drive using a cd command, type in
# "python pressure_advance_tune.py > PAtestsquare.gcode", this will output a
# gcode file in the same directory, happy printing!

# It's a good idea to preview your gcode in a slicer before attempting to print.
# This script assumes your (0,0) coordinate is the corner of a square bed.

# After printing, use calipers to find the z height where your print looks best
# and most consistant all around. Use this z height to calculate your best
# pressure advance value (your measured z height should be a multiple of your
# layer height).
# Your best pressure advance value=((measured_z_height/layer_height)-2)*((PA_max/PA_min)/(number_of_layers))
# Add this calculated value to your firmware config or into your start gcode if
# you have that set up for different materials.

# Modify these following parameters to match your printer and desired settings.
# Units are mm, mm/s, degrees Celcius. Just standard stuff.
bed_x_length=220
bed_y_length=220
nozzle_diameter=0.4 
layer_height=0.3 
filament_diameter=1.75 
nozzle_temp=190
bed_temp=60
travel_speed=150
slow_print_speed=15
fast_print_speed=120
first_layer_speed=20
cooling_fan_speed=51 # PWM value 0 to 255
# Make sure a square with this side length fits in the center of your print bed
rectangle_side_length=50
# Number of layers (this does not include the initial layer or the two finishing
# layers) total z height will be: (layer_height*layers+(3*layer_height))
layers=60
PA_min=0.00 # Minimum pressure advance value
PA_max=1.00 # Maximum pressure advance value
# End of parameter set

print('M140 S%.3f' % bed_temp)
print('M190 S%.3f' % bed_temp)

print('M104 S%.3f' % nozzle_temp)
print('M109 S%.3f' % nozzle_temp)

# Start gcode goes here. this start code is pretty standard, it includes a
# prime strip. Only modify if you know what you're doing
print('''
M220 S100 ;Reset Feedrate
M221 S100 ;Reset Flowrate
G28 ;Home
G92 E0 ;Reset Extruder
G1 Z2.0 F3000 ;Move Z Axis up
G1 X10.1 Y20 Z0.28 F5000.0 ;Start priming wipe
G1 X10.1 Y200.0 Z0.28 F1500.0 E15
G1 X10.4 Y200.0 Z0.28 F5000.0
G1 X10.4 Y20 Z0.28 F1500.0 E30 ;Finish priming wipe
G92 E0 ;Reset Extruder
G1 Z2.0 F3000 ;Move Z Axis up
SET_VELOCITY_LIMIT SQUARE_CORNER_VELOCITY=1 ACCEL=500
SET_PRESSURE_ADVANCE ADVANCE_LOOKAHEAD_TIME=0
''')
# end of start gcode

# enable absolute extrusion mode
print('''
M82
G92 E0
''')

from math import *

# The following two functions control extrusion
def extrusion_volume_to_length(volume):
    return volume / (filament_diameter * filament_diameter * 3.14159 * 0.25)

def extrusion_for_length(length):
    return extrusion_volume_to_length(length * nozzle_diameter * layer_height)

# These values are used to keep track of current xyz coordinates and extruded
# length
current_x=((bed_x_length / 2)-(rectangle_side_length / 2))
current_y=((bed_y_length / 2)-(rectangle_side_length / 2))
current_z=layer_height
current_e=0

# Move the printhead to the starting position and prime nozzle
print('G1 X%.3f Y%.3f Z%.3f E1.0 F%.0f' % (current_x, current_y, current_z, travel_speed * 60))

# Moves the z axis up
def move_up():
  global current_z
  current_z += layer_height
  print('G1 Z%.3f' % current_z)

# Generates the gcode for a line segment using an x length, y length, and speed
def line(x,y,speed):
  length = sqrt(x**2 + y**2)
  global current_x, current_y, current_e
  current_x += x
  current_y += y
  current_e += extrusion_for_length(length)
  print('G1 X%.3f Y%.3f E%.4f F%.0f' % (current_x, current_y, current_e, speed * 60))

def draw_rect(speed_fast, speed_slow):
  line(rectangle_side_length, 0, speed_fast)
  line(0, rectangle_side_length / 2, speed_fast)
  line(0, rectangle_side_length / 2, speed_slow)
  line(-rectangle_side_length, 0, speed_fast)
  line(0, -rectangle_side_length, speed_slow)
  move_up()

# Print first layer without cooling fan and without pressure advance at 20mm/s
# for better adhesion
pressure_advance=0
print('SET_PRESSURE_ADVANCE ADVANCE=%.4f' % pressure_advance)
draw_rect(first_layer_speed, first_layer_speed)

# Start cooling fan      
print("M106 S%.3f" % cooling_fan_speed)

# Generates the gcode for the rectangle 
for i in range(layers):
  pressure_advance = (i / layers) * (PA_max-PA_min) + PA_min;
  print('SET_PRESSURE_ADVANCE ADVANCE=%.4f' % pressure_advance)
  draw_rect(fast_print_speed, slow_print_speed)

# Print two finishing layers at PA_MAX
pressure_advance = PA_max
print('SET_PRESSURE_ADVANCE ADVANCE=%.4f' % pressure_advance)
draw_rect(fast_print_speed, slow_print_speed)
draw_rect(fast_print_speed, slow_print_speed)

# Ending gcode goes here
# (just moves the nozzzle up a bit and turns everything off)
print('''
G91
G1 Z10 F450
G90
M106 S0
M104 S0
M140 S0
M84
''')
