#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 14:12:56 2020

@author: annamoragne
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 22 13:42:45 2020

@author: annamoragne
"""

from bokeh.io import curdoc
from bokeh.layouts import row, column, gridplot
from bokeh.models import ColumnDataSource, ColorBar, LinearColorMapper, Slider, TextInput, Dropdown, Select, Paragraph, TableColumn, DataTable
from bokeh.plotting import figure, show
import numpy as np
from scipy.interpolate import interp1d

time_range=list(range(0, 24))
time_range1=list(range(1,13))
initial_dims=[3, 2, 1, .3]
# [length, width, height, sand_thickness]
rh1=0.5 #needs to be updates to be based on each weather data set
materials=["Brick", "Cardboard", "Aluminum", "Concrete"]
loc_and_time=["Bethlehem, PA", "Miami, Fl", "Puerta Jimenez, Costa Rica", "Quito, Ecuador", "Nairobi, Kenya", "Lusaka, Zambia"]


#defining lists for temperatures
beth_hourly1=[66, 65, 64, 64, 64, 64, 64, 65, 66, 67, 70, 71, 73, 73, 72, 75, 76, 76, 76, 75, 75, 73, 71, 70] #hourly bethlhem temperatures for June 18, 2020
beth_yearly_F=[27.5, 31, 39, 50, 60, 69, 73.5, 71.5, 64, 52.5, 43, 32.5]
CostaRica_C=[26.2, 26.5, 27.7, 28, 27.3, 26.5, 26.7, 26.3, 26, 25.9, 25.6, 25.7]
miami_F=[68, 70, 72.5, 75.5, 80, 82.5, 84, 84, 82.5, 80, 75, 70.5]
Ecuador_C=[15.5, 15.55, 15.45, 15.55, 15.55, 15.5, 15.45, 15.9, 15.85, 15.65, 15.45, 15.5]
Kenya_C=[19.7, 20.2, 20.7, 20.2, 19.1, 17.8, 16.7, 17.2, 18.6, 19.8, 19.3, 19.2]
Zambia_C=[22.5, 22.4, 21.95, 20.55, 18.25, 15.8, 15.6, 17.85, 21.6, 23.95, 23.9, 22.75]


def FtoC(Ftemps):
    newTemps=[]
    for x in Ftemps:
        n=(x-32)*(5/9)
        newTemps.append(n)
    return newTemps

beth_yearly_C=FtoC(beth_yearly_F)
Miami_C=FtoC(miami_F)

class Weather:
    def __init__(self, temps_list, name, rh):
        self.location=name
        self.temps=temps_list
        self.rh=rh
 
beth_yearly=Weather(beth_yearly_C, "Bethlehem, PA", .5)
CostaRica=Weather(CostaRica_C, "Puerta Jimenez, Costa Rica", .9)
Miami=Weather(Miami_C, "Miami, FL", .6)
Ecuador=Weather(Ecuador_C, "Quito, Ecuador", .4)
Kenya=Weather(Kenya_C, "Nairobi, Kenya", .3)
Zambia=Weather(Zambia_C, "Lusaka, Zambia", .7)
beth_hourly1_C=Weather(FtoC(beth_hourly1), "Bethlehem, PA (one day in june)", 0.64)

colors=['CadetBlue', 'Coral', 'DarkOliveGreen', 'DarkRed', 'DarkSlateBlue', 'Peru']
weather_sets=[beth_yearly, CostaRica, Miami, Ecuador, Kenya, Zambia]

TOOLS = "crosshair,pan,undo,redo,reset,save,wheel_zoom,box_zoom, tap"
diff_temps=figure(title="Average Temperature Throughout the Year", x_axis_label="Months", y_axis_label="Temperature in Celsius", tools=TOOLS)
diff_temps.title.text_font_size='15pt'
diff_temps.xaxis.ticker = list(range(1, 13))
diff_temps.xaxis.major_label_overrides={1:'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 
                                        7: "July", 8:'August', 9:'September', 10: 'October', 11: 'November', 12: 'December'}
diff_temps.xaxis.major_label_orientation=1
#diff_temps.line(time_range, beth_hourly1_C.temps, legend_label="Bethlehem, PA in June", line_width=3, color='red')
for t in range(0, 6):
    here=weather_sets[t]
    diff_temps.line(time_range1, here.temps, legend_label=here.location, line_width=2, color=colors[t])
diff_temps.legend.click_policy="hide"

def calc_HC (temps, dims, conductivity, desired_temp):
    k=conductivity
    Area=2*(dims[0]*dims[2])+ 2*(dims[1]*dims[2])
    Tcold=desired_temp
    d=dims[3]
    new_list=[]
    for i in temps:
        new_list.append(2419200*(k*Area)*(i-Tcold)/d)
    return new_list

k_sand = 0.27  # thermal conductivity of dry sand W/mK
k_water = 0.6  # thermal conductivity of water W/mK
k_brick = 0.72  # thermal conductivity of brick W/mK
e_sand = 0.343  # porosity of sand


out1=calc_HC(CostaRica.temps, initial_dims, k_brick, 15)
#print(out1)
source=ColumnDataSource(data=dict(time=time_range1, output=out1))

g1=figure(title="Heat per Time", x_axis_label="Time (in Months)", y_axis_label="Heat per Time", tools=TOOLS)
g1.line('time', 'output', source=source, color="purple", legend_label="Heat Conduction", line_dash=[4,4], line_width=3)
g1.legend.click_policy="hide"
g1.title.text_font_size='15pt'

slide_length=Slider(title="Length of Chamber", value=initial_dims[0], start=0, end=12, step=0.5)
slide_width=Slider(title="Width of Chamber", value=initial_dims[1], start=0, end=12, step=0.5)
slide_height=Slider(title="Height of Chamber", value=initial_dims[2], start=0, end=5, step=0.25)
slide_thick=Slider(title="Thickness of Sand Layer in Chamber Wall", value=initial_dims[3], start=0, end=1, step=0.001)
select_material=Select(title="Choice of Material for Walls of the Chamber:", value="Brick", options=materials)
slide_desired_temp=Slider(title="Desired Temperature for the Inner Chamber", value=20, start=2, end=50, step=0.5)
location_select=Select(title="Location", value="Puerta Jimenez, Costa Rica", options=loc_and_time)


def latent_heat(temp):
    #Interpolating the values for latent heat of evaporation
    y = [45054, 44883,44627,44456,44200,43988,43774,43602,43345,43172,42911,42738,42475,42030,41579,41120] #latent heat of vaporization array
    x = [0,5,10,15,20,25,30,35,40,45,50,55,60,70,80,90] #water temperature array
    f1 = interp1d(x, y, kind= 'cubic')
    return f1(temp)

latent_out=latent_heat(CostaRica.temps)


def SVP(temp):
    #Interpolate the values for Saturated Vapor Pressure
    x=[.01, 4, 5, 6, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29,
       30, 31, 32, 33, 34, 35, 36, 38, 40, 45, 50, 55, 60, 65, 70]
    y=[0.00611, 0.00813, 0.00872, 0.00935, 0.01072, 0.01228, 0.01312, 0.01402, 0.01497, 0.01598, 0.01705, 0.01818, 0.01938, 0.02064, 0.02198,
       0.02339, 0.02487, 0.02645, 0.02810, 0.02985, 0.03169, 0.03363, 0.03567, 0.03782, 0.04008, 0.04246, 0.04496, 0.04759, 0.05034, 0.05324,
       0.05628, 0.05947, 0.06632, 0.07384, 0.09593, .1235, .1576, .1994, .2503, .3119]
    vals=interp1d(x, y, kind='cubic')
    return vals(temp)

def water_needed(dims, temp, SVP):
    theta=1079*0.62198
    SA=2*(dims[0]+dims[3]+.225)*dims[2] + 2*dims[2]*(dims[1]+dims[3]+.225)
    hr=9*24*30 #heat of respiration of potatoes in ml CO2 per kg month
    A = 18.3036
    B = 3816.44
    C = -46.13
    p_star=[]
    p_air=[]
    evap_rate=[]
    for i in temp:
        p_star.append(np.exp(A - B / (C + i + 273))) # Antoine equation for vapor pressure at outside air
    for j in p_star:
        p_air.append(hr*j) # bulk pressure of air at t bulk -- modified by SR - using rh instead of a constant value.
    for x in range(0,12):
        yy=theta*((p_air[x]-p_star[x])/760)*SA*(1/1000) #in g/sec
        yy=yy*(1/1000)*3600 #in L/
        yyy=yy*24*30 #in L/month
        evap_rate.append(yyy)
    return evap_rate

vap_init=[]
for p in CostaRica.temps:
    vap_init.append(SVP(p))
water_monthly=water_needed(initial_dims, CostaRica.temps, vap_init)
sourceW=ColumnDataSource(data=dict(time=time_range1, temps=CostaRica.temps, water=water_monthly))

g3=figure(title="Water Added to System For It To Function Properly", x_axis_label='Time (in Months)', y_axis_label='Water Added (in Liters)', tools=TOOLS)
g3.line('time', 'water', source=sourceW, color='blue', line_width=2)
g3.title.text_font_size='12pt'

#Evaporative Cooling Rate Q/t=mLv/t
def evap_cool(mass, latent, time):
    cooling_rate=[]
    for w in range(0,12):
        cooling_rate.append((mass[w]*latent[w]/(time[w]+1))/100)
    return cooling_rate

evap_out=evap_cool(water_monthly, latent_out, time_range1)    
source3=ColumnDataSource(data=dict(time=time_range1, evap_out=evap_out))
g1.line('time', 'evap_out', source=source3, color='orange', legend_label="Evaporation Cooling Rate", line_width=3)


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
    water_cost=water_amount*0.0001
    final_cost=materials_cost+water_cost
    return final_cost

price1=cost_calc(initial_dims, sum(water_monthly), "Brick")
#print(price1)
sourceP=ColumnDataSource(data=dict(price=[price1]))

sourceTable=ColumnDataSource(data=dict(name=[CostaRica.location], price=[round(price1, 2)], DayWater=[round(sum(water_monthly), 2)], space=[initial_dims[0]*initial_dims[1]*initial_dims[2]]))
columnsT=[TableColumn(field='name', title='Location and Time'), TableColumn(field='space', title='Storage Volume Capacity (in m^3)'), TableColumn(field='DayWater', title='Amount of Water Used Monthly (in L)'), TableColumn(field='price', title='Yearly Cost in $')]
data_table=DataTable(source=sourceTable, columns=columnsT)


def update_data(attr, old, new):
    #Get Slider Values
    length=slide_length.value
    height=slide_height.value
    width=slide_width.value
    mat=select_material.value
    thick=slide_thick.value
    want_temp=slide_desired_temp.value
    loc=location_select.value
    cond=0
    place=CostaRica
    #loc_and_time=["Bethlehem, PA", "Miami, Fl", "Puerta Jimenez, Costa Rica", "Quito, Ecuador", "Nairobi, Kenya", "Lusaka, Zambia"]
    if loc=="Miami, FL":
        place=Miami
    elif loc=="Puerta Jimenez, CostaRica":
        place=CostaRica
    elif loc=="Quito, Ecuador":
        place=Ecuador
    elif loc=="Nairobi, Kenya":
        place=Kenya
    elif loc=="Lusaka, Zambia":
        place=Zambia
    if mat =="Brick":
        cond=0.72
    elif mat=="Cardboard":
        cond=0.048 
    elif mat=='Aluminum':
        cond=205 
    elif mat=='Concrete':
        cond=0.8
    dims=[length, width, height, thick]
    out=calc_HC(place.temps, dims, cond, want_temp)
    water=water_needed(dims, place.temps, vap_init)
    price=cost_calc(dims, sum(water), mat)
    latent=latent_heat(place.temps)
    evap=evap_cool(water, latent, time_range1)
    
    source.data=dict(time=time_range1, output=out)
    sourceW.data=dict(time=time_range1, temps=place.temps, water=water)
    source3.data=dict(time=time_range1, evap_out=evap)
    sourceTable.data=dict(name=[place.location], price=[round(price, 2)], DayWater=[round(sum(water), 2)], space=[dims[0]*dims[1]*dims[2]])
   

updates=[location_select, select_material, slide_length, slide_height, slide_width, slide_thick, slide_desired_temp]
for u in updates:
    u.on_change('value', update_data)

widgets=column(location_select, select_material, slide_length, slide_height, slide_width, slide_thick, slide_desired_temp, data_table)
graphs=column(row(g1, diff_temps), g3)

curdoc().add_root(row(widgets, graphs))
curdoc().title="Heat Transfer and Cost for ZECC Model"



