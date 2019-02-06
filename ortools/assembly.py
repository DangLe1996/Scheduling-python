# -*- coding: utf-8 -*-
"""
Created on Mon Dec 31 14:20:26 2018

@author: baoda
"""

from __future__ import print_function
import pandas as pd
import collections
import math
from operator import attrgetter
from operator import itemgetter

# Import Python wrapper for or-tools CP-SAT solver.

class order():
    def __init__(self, number):
        self.number = number
        self.a_time = 0
        self.sections = []
        self.qualified_group = []
    def set_group(self,group):
        self.qualified_group.append(group)
    def add_section(self,value):
        self.sections.append(value)
    def update_time(self, start, finish, interval):
        self.start = start
        self.finish = finish
class sub_order():
  
     def __init__(self, index ):
        #self.order_number = order_number
        #self.line = line
        self.index = index
        self.tasks = {}
        self.sequence = []
        self.start = {}
        self.finish = {}
     def update_time(self,attr, task_type):
        self.tasks[attr] = task_type
class assembly_scheduling():
    bad_orders = []
    all_sections = []
    map_order = {}
    solution =[]
    solution_machining = []

    @classmethod

    def map_oder_input(cls,sub):
        priority_rank = {
        'High Priority': 1,
        'Priority' : 2,
        'Regular': 3

        }
        if sub not in cls.map_order[sub.Order].sections:
            if cls.map_order[sub.Order].priority > priority_rank [getattr(sub,'Promised')] :
                cls.map_order[sub.Order].priority = priority_rank [getattr(sub,'Promised')]
            cls.map_order[sub.Order].add_section(sub)
            try:
                cls.map_order[sub.Order].a_time += math.ceil(getattr(sub,'Real Time'))
            except TypeError or ValueError :
                 pass

    @classmethod
    def read_data_assembly(cls,filename, today):
#order_input = pd.read_csv('order_input.csv')
        fields = ['Job no.','Order', 'Line', 'Status', 'Sched. Ship Date',
                 'Real Status' , 'Real Time', 'Promised' , 'ISSUE','Missing Materials', 'Production Group', 'Production Group' ]
        #section_input = pd.read_csv("Axis-Assembly-Input.csv", skiprows = 1)
        try:
            assembly_input = pd.read_csv(filename, skipinitialspace=True, usecols=fields)
        except FileNotFoundError:
            print('Invalid file input or file does not exist, please check again')
            return 0
        #print("{} and  {} ".format(assembly_input['Production Group'], assembly_input['Order']))
       
        priority_rank = {
        'High Priority': 1,
        'Priority' : 2,
        'Regular': 3

        }
        status_rank = {
            'Wiring Started': 1,
            'Machine Shop Finished' : 2,
            'Machine Shop Started': 3,
            'Scheduled/Released': 4

            }
        
        good_value = ['0', float('NaN')]
        for index, row in assembly_input.iterrows():
            if row['Order'] not in cls.bad_orders:
                if(row['Status'] in status_rank and row['ISSUE'] in good_value):
                    if(row['Order'] not in map_order):
                        ord = order(row['Order'])
                        setattr(ord, 'priority', 5)
                        map_order[row['Order']] = ord
                    sub = sub_order(index)
            
                    for value in fields:
                        setattr(sub, value, row[value])
                    setattr(sub, 'priority', priority_rank[sub.Promised])
                    formatter_string = "%d.%m.%Y" 
                    datetime_object = datetime.strptime(getattr(sub,'Sched. Ship Date'), formatter_string)
                    subtract = abs((datetime_object - today).days)
                    setattr(sub,'ship_date', datetime_object.date())
                    setattr(sub,'days_from_today', subtract)
                    setattr(sub,'real_time', getattr(sub,'Real Time'))
                    #quali = getattr(sub,'Production Group').split(',')
                    quali = list(map(int, getattr(sub,'Production Group').split(',')))
                    setattr(sub, 'qualified_groups',quali)
                    value = [0, subtract]
                    ID = str(row['Order']) + str(row['Line']) + str(max(value))
                    setattr(sub, 'ID',int(ID))
                    if status_rank[sub.Status] == 1 :
                        sub.Status = 1
                    elif status_rank[sub.Status] == 2:
                        try:
                            if math.isnan(getattr(sub,'Missing Materials')):
                                sub.Status = 2   
                            elif getattr(sub,'Missing Materials') == '=+Cartridge':
                                sub.Status = 3
                            else :sub.Status = 7
                        except TypeError:
                            sub.Status = 7
                    elif status_rank[sub.Status] == 3:
                        if getattr(sub,'Missing Materials') == '=+lens':
                            sub.Status = 4     
                        if getattr(sub,'Missing Materials') == 'Material+Cartridge':
                            sub.Status = 5  
                        if getattr(sub,'Missing Materials') == 'Material+lens+Cartridge+Housing':
                            sub.Status = 6
                        else :sub.Status = 7
                    else :sub.Status = 7
                    if int(sub.Status) :
                        map_oder_input(sub)
                else: 
                    if row['Order'] in bad_orders:
                        bad_orders.remove(row['Order'])
                    else: 
                        bad_orders.append(row['Order'])
        print('File input sucessfully')
        return 1
    def Assembly_Scheduling(all_orders, groups):
        horizon = 5
        from ortools.linear_solver import pywraplp
        solver = pywraplp.Solver('CoinsGridCLP',
                                 pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
        x = {}
        y = {}
        z = {}
        variable_list = []
        for o in all_orders:
            for i in o.sections:
                for j in i.qualified_groups:
                    x[(i.ID,j)] = solver.IntVar(0,1, 'x[%i,%i]' % (i.ID,j))
                    #variable_list.append(x[(i.ID,j)])
                for j in range(horizon):
                    y[(i.ID,j)] = solver.IntVar(0,1, 'y[%i,%i]' % (i.ID,j))
                    #variable_list.append(y[(i.ID,j)])
                    for k in i.qualified_groups:
                        z[(i.ID,j,k)] = solver.IntVar(0,int( i.real_time), 'z[%i,%i,%i]' % (i.ID,j,k))
                        variable_list.append(z[(i.ID,j,k)])
    
        makespan = solver.IntVar(0,horizon, 'makespan')
        days_used = solver.IntVar(0,10000, 'days_used')
        for o in all_orders:
            for i in o.sections:
                solver.Add(solver.Sum([x[(i.ID,j)] for j in i.qualified_groups]) == 1) #one group
                solver.Add(solver.Sum([y[(i.ID,j)] for j in range(horizon)]) >= 1) #multiple days
                [solver.Add(makespan >= y[(i.ID,j)]*j) for j in range(horizon)]
                [solver.Add(z[(i.ID,j,k)] <= i.real_time *x[(i.ID,k)]) for j in range(horizon) for k in i.qualified_groups]
                [solver.Add(z[(i.ID,j,k)] <= i.real_time *y[(i.ID,j)]) for j in range(horizon) for k in i.qualified_groups]
                solver.Add(solver.Sum([z[(i.ID,j,k)]for j in range(horizon) for k in i.qualified_groups]) == int( i.real_time))
        solver.Add(days_used == solver.Sum([y[(i.ID,j)]for j in range(horizon) for o in all_orders for i in o.sections]) )
        for k in groups.number:
            expr = []
            for j in range(horizon):
                for o in all_orders:
                    for i in o.sections:
                        if k in i.qualified_groups:
                            expr.append(z[(i.ID,j,k)])
                solver.Add(solver.Sum(expr[r] for r in range(len(expr))) <= groups.capacity[k])
                expr.clear()


        solver.Minimize(makespan + days_used)
        #solver.Minimize(makespan )
        solver.Solve()
        best = round(makespan.SolutionValue())
        print(round(days_used.SolutionValue()))
        print(best)
        for variable in variable_list:
            if variable.solution_value() > 0:
                print(('%s = %f' % (variable.name(), variable.solution_value())))
        print('finish')