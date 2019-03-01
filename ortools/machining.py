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
from ortools.sat.python import cp_model

class order():
    def __init__(self, ID):
        self.ID = ID
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
        'Machine Shop Started': 3,
        'Scheduled/Released':4

       }
    dbug_value = ['Order', 'Line','Status','Priority', 
                  'Ship_date', 'Issue','Missing',
                 'Complete', 'Resolve' ]
    machine_status_dict = {
    'saw' : ['Extrusion cut double saw','Saw Cycle Time',False  ],
    'body_a' : ['BA Status', 'HousingCycle Time',False ],
    'welding' : ['Welding Status','Welding Cycle Time', 'ToDo'] ,
    'punch': ['Punching Required', 'Puching Cycle time',  3],

    }
    cnc_condition = ['CNC Holes', 'CNC MR', 'CNC Controls']
    sequence = ['saw', 'mill', 'punch', 'welding', 'body_a', 'lens']
    fields_input = {
        'Order': 'Order', 
        'Line': 'Line',
        'Status': 'Status', 
        'Priority': 'Sched Date Priority', 
        'Ship_date': 'Scheduled Ship Date',
        'SD': 'SD vs BOM'
        }
    #fields = {'Order':'Order', 'Line':'Line', 'Status':'Status', 'Ship':'Scheduled Ship Date', 'SD':'SD vs BOM', 'Saw':'Saw Cycle Time', 'Welding':'Welding Cycle Time', 'Lens':'Lens Cycle Time'
    #          ,'Saw':'Extrusion cut double saw' , 'BA Status', 'MSLens', 'Welding Status', 'CNC Holes', 'CNC MR', 'CNC Controls',
    #          'Puching Cycle time', 'Milling Cycle time', 'HousingCycle Time', 'Punching Required'}
            
    def __init__(self, index ):
        self.index = index
        self.amount_assigned = {}

class machine_scheduling():
    today = 0
    SORT_ORDER = {}
    map_order ={}
    @classmethod
    def read_data_excel(cls,filename, today, sheet):
        for index, i in enumerate(sub_order.sequence):
            cls.SORT_ORDER[i] = index
        formatter_string = "%d.%m.%Y" 
        today = pd.to_datetime(today, format=formatter_string)
        cls.today = today
        try:
            data_file = pd.read_excel(filename, sheet_name=sheet)
        except FileNotFoundError:
            print('Invalid file input or file does not exist, please check again')
            return 0
        index = 0
        for index, row in data_file.iterrows():
            if row[sub_order.fields_input['SD']] == True :
                if(row[sub_order.fields_input['Order']] not in cls.map_order):
                    ord = order(row[sub_order.fields_input['Order']])
                    setattr(ord, 'status', sub_order.status_rank[row[sub_order.fields_input['Status']]])
                    cls.map_order[row[sub_order.fields_input['Order']]] = ord
                sub = sub_order(row[sub_order.fields_input['Line']])
                for index,value in sub_order.fields_input.items():
                    setattr(sub, index, row[value])
                for i in sub_order.sequence:
                    if i in sub_order.machine_status_dict and row[sub_order.machine_status_dict[i][0]] ==row[sub_order.machine_status_dict[i][2]]:
                        setattr(sub, i,math.ceil(float(getattr(sub,row[sub_order.machine_status_dict[i][1]]))))
                        if math.ceil(float(row[sub_order.machine_status_dict[i][1]])) > 0 : 
                            sub.sequence.append(cls.SORT_ORDER[i])
                    else: setattr(sub,i , 0)
        return 1

    @classmethod
    def MachineShopScheduling(all_orders):
        #not_used = ['section', 'order_number','final_a',   'tasks', 'task_type']
        sequence = ['saw', 'mill', 'punch', 'welding', 'body_a', 'lens']
        #for i in range(len(sequence)):
        #    sequence[i] = sequence[i]  + '_total_time'
        #allowed_status = ['Machine Shop Started', 'Scheduled/Released']
 
        #Create the model
        model = cp_model.CpModel()
        machine_count = len(sequence)
        all_machines = range(machine_count)
    
        #Compute horizon
        horizon = sum(int(value) for o in all_orders for s in o.sections for attr, value in s.__dict__.items() 
                      if attr in sequence  )
        horizon = horizon * 10


        if(horizon > 0):
            print("Horizon = " + str(horizon))
            task_type = collections.namedtuple('task_type', 'start end interval')
            for o in all_orders:
                for s in o.sections:
                    for task_id, attr in enumerate(sequence):
                        try:
                            if getattr(s,attr) > 0:
                                    start_var = model.NewIntVar(0,horizon,'start_%i_%i_%i' %(o.number,s.Line, task_id))
                                    duration = math.ceil (getattr(s,attr))
                                    end_var = model.NewIntVar(0,horizon,'end_%i_%i_%i' %(o.number,s.Line, task_id))
                                    interval_var = model.NewIntervalVar(start_var,duration,end_var,'interval_%i_%i_%i'%(o.number,s.Line,task_id))  
                                    s.update_time(attr,task_type(start = start_var,  end = end_var, interval = interval_var))
                        except AttributeError:
                                    pass

    
             #create and add disjunctive constraints
       
            count = 0
            for task_id, attr in enumerate(sequence): #enumerator
                    intervals = []
                    for o in all_orders:
                        for s in o.sections:
                            try:
                                if getattr(s,attr) > 0:
                                    intervals.append(s.tasks[attr].interval)
                            except AttributeError:
                                    pass
                    model.AddNoOverlap(intervals)

            #precedent constraint
            for o in all_orders:
                    for s in o.sections:
                        for i in range(len(s.sequence) - 1):
                                model.Add(s.tasks[sequence[s.sequence[i+1]]].start >= s.tasks[sequence[s.sequence[i]]].end)

       
      

             #makespan objective
            obj_var = model.NewIntVar(0,horizon,'makespan')       
            model.AddMaxEquality(obj_var,[s.tasks[sequence[attr]].end for o in all_orders for s in o.sections for attr in s.sequence ])    
            model.Minimize(obj_var)

            solver = cp_model.CpSolver()
            solver.parameters.max_time_in_seconds = 30.0
            #status = 0
            status = solver.Solve(model)

            if status == cp_model.FEASIBLE:
                print('Feasible Schedule Length: %i' % solver.ObjectiveValue())
                print('Number of Branches explored: %i' %solver.NumBranches())
                print()
            for o in all_orders:
                for s in o.sections:
                    for i in s.sequence:
                        s.start[sequence[i]] =solver.Value(s.tasks[sequence[i]].start)
                        s.finish[sequence[i]] =solver.Value(s.tasks[sequence[i]].end)
                       
                    
            if status == cp_model.OPTIMAL:
                # Print out makespan.
                print('Optimal Schedule Length: %i' % solver.ObjectiveValue())
                print()
            if status == cp_model.INFEASIBLE:
                # Print out makespan.
                print('infeasible')
                print()
            if status == cp_model.MODEL_INVALID:
                # Print out makespan.
                print('invalid')
                print()
            return 1
        else: 
            print('No jobs to schedule')
            return 0
    #for job in all_jobs:
    #    for task_id in range(0,len(jobs_data[job]) -1 ):
    #        model.Add(all_tasks[job, task_id + 1].start >= all_tasks[job, task_id].end)
    
machine_scheduling.read_data_excel("machine_input.xlsx","1.1.2019",'Data')


  
