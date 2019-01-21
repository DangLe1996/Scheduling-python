# -*- coding: utf-8 -*-
"""
Created on Mon Dec 31 14:20:26 2018

@author: baoda
"""

from __future__ import print_function
import pandas as pd
import collections
import math


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
    

def AssemblyScheduling(all_orders, useages):

       # Instantiate a cp model.
   
    horizon = sum(o.a_time for o in all_orders); 
    
    horizon = horizon + sum(value for key, value in useages.items())
    horizon =math.ceil(horizon )
    model = cp_model.CpModel()
    # Variables
    makespan = model.NewIntVar(0, horizon, 'makespan')
    x = {}
    start= {}
    y = {}
    inter = []
    for o in all_orders:
        t = []
        for p in all_orders :
            if p.number !=  o.number:
                try:
                    inter = intersection(o.qualified_group, p.qualified_group)
                    if(len(inter) > 0):
                        for r in inter:
                            y[(o.number, p.number, r)] = model.NewBoolVar('y[%i,%i, %i]' % (o.number, p.number, r))
                except TypeError:
                    if o.qualified_group ==  p.qualified_group :
                        inter = o.qualified_group
                        y[(o.number, p.number, inter)] = model.NewBoolVar('y[%i,%i, %i]' % (o.number, p.number, inter))
        try:       
            for g in o.qualified_group: 
                x[(o.number,g)] = model.NewBoolVar('x[%i,%i]' % (o.number, g))
            start[o.number] = model.NewIntVar(0,horizon,'start[%i]' % o.number)
        except TypeError:
            g = o.qualified_group
            x[(o.number,g)] = model.NewBoolVar('x[%i,%i]' % (o.number, g))
            start[o.number] = model.NewIntVar(0,horizon,'start[%i]' % o.number)


    ## Constraints

    # Each task is assigned one qualified group.
    for o in all_orders:
        try:
            model.Add(sum(x[(o.number, g)] for g in o.qualified_group) == 1) 
            [model.Add(start[o.number] >= useages[g] *x[(o.number, g)] ) for g in o.qualified_group]
        except TypeError:
            model.Add(x[(o.number, o.qualified_group)]  == 1) 
            #model.Add(start[o.number] >= useages[o.qualified_group] )

    for o in all_orders:
        for p in all_orders :
            if p.number > o.number:
                try:
                    inter = intersection(o.qualified_group, p.qualified_group)
                    if(len(inter) > 0):
                        for r in inter:
                             model.Add(start[o.number] >= start[p.number] + p.a_time).OnlyEnforceIf(y[(o.number, p.number, r)])
                             model.Add(start[p.number] >= start[o.number] + o.a_time).OnlyEnforceIf(y[(p.number, o.number, r)])
                             model.Add(y[(o.number, p.number, r)] + y[(p.number, o.number, r)] >= x[(o.number, r)] + x[(p.number, r)] - 1)
                             model.Add(y[(o.number, p.number, r)] + y[(p.number, o.number, r)] <= x[(o.number, r)])
                             model.Add(y[(o.number, p.number, r)] + y[(p.number, o.number, r)] <=  x[(p.number, r)])
                            
                            #model.add(y[(o.number, p.number, r)] == 0).OnlyEnforceIf(x[(o.number, r)].Not())
                            #model.add(y[(o.number, p.number, r)] == 0).OnlyEnforceIf(x[(p.number, r)].Not())
                           
                            #model.Add(y[(o.number, p.number, r)] + y[(o.number, p.number, r)] == 1).OnlyEnforceIf(x[(o.number, r)] and x[(p.number, r)])
                except TypeError:
                    if o.qualified_group ==  p.qualified_group :
                        r = o.qualified_group
                        model.Add(start[o.number] >= start[p.number] + p.a_time).OnlyEnforceIf(x[(o.number, r)] and x[(p.number, r)] and y[(o.number, p.number, r)])
                        model.Add(start[p.number] >= start[o.number] + o.a_time).OnlyEnforceIf(x[(o.number, r)] and x[(p.number, r)] and y[(o.number, p.number, r)].Not())

    ## Total task size for each worker is at most total_size_max
    ##for i in all_workers:
    ##    model.Add(sum(sizes[j] * x[i][j] for j in all_tasks) <= total_size_max)

    ## Total cost
    [model.Add(makespan >= start[o.number] + o.a_time)  for o in all_orders]
    model.Minimize(makespan)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5.0
    status = solver.Solve(model)
    print('Status is ', solver.StatusName(status))
    if status == cp_model.FEASIBLE:
        print('Feasible sol = %i' % solver.ObjectiveValue())
        assign_solution(solver, all_orders, start, x)
    if status == cp_model.OPTIMAL:
        print('Optimal sol = %i' % solver.ObjectiveValue())
        assign_solution(solver,all_orders, start, x)
        #print()
        #for i in all_workers:
        #    for j in all_tasks:
        #        if solver.Value(x[i][j]) == 1:
        #            print('Worker ', i, ' assigned to task ', j, '  Cost = ',
        #                  cost[i][j])

        #print()

    #print('Statistics')
    #print('  - conflicts : %i' % solver.NumConflicts())
    #print('  - branches  : %i' % solver.NumBranches())
    #print('  - wall time : %f s' % solver.WallTime())

def best_fit(solution, useage):
    for key, o in solution.items():
        if(o.Status > 1):
            if type(o.qualified_group) == list:
                for g in o.qualified_group:
                    if(g != o.group):
                        if(useage[o.group] - useage[g] >= o.a_time):
                            useage[o.group] -= o.a_time
                            useage[g] += o.a_time
                            o.group = g


def assign_solution(solver, all_orders, start, x):
    for o in all_orders:
            setattr(o, 'start', solver.Value(start[o.number]))
            setattr(o, 'finish', o.start + o.a_time)
            try:
                for g in o.qualified_group:
                    if solver.Value(x[(o.number,g)]) == 1:
                        setattr(o, 'group', g)
            except TypeError: 
                setattr(o, 'group', o.qualified_group)


  
def common_member(a, b): 
    a_set = set(a) 
    b_set = set(b) 
    if (a_set & b_set): 
        return True 
    else: 
        return False

def intersection(lst1, lst2): 
    return list(set(lst1) & set(lst2))