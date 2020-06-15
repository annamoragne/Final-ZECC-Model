#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 13:07:21 2020

@author: annamoragne
"""

from bokeh.io import curdoc
from bokeh.layouts import row, column, gridplot
from bokeh.models import ColumnDataSource, ColorBar, LinearColorMapper, Slider, TextInput, Dropdown
from bokeh.plotting import figure, show


#Heat Conduction: Q/t= kA(Thot - Tcold)/d
amb_temp=list(range(10, 30))
initial_dims=[3, 2, 1, .1125]
materials=[("Brick", 'Brick'), ("Cardboard", 'Cardboard'), ("Aluminum", 'Aluminum'), ("Concrete", 'Concrete')]
#brick=0.72,  cardboard=0.048,  aluminum=205,  concrete=0.8

#Q/t for heat conduction
#dims=[length, width, height, thickness]
def calc_HC (temps, dims, conductivity, desired_temp):
    k=conductivity
    Area=2*(dims[0]*dims[2])+ 2*(dims[1]*dims[2])
    Tcold=desired_temp
    d=dims[3]
    new_list=[]
    for i in temps:
        new_list.append((k*Area)*(i-Tcold)/d)
    return new_list


k_sand = 0.27  # thermal conductivity of dry sand W/mK
k_water = 0.6  # thermal conductivity of water W/mK
k_brick = 0.72  # thermal conductivity of brick W/mK
e_sand = 0.343  # porosity of sand

out1=calc_HC(amb_temp, initial_dims, k_brick, 20)
source=ColumnDataSource(data=dict(temp=amb_temp, output=out1))

g1=figure(title="Heat Conduction and Evaporative Cooling Varying with Outside Temperature", x_axis_label="Ambient Temperature (in Celsius)", y_axis_label="Heat per Time")
g1.line('temp', 'output', source=source, color="purple", legend_label="Heat Conduction")

slide_length=Slider(title="Length of Chamber", value=initial_dims[0], start=0, end=12, step=0.5)
slide_width=Slider(title="Width of Chamber", value=initial_dims[1], start=0, end=12, step=0.5)
slide_height=Slider(title="Height of Chamber", value=initial_dims[2], start=0, end=5, step=0.25)
slide_thick=Slider(title="Thickness of Chamber Wall", value=initial_dims[3], start=0, end=1, step=0.001)
drop_mat=Dropdown(label="Material for Walls of Chamber", button_type='primary', menu=materials)
slide_desired_temp=Slider(title="Desired Temperature for the Inner Chamber", value=20, start=10, end=30, step=0.5)

def update_data(attr, old, new):
    #Get Slider Values
    length=slide_length.value
    height=slide_height.value
    width=slide_width.value
    mat=drop_mat.value
    thick=slide_thick.value
    want_temp=slide_desired_temp.value
    cond=0 
    
    if mat =="Brick":
        cond=0.72
    elif mat=="Cardboard":
        cond=0.048 
    elif mat=='Aluminum':
        cond=205 
    elif mat=='Concrete':
        cond=0.8
    dims=[length, width, height, thick]
    out=calc_HC(amb_temp, dims, cond, want_temp)
    source.data=dict(temp=amb_temp, output=out)
    
updates=[drop_mat, slide_length, slide_height, slide_width, slide_thick, slide_desired_temp]
for u in [drop_mat, slide_length, slide_height, slide_width, slide_thick, slide_desired_temp]:
    u.on_change('value', update_data)
                       
widgets=column(drop_mat, slide_length, slide_height, slide_width, slide_thick, slide_desired_temp)

show(row(widgets, g1))