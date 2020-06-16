#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 13:07:21 2020

@author: annamoragne
"""

from bokeh.io import curdoc
from bokeh.layouts import row, column, gridplot
from bokeh.models import ColumnDataSource, ColorBar, LinearColorMapper, Slider, TextInput, Dropdown, MultiSelect
from bokeh.plotting import figure, show


#Heat Conduction: Q/t= kA(Thot - Tcold)/d
amb_temp=list(range(10, 30))
initial_dims=[3, 2, 1, .3]
materials=[("Brick", "Brick"), ("Cardboard", "Cardboard"), ("Aluminum", "Aluminum"), ("Concrete", "Concrete")]
#brick=0.72,  cardboard=0.048,  aluminum=205,  concrete=0.8

#Q/t for heat conduction
#dims=[length, width, height, thickness, sand_thickness]
def calc_HC (temps, dims, conductivity, desired_temp):
    k=conductivity
    Area=2*(dims[0]*dims[2])+ 2*(dims[1]*dims[2])
    Tcold=desired_temp
    d=0.1125
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
select_material=MultiSelect(title="Choice of Material for Walls of the Chamber:", value=["Brick", "Brick"], options=materials)
slide_desired_temp=Slider(title="Desired Temperature for the Inner Chamber", value=20, start=10, end=30, step=0.5)



g2=figure(title="Cost vs. Water Input", x_axis_label="Amount of Water Used per Day (in liters)", y_axis_label="Cost in $ per Year")

def cost_calc(dims, water_amount):
    #dims=[brick_length, brick_width, brick_height, sand_thickness]
    L0=dims[0] #length of inner brick chamber
    w0=dims[1] #width of inner brick chamber
    L1 = 0.1125
    L3=0.1125#thickness of brick
    L2=dims[3] #thickness of sand
    h=dims[2] #height of chamber
    w1 = w0 + 2 * L1  # width of inner brick layer
    w2 = w1 + 2 * L2  # width of sand layer
    w3 = w2 + 2 * L3  # width of outer brick layer
    A0 = L0 * w0  # area of inner chamber
    A1 = ((L0 + L1) * w1) - A0  # area of inner brick layer
    A2 = ((L0 + L1 + L2) * w2) - A1  # area of sand layer
    A3 = ((L0 + L1 + L2 + L3) * w3) - A2  # area of outer brick layer
    V0 = A0 * h  # inner chamber volume
    V1 = A1 * h  # inner brick volume
    V2 = A2 * h  # sand volume
    V3 = A3 * h  # outer brick volume
    materials_cost= 1900*0.037*V1 + 1905*.05*V2 + 1900*0.037*V3
    #cost of brick is 0.037 $/kg
    #cost of sand 0.05 $/kg
    #Density of Brick (kg/m^3): 1900
    #Density of Sand (kg/m^3): 1905
    water_list=[]
    for x in water_amount:
        water_list.append(x*0.0001*365)
    final_cost=[]
    for y in water_list:
        final_cost.append(materials_cost+y)
    return final_cost

possible_water=list(range(0, 30))
var_cost=cost_calc(initial_dims, possible_water)
source2=ColumnDataSource(data=dict(cost=var_cost, water=possible_water))
g2.line('water', 'cost', source=source2, color='green', legend_label="Yearly Cost")

def update_data(attr, old, new):
    #Get Slider Values
    length=slide_length.value
    height=slide_height.value
    width=slide_width.value
    mat=select_material.value
    thick=slide_thick.value
    want_temp=slide_desired_temp.value
    cond=0.72
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
    cost=cost_calc(dims, possible_water)
    source.data=dict(temp=amb_temp, output=out)
    source2.data=dict(cost=cost, water=possible_water)
    
updates=[select_material, slide_length, slide_height, slide_width, slide_thick, slide_desired_temp]
for u in [select_material, slide_length, slide_height, slide_width, slide_thick, slide_desired_temp]:
    u.on_change('value', update_data)
                       
widgets=column(select_material, slide_length, slide_height, slide_width, slide_thick, slide_desired_temp)


graphs=row(g1, g2)
curdoc().add_root(row(widgets, graphs))
curdoc().title="Heat Transfer and Cost for ZECC Model"


