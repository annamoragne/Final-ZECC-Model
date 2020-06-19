#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 15 13:07:21 2020

@author: annamoragne
"""

from bokeh.io import curdoc
from bokeh.layouts import row, column, gridplot
from bokeh.models import ColumnDataSource, ColorBar, LinearColorMapper, Slider, TextInput, Dropdown, Select, Paragraph
from bokeh.plotting import figure, show
import numpy as np
from scipy.interpolate import interp1d


#Heat Conduction: Q/t= kA(Thot - Tcold)/d
amb_temp=list(range(10, 30))
time_range=list(range(0,24))
initial_dims=[3, 2, 1, .3]
rh1=0.5
materials=["Brick", "Cardboard", "Aluminum", "Concrete"]
loc_and_time=["Bethlehem in June", "Bethlehem in January", "San Fransisco in June", "San Fransisco in January", "Florida in June", "Florida in January"]
#brick=0.72,  cardboard=0.048,  aluminum=205,  concrete=0.8
beth_hourly1=[66, 65, 64, 64, 64, 64, 64, 65, 66, 67, 70, 71, 73, 73, 72, 75, 76, 76, 76, 75, 75, 73, 71, 70] #hourly bethlhem temperatures for June 18, 2020
beth_hourly1_C=[]
for i in beth_hourly1:
    beth_hourly1_C.append((i-32)*(5/9))

#Q/t for heat conduction
#dims=[length, width, height, sand_thickness]
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

out1=calc_HC(beth_hourly1_C, initial_dims, k_brick, 20)
source=ColumnDataSource(data=dict(time=time_range, output=out1))
TOOLS = "crosshair,pan,undo,redo,reset,save,wheel_zoom,box_zoom, tap"

g1=figure(title="Heat per Time", x_axis_label="Time (hours in the day, starting at 12am)", y_axis_label="Heat per Time", tools=TOOLS)
g1.line('time', 'output', source=source, color="purple", legend_label="Heat Conduction", line_dash=[4,4], line_width=3)
g1.legend.click_policy="hide"

slide_length=Slider(title="Length of Chamber", value=initial_dims[0], start=0, end=12, step=0.5)
slide_width=Slider(title="Width of Chamber", value=initial_dims[1], start=0, end=12, step=0.5)
slide_height=Slider(title="Height of Chamber", value=initial_dims[2], start=0, end=5, step=0.25)
slide_thick=Slider(title="Thickness of Sand Layer in Chamber Wall", value=initial_dims[3], start=0, end=1, step=0.001)
select_material=Select(title="Choice of Material for Walls of the Chamber:", value="Brick", options=materials)
slide_desired_temp=Slider(title="Desired Temperature for the Inner Chamber", value=20, start=2, end=50, step=0.5)
location=Select(title="Location and Time of Year", value="Bethlehem in June", options=loc_and_time)



def latent_heat(temp):
    #xnew = np.linspace(0,90, endpoint= True)
    y = [45054, 44883,44627,44456,44200,43988,43774,43602,43345,43172,42911,42738,42475,42030,41579,41120] #latent heat of vaporization array
    x = [0,5,10,15,20,25,30,35,40,45,50,55,60,70,80,90] #water temperature array
    f1 = interp1d(x, y, kind= 'cubic')
    return f1(temp)

#Evaporative Cooling Rate Q/t=mLv/t
latent_out=latent_heat(beth_hourly1)
def evap_cool(mass, latent, time):
    cooling_rate=[]
    for w in range(0,24):
        cooling_rate.append((mass*latent[w]/(time[w]+1))/100)
    return cooling_rate

evap_out=evap_cool(4, latent_out, time_range)   
#print(evap_out[0], evap_out[12])                         
source3=ColumnDataSource(data=dict(time=time_range, evap_out=evap_out))
g1.line('time', 'evap_out', source=source3, color='orange', legend_label="Evaporation Cooling Rate", line_width=3)

#gh=theta(SA)(Xs-X)
def water_needed(dims, temp, rh, SVP):
    theta=1079*0.62198
    SA=2*(dims[0]+dims[3]+.225)*dims[2] + 2*dims[2]*(dims[1]+dims[3]+.225)
    A = 18.3036
    B = 3816.44
    C = -46.13
    p_star=np.exp(A - B / (C + temp + 273))  # Antoine equation for vapor pressure at outside air
    p_air=rh*p_star # bulk pressure of air at t bulk -- modified by SR - using rh instead of a constant value.
    evap_rate=theta*(SVP-p_air)*SA*(18/1000) # in L/sec
    return evap_rate
    
print(latent_heat(18))
#g2=figure(title="Cost of Chamber for Different Materials and Varrying Daily Water Input Levels", x_axis_label="Amount of Water Used per Day (in liters)", y_axis_label="Cost in $ per Year")

def cost_calc(dims, water_amount, mat):
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
    materials_cost=0
    if mat=="Brick":
       materials_cost= 1900*0.037*V1 + 1905*.05*V2 + 1900*0.037*V3
       #Brick cost 0.037 $/Kg and density is 1900 Kg/m^3
    elif mat=="Cardboard":
        materials_cost=1905*0.5*V2 + (V1+V2)*(0.11*689)
        #Cardboard cost $0.11/Kg and desnsity is 689 Kg/m^3
    elif mat=="Aluminum":
        materials_cost=1905*0.5*V2 + (V1+V2)*(1.754*2710)
        #Aluminum cost is $1.754/Kg and density is 2710 Kg/m^3
    elif mat=="Concrete":
        materials_cost==1905*0.5*V2 + (V1+V2)*(98.425)
        #Concrete cost is $98.425/m^3
    #cost of sand 0.05 $/kg
    #Density of Sand (kg/m^3): 1905
    water_cost=water_amount*0.0001*365
    final_cost=materials_cost+water_cost
    return final_cost

price1=cost_calc(initial_dims, 35, "Brick")
sourceP=ColumnDataSource(data=dict(price=[price1]))
#source2=ColumnDataSource(data=dict(brick=cost_brick, concrete=cost_conc, aluminum=cost_alum, cardboard=cost_cardboard, water=possible_water))
#g2.line('water', 'brick', source=source2, color='darkorange', legend_label="Brick")
#g2.line('water', 'aluminum', source=source2, color="darkblue", legend_label="Aluminum")
#g2.line('water', 'cardboard', source=source2, color='brown', legend_label="Cardboard")
#g2.line('water', 'concrete', source=source2, color='teal', legend_label="Concrete")

def update_data(attr, old, new):
    #Get Slider Values
    length=slide_length.value
    height=slide_height.value
    width=slide_width.value
    mat=select_material.value
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
    out=calc_HC(beth_hourly1_C, dims, cond, want_temp)
    price=cost_calc(dims, 35, mat)
    source.data=dict(time=time_range, output=out)
    sourceP.data=dict(price=price)
   # source2=ColumnDataSource(data=dict(brick=cost_B, concrete=cost_Conc, aluminum=cost_Al, cardboard=cost_Card, water=possible_water))

updates=[select_material, slide_length, slide_height, slide_width, slide_thick, slide_desired_temp]
for u in [select_material, slide_length, slide_height, slide_width, slide_thick, slide_desired_temp]:
    u.on_change('value', update_data)

priceP=sourceP.data['price']
#trial2="The amount of water needed per day is "+str(round(first_water, 2))+" liters"
#print(priceP[0])
trial_text="The yearly cost of the cooling chamber you have created is: $" + str(round(priceP[0], 2))
chamber_price=Paragraph(text=trial_text)
#waterL=Paragraph(text=trial2)

                       
widgets=column(location, select_material, slide_length, slide_height, slide_width, slide_thick, slide_desired_temp, chamber_price)


curdoc().add_root(row(widgets, g1))
curdoc().title="Heat Transfer and Cost for ZECC Model"


