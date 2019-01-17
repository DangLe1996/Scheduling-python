# -*- coding: utf-8 -*-
"""
Created on Mon Dec 31 14:20:26 2018

@author: baoda
"""

from __future__ import print_function
import pandas as pd
import collections


# Import Python wrapper for or-tools CP-SAT solver.
from ortools.sat.python import cp_model

def MachineShopScheduling(all_orders):
    #not_used = ['section', 'order_number','final_a',   'tasks', 'task_type']
    sequence = ['mill', 'punch', 'welding', 'house_a', 'lens_cut', 'lens_a', 'manu']
    for i in range(len(sequence)):
        sequence[i] = sequence[i]  + '_total_time'
    allowed_status = ['Machine Shop Started', 'Machine Shop Not Started']
    sequence_qty = ['mill', 'punch', 'welding', 'house_a', 'lens_cut', 'lens_a', 'manu']
    #Create the model
    model = cp_model.CpModel()
    machine_count = len(sequence)
    all_machines = range(machine_count)
    
    #Compute horizon
    horizon = sum(int(value) for o in all_orders for s in o.sections for attr, value in s.__dict__.items() 
                  if attr in sequence and o.status in allowed_status)
    if(horizon > 0):
        print("Horizon = " + str(horizon))
        task_type = collections.namedtuple('task_type', 'start end interval')
        for o in all_orders:
            if(o.status in allowed_status):
                for s in o.sections:
                    for task_id, attr in enumerate(sequence):
                             start_var = model.NewIntVar(0,horizon,'start_%i_%i_%i' %(o.number,s.section, task_id))
                             duration = getattr(s,attr)
                             end_var = model.NewIntVar(0,horizon,'end_%i_%i_%i' %(o.number,s.section, task_id))
                             interval_var = model.NewIntervalVar(start_var,duration,end_var,'interval_%i_%i_%i'%(o.number,s.section,task_id))  
                             s.update_time(attr,task_type(start = start_var,  end = end_var, interval = interval_var))

    
         #create and add disjunctive constraints
       
        count = 0
        for task_id, attr in enumerate(sequence): #enumerator
                intervals = []
                for o in all_orders:
                    if(o.status in allowed_status):
                        for s in o.sections:
                            intervals.append(s.tasks[attr].interval)
                            for i in range(machine_count-1):
                                count += 1
                                #add precedent constraint
                                model.Add(s.tasks[sequence[i + 1]].start >= s.tasks[sequence[i]].end)
                           
                   
                #add nonoverlapping constraint for each machine. 
                count += 1
                model.AddNoOverlap(intervals)
        print('Number of precedent const is ' + str(count))


      

         #makespan objective
        obj_var = model.NewIntVar(0,horizon,'makespan')       
        model.AddMaxEquality(obj_var,[s.tasks[sequence[-1]].end for o in all_orders for s in o.sections if o.status in allowed_status])    
        model.Minimize(obj_var)

        solver = cp_model.CpSolver()
        solver.parameters.max_time_in_seconds = 30.0
        #status = 0
        status = solver.Solve(model)

        if status == cp_model.FEASIBLE:
            print('Feasible Schedule Length: %i' % solver.ObjectiveValue())
            print('Number of Branches explored: %i' %solver.NumBranches())
        #    print()
        for o in all_orders:
            if o.status in allowed_status:
                for s in o.sections:
                    for i in range(machine_count):
                        s.start.append(solver.Value(s.tasks[sequence[i ]].start))
                        s.finish.append(solver.Value(s.tasks[sequence[i ]].end))
        if status == cp_model.OPTIMAL:
            # Print out makespan.
            print('Optimal Schedule Length: %i' % solver.ObjectiveValue())
            print()
        return 1
    else: 
        print('No jobs to schedule')
        return 0
    #for job in all_jobs:
    #    for task_id in range(0,len(jobs_data[job]) -1 ):
    #        model.Add(all_tasks[job, task_id + 1].start >= all_tasks[job, task_id].end)
    

def AssemblyScheduling(all_orders):
    pass
  
