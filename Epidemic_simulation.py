#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 15 07:10:39 2020

@author: arunravishankar
"""
import numpy as np
import os
import csv




path = '/home/arunravishankar/Arun Ravishankar/Academics/Data Science/Covid19/Simulation/simulation_files'
file = 'epidemic_simulation.csv'

box_dimension = 1000.0
population = 100
time_step = 1
time_limit = 500
time = 0
velocity_mean = 0
velocity_sigma = 2.5
quarantine_percentage = 95
transmission_radius_factor = 0.93

prob_S_to_I = 0.8
prob_I_to_R = 0.23
prob_I_to_Q = 0.43
prob_I_to_H = 0.34
prob_Q_to_R = 0.65
prob_Q_to_D = 0.35
prob_H_to_R = 0.35
prob_H_to_D = 0.65
prob_HQ_to_R = 0.1
prob_HQ_to_D = 0.9
prob_R_to_I = 0.15

incubation_transmission_radius = 100*transmission_radius_factor
quarantined_transmission_radius = 25*transmission_radius_factor
hospitalized_transmission_radius = 4*transmission_radius_factor

hospital_capacity = int(population*0.05)

incubation_period = 25
hospitalization_period = 50
quarantine_period = 50
hospitals_full_quarantine_period = 50

total_hospitalized = 0

def distance(x1, y1, x2, y2):
    return np.sqrt((x1-x2)**2 + (y1-y2)**2)


def position_sampling(box_dimension):
    """
    Given the dimensions of the box, 
    this function randomly initializes the 
    initial x and y position of the person
    Parameters:
        box_dimension (float) : Size of the box
    Returns:
        x_position (float) : x coordinate of person
        y_position (float) : y coordinate of person
    """
    x_position = box_dimension*np.random.random()
    y_position = box_dimension*np.random.random()
    return(x_position, y_position)

    

def velocity_sampling(mean, sigma, quarantine = 0, sigma2 = 0.1):
    """
    This function samples a velocity from a unimodal
    or bimodal Gaussian.
    Parameters: 
        mean (float) : mean for the main Gaussian distribution
        sigma (float) : sigma for the main Gaussian distribution
        quarantine (float) : percentage of strictness of quarantine
        sigma2 (float) : sigma for the secondary Gaussian distribution
    Returns: 
        x_velocity (float) : x component of velocity
        y_velocity (float) : y component of velocity
    """
    p = 1 - quarantine/100
    if p < 0:
        return 'Quarantine value should be between 0 and 100'
    normal1 = np.random.normal(mean,sigma)
    normal2 = np.random.normal(0,sigma2)
    w = np.random.binomial(n=1, p=p, size=1)      
    velocity = w*normal1 + (1-w)*normal2
    velocity_magnitude = abs(velocity).item()
    angle = 2*np.pi*np.random.random()
    x_velocity = velocity_magnitude*np.cos(angle)
    y_velocity = velocity_magnitude*np.sin(angle)
    return(x_velocity, y_velocity)


class Person:
    """
    This is a class for a person that moves within a box
    Attributes: 
        x_position (float): x coordinate of person
        y_position (float): y coordinate of person
        x_velocity (float): x velocity of person
        y_velocity (float): y velocity of person
        status (string): susceptible, incubation, transmitting, 
        quarantined, hospitalized, quarantined_to_be_hospitalized
    """
    

    
    def __init__(self):
        """
        The attributes that a person has are the position and velocity
        Parameters: 
            x_position (float) : x coordinate
            y_position (float) : y coordinate
            x_velocity (float) : x velocity
            y_velocity (float) : y velocity
        """
        if time == 0:
            self.x_position, self.y_position = position_sampling(box_dimension)
            self.x_velocity, self.y_velocity = velocity_sampling(velocity_mean,
                                                                velocity_sigma)
        else:
            print('Time is not 0')
        
        
        if prob_I_to_R + prob_I_to_Q + prob_I_to_H != 1:
            print('Pre-existing condition probabilities do not add up to 1.')
            
        sampled_Q_H_R = np.random.multinomial(1, [prob_I_to_R, prob_I_to_Q,
                                                  prob_I_to_H])
        if sampled_Q_H_R[0] == 1:
            self.category = 'Healthy'
        elif sampled_Q_H_R[1] == 1:
            self.category = 'Semi-Healthy'
        else:
            self.category = 'At-Risk'
        
        self.status = 'Susceptible'
        
        self.transmission_radius = 0
        
        global total_hospitalized
        
        
    
    def get_current_position(self):
        print(self.x_position, self.y_position)
        return
    
    
    
    def status_check(self):
        if self.status in {'Susceptible', 'Incubation', 'Recovered'}:
            self.move()
        elif self.status in {'Quarantined', 'Hospitals full, quarantined'}:
            self.x_velocity, self.y_velocity = velocity_sampling(velocity_mean,
                            velocity_sigma, quarantine = quarantine_percentage)
            self.move()
        elif self.status in {'Hospitalized', 'Dead'}:
            self.x_velocity, self.y_velocity = velocity_sampling(0,0,0,0)
            self.move()
            
            
            
    def move(self):
        """
        Given an initial position and velocity, this function
        moves the person to the next time step.
        Parameters:
            self : takes and updates the positions and 
            velocities by moving
        """
        self.x_position = self.x_position + self.x_velocity*time_step
        self.y_position = self.y_position + self.y_velocity*time_step  
        self.x_velocity = self.x_velocity
        self.y_velocity = self.y_velocity
    
        if self.x_position > box_dimension or self.x_position < 0:
            self.x_velocity = -self.x_velocity
            self.x_position = self.x_position + self.x_velocity*time_step
    
        elif self.y_position > box_dimension or self.y_position < 0:
            self.y_velocity = -self.y_velocity
            self.y_position = self.y_position + self.y_velocity*time_step 
            
        return
    

    
    def status_update(self):
        
        global total_hospitalized
        
        if self.status in {'Susceptible'}:
            
            self.transmission_radius = 0
            
            if self.in_transmission_zone == 1:    
                sampling_S_to_I = np.random.binomial(n = 1, p = prob_S_to_I, 
                                                     size = 1)[0]
                
                if sampling_S_to_I == 1:
                    self.status = 'Incubation'
                    self.incubation_days = 0
                    
                    
        elif self.status in {'Recovered'}:
            
            self.transmission_radius = 0
            
            if self.in_transmission_zone == 1:    
                sampling_R_to_I = np.random.binomial(n = 1, p = prob_R_to_I,
                                                     size = 1)[0]
                
                if sampling_R_to_I == 1:
                    self.status = 'Incubation'
                    self.incubation_days = 0
                
                
        elif self.status in {'Incubation'}:
            
            self.transmission_radius = incubation_transmission_radius
            self.incubation_days = self.incubation_days + 1
            
            if self.incubation_days < incubation_period:
                self.status = 'Incubation'       
                
            elif self.incubation_days >= incubation_period: 
                
                if self.category == 'Healthy':
                    self.status = 'Recovered'
                    self.x_velocity, self.y_velocity = velocity_sampling(velocity_mean, velocity_sigma, quarantine = 0)
                    
                elif self.category == 'Semi-Healthy':
                    sampling_I_to_Q = np.random.binomial(n = 1,
                                                p = prob_I_to_Q, size = 1)[0]
                    
                    if sampling_I_to_Q == 1:
                        self.status = 'Quarantined'
                        self.days_quarantined = 0
                        
                elif self.category == 'At-Risk':
                    sampling_I_to_H = np.random.binomial(n = 1, 
                                                p = prob_I_to_H, size = 1)[0]
                    
                    if sampling_I_to_H == 1:
                        
                        if total_hospitalized < hospital_capacity:
                            self.status = 'Hospitalized'
                            total_hospitalized = total_hospitalized + 1
                            self.days_hospitalized = 0
                        
                        elif total_hospitalized >= hospital_capacity:
                            self.status = 'Hospitals full, quarantined'
                            self.days_quarantined_hospitals_full = 0
                            
                            
        elif self.status in {'Quarantined'}:
            
            self.transmission_radius = quarantined_transmission_radius
            self.days_quarantined = self.days_quarantined + 1
            
            if self.days_quarantined < quarantine_period:
                self.status = 'Quarantined'
            
            elif self.days_quarantined >= quarantine_period:
                sampling_Q_to_R = np.random.binomial(n = 1,
                                                p = prob_Q_to_R, size = 1)[0]
                
                if sampling_Q_to_R == 1:
                    self.status = 'Recovered'
                    self.x_velocity, self.y_velocity = velocity_sampling(velocity_mean, velocity_sigma, quarantine = 0)

                else:
                    self.status = 'Dead'
            
            
        elif self.status in {'Hospitalized'}:
            
            self.transmission_radius = hospitalized_transmission_radius
            self.days_hospitalized = self.days_hospitalized + 1
            
            if self.days_hospitalized < hospitalization_period:
                self.status = 'Hospitalized'
                
            elif self.days_hospitalized >= hospitalization_period:
                sampling_H_to_R = np.random.binomial(n = 1,
                                                p = prob_H_to_R, size = 1)[0]
                
                if sampling_H_to_R == 1:
                    self.status = 'Recovered'
                    self.x_velocity, self.y_velocity = velocity_sampling(velocity_mean, velocity_sigma, quarantine = 0)

                else:
                    self.status = 'Dead'
                
                total_hospitalized = total_hospitalized - 1
                
                
        elif self.status in {'Hospitals full, quarantined'}:
            
            self.transmission_radius = quarantined_transmission_radius
            self.days_quarantined_hospitals_full = self.days_quarantined_hospitals_full + 1
            
            if self.days_quarantined_hospitals_full < hospitals_full_quarantine_period:
                self.status = 'Hospitals full, quarantined'
                
            elif self.days_quarantined_hospitals_full == hospitals_full_quarantine_period:
                sampling_HQ_to_R = np.random.binomial(n = 1, p = prob_HQ_to_R, size = 1)[0]
                
                if sampling_HQ_to_R == 1:
                    self.status = 'Recovered'
                    self.x_velocity, self.y_velocity = velocity_sampling(velocity_mean, velocity_sigma, quarantine = 0)

                else:
                    self.status = 'Dead'
                    
       
        elif self.status in {'Dead'}:
            
            self.transmission_radius = 0
        

        
    

def initialize_population(population):
            
    persons = []
    for i in range(population):
        person = Person()
        persons.append(person)
    
    persons[0].status = 'Incubation'
    persons[0].incubation_days = 0
    persons[0].transmission_radius = incubation_transmission_radius 

    return(persons)
    
def run_simulation(time_limit, population, persons):
    
    with open(os.path.join(path, file), 'w') as fp:
        writer = csv.writer(fp, delimiter = '\t', lineterminator = '\n',)
        writer.writerow(['Time', 'Person', 'Status', 'x-coordinate', 'y-coordinate', 'Transmission Radius'])
        
    for time in range(time_limit):

        for i in range(population):
            with open(os.path.join(path, file), 'a') as fp:
                writer = csv.writer(fp, delimiter = '\t', lineterminator = '\n',)
                writer.writerow([str(time), str(i+1), persons[i].status, str(round(persons[i].x_position, 4)), str(round(persons[i].y_position, 4)), str(persons[i].transmission_radius)])


        for i in range(population):

            for j in range(population):
                dist = distance(persons[j].x_position, persons[j].y_position, persons[i].x_position, persons[i].y_position)

                if j == i:
                    continue

                if persons[i].status not in {'Susceptible', 'Recovered'}:
                    continue

                if dist < (persons[j].transmission_radius):
                    persons[i].in_transmission_zone = 1

                    break

                else:
                    persons[i].in_transmission_zone = 0

            persons[i].status_update()
            persons[i].status_check()


persons = initialize_population(population)

run_simulation(time_limit, population, persons)
