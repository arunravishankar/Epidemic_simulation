#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 15 11:19:04 2020

@author: arunravishankar
"""
import matplotlib.pyplot as plt
import pandas as pd
import imageio
import numpy as np
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True

box_dimension = 1000.0
time_step = 1

path = '/home/arunravishankar/Arun Ravishankar/Academics/Data Science/Covid19/Simulation/simulation_files/epidemic_simulation.csv'
path_simulation = '/home/arunravishankar/Arun Ravishankar/Academics/Data Science/Covid19/Simulation/simulation_files/gif/simulation.csv'
path_stackplot = '/home/arunravishankar/Arun Ravishankar/Academics/Data Science/Covid19/Simulation/simulation_files/gif/stackplot.csv'
data = pd.read_csv(path, sep = "\t")

categories = ['Susceptible', 'Incubation', 'Quarantined', 'Hospitalized', 'Hospitals full, quarantined', 'Recovered', 'Dead']
colors = ['dodgerblue', 'gold', 'sienna', 'red', 'lightslategray', 'limegreen', 'black']
colorDict = dict(zip(categories, colors))


timed_data = []
number_until_now = []
time_array = []
for time, data_at_time in data.groupby('Time'):
    timed_data.append(data_at_time)
    
def update_number_statuses(df, categories=categories):
    current_list_statuses = df['Status'].value_counts().index.to_list()
    counts = []
    for i, status in enumerate(categories):
        if status not in current_list_statuses:
            counts.append(0)
        else:
            counts.append(df['Status'].value_counts()[status])

    return counts        

def dfScatter(df, x, y, time, catcol = 'Status'):
    fig = plt.figure(figsize = (7,7))
    ax = fig.add_subplot(111)
    
    ax.scatter(df[x], df[y], c = df['Status'].apply(lambda x: colorDict[x]), rasterized = True)
    ax.axis('off')
    plt.xlim(0, box_dimension+10)
    plt.ylim(0, box_dimension+10)
    fig.savefig('/home/arunravishankar/Arun Ravishankar/Academics/Data Science/Covid19/Simulation/simulation_files/config_%s.png' % time)
    plt.close(fig)


def stackedplot(df, time, number_until_now):
    time_array.append(time)
    fig = plt.figure(figsize = (7,3.5))
    ax = fig.add_subplot(111)
    for i in range(len(categories)):
        plt.plot([], [], color = colors[i], label = categories[i], rasterized = True)
    ax.stackplot(time_array, number_until_now, colors = colors, rasterized = True)    
    plt.xlim(0,time+0.01)
    plt.ylim(0,100)
    plt.legend(loc = 'lower left', fontsize = 'medium')
    fig.savefig('/home/arunravishankar/Arun Ravishankar/Academics/Data Science/Covid19/Simulation/simulation_files/stackplot_%s.png' % time)
    plt.close(fig)

filenames = list('/home/arunravishankar/Arun Ravishankar/Academics/Data Science/Covid19/Simulation/simulation_files/config_%s.png' % time for time in range(0,timed_data[-1]['Time'].unique()[0]))  
filenames_stackplot = list('/home/arunravishankar/Arun Ravishankar/Academics/Data Science/Covid19/Simulation/simulation_files/stackplot_%s.png' % time for time in range(0,timed_data[-1]['Time'].unique()[0]))  
   
def create_gif(filenames, output, duration=0.05):
    images = []
    for filename in filenames:
        images.append(imageio.imread(filename))
    imageio.mimsave(output, images, duration = duration)
    
def run_file(timed_data):
    for time in range(timed_data[-1]['Time'].unique()[0]):
        
        dfScatter(timed_data[time], 'x-coordinate', 'y-coordinate', time)
        number_now = update_number_statuses(timed_data[time], categories)

        if time == 0:
            number_until_now = np.transpose(number_now)
        else:
            number_until_now = np.column_stack((number_until_now, number_now))
        stackedplot(timed_data[time], time, number_until_now)
    
    
simulation_output = '/home/arunravishankar/Arun Ravishankar/Academics/Data Science/Covid19/Simulation/simulation_files/gif/simulation.gif'
stackplot_output = '/home/arunravishankar/Arun Ravishankar/Academics/Data Science/Covid19/Simulation/simulation_files/gif/stackplot.gif'
run_file(timed_data)
create_gif(filenames, simulation_output)
create_gif(filenames_stackplot, stackplot_output)
