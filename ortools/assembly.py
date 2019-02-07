# -*- coding: utf-8 -*-
"""
Created on Mon Dec 31 14:20:26 2018

@author: baoda
"""

from __future__ import print_function
import pandas as pd
import collections
import math
from operator import attrgetter, itemgetter
import time
from datetime import datetime,date, timedelta 

# Import Python wrapper for or-tools CP-SAT solver.

class order():
    def __init__(self, number):
        self.number = number
        self.a_time = 0
        self.Status = 0
        self.sections = []
    def add_section(self,value):
        self.sections.append(value)
class sub_order():
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
    def __init__(self, index ):
        self.index = index
    

class groups():
    capacity = {}
    @classmethod
    def capacity_input(cls,filename):
        try:
            capacity_input = pd.read_csv(filename, skipinitialspace=True)
        except FileNotFoundError:
            print('Invalid file input or file does not exist, please check again')
            return 0
        for index, row in capacity_input.iterrows():
            cls.capacity[row["Group"]] = row["Capacity"]

class assembly_scheduling():
    bad_orders = []
    all_sections = []
    map_order = {}
    solution =[]
    order_rank = {
        1: [], 
        2: [], 
        3: [], 
        4: [], 
        5: [], 
        6: [], 
        7: []
        
        }

    @classmethod
    def map_oder_input(cls,sub):
        if sub not in cls.map_order[sub.Order].sections:
            if cls.map_order[sub.Order].priority > sub_order.priority_rank [getattr(sub,'Promised')] :
                cls.map_order[sub.Order].priority = sub_order.priority_rank [getattr(sub,'Promised')]
            if sub.Status > cls.map_order[sub.Order].Status:
                cls.map_order[sub.Order].Status = sub.Status 
            cls.map_order[sub.Order].add_section(sub)
            try:
                cls.map_order[sub.Order].a_time += math.ceil(getattr(sub,'Real Time'))
            except TypeError or ValueError :
                 pass

    @classmethod
    def read_data_assembly(cls,filename, today):
        today = datetime.strptime( today,"%d/%m/%Y" )
        fields = ['Job no.','Order', 'Line', 'Status', 'Sched. Ship Date',
                 'Real Status' , 'Real Time', 'Promised' , 'ISSUE',
                 'Missing Materials', 'Production Group', 'Production Group', 'Complete/Partial' ]
        try:
            assembly_input = pd.read_csv(filename, skipinitialspace=True, usecols=fields)
            d_file= open("debug.csv","w")
            d_file.write('Order, Line, Status, Promised, Scheduled Ship Date, Issue, Missing Materials \n')
        except FileNotFoundError:
            print('Invalid file input or file does not exist, please check again')
            return 0
    

        line = []
        good_value = ['0', float('NaN')]
        dbug_value = ['Order', 'Line','Status','Promised', 'Sched. Ship Date', 'ISSUE','Missing Materials', 'Complete/Partial'  ]
        for index, row in assembly_input.iterrows():
            if row['Order'] not in cls.bad_orders:
                if not ( row['Status'] in sub_order.status_rank and row['Complete/Partial'] == 'Complete' and  (pd.isnull(row['ISSUE']) or row['ISSUE'] == '0')):
                    cls.bad_orders.append(row['Order'])
                    for i in dbug_value:
                        line += str(row[i]) + ','
                    line += '\n' 
        line = ''.join(line)
        d_file.write(line)
        for index, row in assembly_input.iterrows():
            if row['Order'] not in cls.bad_orders:
                    if(row['Order'] not in cls.map_order):
                        ord = order(row['Order'])
                        setattr(ord, 'priority', 5)
                        cls.map_order[row['Order']] = ord
                    sub = sub_order(index)
            
                    for value in fields:
                        setattr(sub, value, row[value])
                    setattr(sub, 'priority', sub_order.priority_rank[sub.Promised])
                    formatter_string = "%d.%m.%Y" 
                    datetime_object = datetime.strptime(getattr(sub,'Sched. Ship Date'), formatter_string)
                    subtract = abs((datetime_object - today).days)
                    setattr(sub,'ship_date', datetime_object.date())
                    setattr(sub,'days_from_today', subtract)
                    setattr(sub,'real_time', getattr(sub,'Real Time'))
                    quali = list(map(int, getattr(sub,'Production Group').split(',')))
                    setattr(sub, 'qualified_groups',quali)
                    value = [0, subtract]
                    ID = str(row['Order']) + str(row['Line']) + str(max(value))
                    setattr(sub, 'ID',int(ID))
                    if sub_order.status_rank[sub.Status] == 1 :
                        sub.Status = 1
                    elif sub_order.status_rank[sub.Status] == 2:
                        try:
                            if math.isnan(getattr(sub,'Missing Materials')):
                                sub.Status = 2   
                            elif getattr(sub,'Missing Materials') == '=+Cartridge':
                                sub.Status = 3
                            else :sub.Status = 7
                        except TypeError:
                            sub.Status = 7
                    elif sub_order.status_rank[sub.Status] == 3:
                        if getattr(sub,'Missing Materials') == '=+lens':
                            sub.Status = 4     
                        if getattr(sub,'Missing Materials') == 'Material+Cartridge':
                            sub.Status = 5  
                        if getattr(sub,'Missing Materials') == 'Material+lens+Cartridge+Housing':
                            sub.Status = 6
                        else :sub.Status = 7
                    else :sub.Status = 7
                    cls.map_oder_input(sub)
        print('File input sucessfully')
        for index, ord in cls.map_order.items():
            cls.order_rank[ord.Status].append(ord);
        return cls.order_rank
    def schedule(all_orders, groups):
        if len(all_orders) > 0:
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
            for k, value in groups.capacity.items():
                expr = []
                for j in range(horizon):
                    for o in all_orders:
                        for i in o.sections:
                            if k in i.qualified_groups:
                                expr.append(z[(i.ID,j,k)])
                    solver.Add(solver.Sum(expr[r] for r in range(len(expr))) <= value*60)
                    expr.clear()


            solver.Minimize(makespan + days_used)
            #solver.Minimize(makespan )
            solver.Solve()
            best = round(makespan.SolutionValue())
            print(round(days_used.SolutionValue()))
            print(best)
        #for variable in variable_list:
        #    if variable.solution_value() > 0:
        #        print(('%s = %f' % (variable.name(), variable.solution_value())))
      