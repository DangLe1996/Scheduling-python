# -*- coding: utf-8 -*-
"""
Created on Mon Dec 31 14:20:26 2018

@author: baoda
"""

from __future__ import print_function
import pandas as pd
import collections
from assembly import MinimalJobshopSat

# Import Python wrapper for or-tools CP-SAT solver.
from ortools.sat.python import cp_model

def MachineShopScheduling(all_orders, all_sections, map_section):
    #not_used = ['section', 'order_number','final_a',   'tasks', 'task_type']
    sequence = ['mill', 'punch', 'welding', 'house_a', 'lens_cut', 'lens_a', 'manu']
    #Create the model
    model = cp_model.CpModel()
    machine_count = len(sequence)
    all_machines = range(machine_count)
    #jobs_count = len(all_sections) #count how many jobs there is
    jobs_count = 2 #count how many jobs there is
    all_jobs = range(jobs_count)
    #Compute horizon
    horizon = sum(int(value)  for s in all_sections for attr, value in s.__dict__.items() 
                  if attr in sequence)

    task_type = collections.namedtuple('task_type', 'start end interval')
    for o in all_orders:
        #start_a_var = model.NewIntVar(0,horizon, 'start_assembly_%i' %(int(o.number)))
        #duration = o.a_time
        #end_a_var = model.NewIntVar(0,horizon, 'end_assembly_%i' %(int(o.number)))
        #o.update_time(start_a_var, duration, end_a_var )
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
                for s in o.sections:
                    intervals.append(s.tasks[attr].interval)
            #add nonoverlapping constraint for each machine. 
            count += 1
            model.AddNoOverlap(intervals)
    print('Number of precedent const is ' + str(count))


     #Add precedent constraint
    count = 0
    for o in all_orders:
        for s in o.sections:
            for i in range(machine_count-1):
                count += 1
                model.Add(s.tasks[sequence[i + 1]].start >= s.tasks[sequence[i]].end)
    print('Number of const is ' + str(count))


     #makespan objective
    obj_var = model.NewIntVar(0,horizon,'makespan')
    model.AddMaxEquality(obj_var,[s.tasks[sequence[-1]].end for o in all_orders for s in o.sections])
    model.Minimize(obj_var)

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30.0
    #status = 0
    status = solver.Solve(model)

    if status == cp_model.FEASIBLE:
        print('Feasible Schedule Length: %i' % solver.ObjectiveValue())
    #    print()
    for o in all_orders:
        for s in o.sections:
            for i in range(machine_count):
                s.start.append(solver.Value(s.tasks[sequence[i ]].start))
                s.finish.append(solver.Value(s.tasks[sequence[i ]].end))
    if status == cp_model.OPTIMAL:
        # Print out makespan.
        print('Optimal Schedule Length: %i' % solver.ObjectiveValue())
        print()
    #for job in all_jobs:
    #    for task_id in range(0,len(jobs_data[job]) -1 ):
    #        model.Add(all_tasks[job, task_id + 1].start >= all_tasks[job, task_id].end)
    


  


def MinimalJobshopSat(jobs_data, all_orders):
    #Create the model
    model = cp_model.CpModel()
    machine_count = 7
    all_machines = range(machine_count)
    #jobs_count = len(jobs_data) #count how many jobs there is
    jobs_count = len(jobs_data) #count how many jobs there is
    all_jobs = range(jobs_count)

    #Compute horizon
    horizon = sum(task[1]  for job in jobs_data for task in job)
    print(horizon)

    #data type container
    #create a namedtuple that name task_type with three input parameter of start, end and interval.
    task_type = collections.namedtuple('task_type', 'start end interval')
    assembly_type = collections.namedtuple('assembly_type', 'start end interval')
    #similar to the one above, with three variables of start, job and index. 
    #assigned task type is used to store solution. Not needed to define the problem. 
    assigned_task_type = collections.namedtuple('assigned_task_type', 'start job index')

    #orders = {}
    #for o in all_orders:
    #    order = []
    #    start_assembly_var = model.NewIntVar(0,horizon, 'start_assembly_%i' %(o))
    #    duration = o.a_time
    #    end_assembly_var = model.NewIntVar(0,horizon, 'end_assembly_%i' %(o))
    #    orders[o.number] = assembly_type(start_assembly_var,
    #                                                  duration, end_assembly_var)

    #create jobs
    all_tasks = {} #dictionary
    for job in all_jobs:
        for task_id, task in enumerate(jobs_data[job]): #enumerator
            start_var = model.NewIntVar(0,horizon,'start_%i_%i' %(job, task_id))
            duration = task[1]
            end_var = model.NewIntVar(0,horizon,'end_%i_%i' %(job, task_id))
            interval_var = model.NewIntervalVar(start_var,duration,end_var,'interval_%i_%i'%(job,task_id))
            #use job and task_id to create a dictionary
            all_tasks[job,task_id] = task_type(start = start_var, end = end_var, interval = interval_var)
    #create assembly constraint

     #for o in all_orders:
     #    for s in o.sections:
     #        model.Add(orders[o.number].start_assembly_var >=  )


    #create and add disjunctive constraints
    count = 0
    for machine in all_machines:
        intervals = []
        for job in all_jobs:
            #for task_id, task in enumerate(jobs_data[job]):
            #    if task[0] == machine:
                    intervals.append(all_tasks[job,machine].interval)
        #add nonoverlapping constraint for each machine. 
        count +=1
        model.AddNoOverlap(intervals)
    print('Number of precedent const is ' + str(count))


    count = 0
    #Add precedent constraint
    for job in all_jobs:
        for task_id in range(0,len(jobs_data[job]) -1 ):
            count +=1
            model.Add(all_tasks[job, task_id + 1].start >= all_tasks[job, task_id].end)
    print('Number of const is ' + str(count))


    #makespan objective
    obj_var = model.NewIntVar(0,horizon,'makespan')
    model.AddMaxEquality(obj_var,[all_tasks[(job,len(jobs_data[job]) - 1)].end for job in all_jobs])
    model.Minimize(obj_var)

    #solve_model

   
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30.0
    #status = solver.Solve(model)
    status = 0
    assigned_task_type = collections.namedtuple('assigned_task_type', 'start job index')

    if status == cp_model.FEASIBLE:

        print('feasible schedule length: %i' % solver.ObjectiveValue())
        print()
         # Create one list of assigned tasks per machine.
        assigned_jobs = [[] for _ in all_machines]
        for job in all_jobs:
            for task_id, task in enumerate(jobs_data[job]):
                machine = task[0]
                assigned_jobs[machine].append(
                    assigned_task_type(
                        start=solver.Value(all_tasks[job, task_id].start),
                        job=job,
                        index=task_id))

        disp_col_width = 10
        sol_line = ''
        sol_line_tasks = ''

        print('Feasible Schedule', '\n')

        for machine in all_machines:
            # Sort by starting time.
            assigned_jobs[machine].sort()
            sol_line += 'Machine ' + str(machine) + ': '
            sol_line_tasks += 'Machine ' + str(machine) + ': '

            for assigned_task in assigned_jobs[machine]:
                name = 'job_%i_%i' % (assigned_task.job, assigned_task.index)
                # Add spaces to output to align columns.
                sol_line_tasks += name + ' ' * (disp_col_width - len(name))
                start = assigned_task.start
                duration = jobs_data[assigned_task.job][assigned_task.index][1]

                sol_tmp = '[%i,%i]' % (start, start + duration)
                # Add spaces to output to align columns.
                sol_line += sol_tmp + ' ' * (disp_col_width - len(sol_tmp))

            sol_line += '\n'
            sol_line_tasks += '\n'

        print(sol_line_tasks)
        print('Task Time Intervals\n')
        print(sol_line)

    if status == cp_model.OPTIMAL:
        # Print out makespan.
        print('Optimal Schedule Length: %i' % solver.ObjectiveValue())
    #    print()


#def MinimalJobshopSat():
#    """Minimal jobshop problem."""
#    # Create the model.
#    model = cp_model.CpModel()

   
#    #jobs_data = [  # task = (machine_id, processing_time).
#    #    [(0, 3), (1, 2), (2, 2)],  # Job0
#    #    [(0, 2), (2, 1), (1, 7)],  # Job1
#    #    [(0, 2), (2, 1), (1, 4)],  # Job1
#    #    [(0, 2), (2, 1), (1, 4)],  # Job1
#    #    [(0,6), (2, 5), (1, 4)],  # Job1
#    #    [(0, 2), (2, 3), (1, 4)],  # Job1
#    #    [(0, 2), (2, 5), (1, 6)],  # Job1
#    #    [(0, 2), (2, 1), (1, 4)],  # Job1
#    #    [(0, 2), (2, 6), (1, 3)],  # Job1
#    #    [(0, 9), (2, 1), (1, 4)],  # Job1
#    #    [(1, 4), (2, 3)]  # Job2
#    #]

#    machines_count = 1 + max(task[0] for job in jobs_data for task in job)
#    #for job in jobs_data:
#    #    for task in job:
#    #        print(task[0])
  

#    all_machines = range(machines_count)
#    jobs_count = len(jobs_data)
#    all_jobs = range(jobs_count)

#    # Compute horizon.
#    horizon = sum(task[1] for job in jobs_data for task in job)

#    task_type = collections.namedtuple('task_type', 'start end interval')
#    assigned_task_type = collections.namedtuple('assigned_task_type',
#                                                'start job index')

#    # Create jobs.
#    all_tasks = {}
#    for job in all_jobs:
#        for task_id, task in enumerate(jobs_data[job]):
#            start_var = model.NewIntVar(0, horizon,
#                                        'start_%i_%i' % (job, task_id))
#            duration = task[1]
#            end_var = model.NewIntVar(0, horizon, 'end_%i_%i' % (job, task_id))
#            interval_var = model.NewIntervalVar(
#                start_var, duration, end_var, 'interval_%i_%i' % (job, task_id))
#            all_tasks[job, task_id] = task_type(
#                start=start_var, end=end_var, interval=interval_var)

#    # Create and add disjunctive constraints.
#    for machine in all_machines:
#        intervals = []
#        for job in all_jobs:
#            for task_id, task in enumerate(jobs_data[job]):
#                if task[0] == machine:
#                    intervals.append(all_tasks[job, task_id].interval)
#        model.AddNoOverlap(intervals)

#    # Add precedence contraints.
#    for job in all_jobs:
#        for task_id in range(0, len(jobs_data[job]) - 1):
#            model.Add(all_tasks[job, task_id +
#                                1].start >= all_tasks[job, task_id].end)

#    # Makespan objective.
#    obj_var = model.NewIntVar(0, horizon, 'makespan')
#    model.AddMaxEquality(
#        obj_var,
#        [all_tasks[(job, len(jobs_data[job]) - 1)].end for job in all_jobs])
#    model.Minimize(obj_var)

#    # Solve model.
#    solver = cp_model.CpSolver()
#    status = solver.Solve(model)

#    if status == cp_model.OPTIMAL:
#        # Print out makespan.
#        print('Optimal Schedule Length: %i' % solver.ObjectiveValue())
#        print()

#        # Create one list of assigned tasks per machine.
#        assigned_jobs = [[] for _ in all_machines]
#        for job in all_jobs:
#            for task_id, task in enumerate(jobs_data[job]):
#                machine = task[0]
#                assigned_jobs[machine].append(
#                    assigned_task_type(
#                        start=solver.Value(all_tasks[job, task_id].start),
#                        job=job,
#                        index=task_id))

#        disp_col_width = 10
#        sol_line = ''
#        sol_line_tasks = ''

#        print('Optimal Schedule', '\n')

#        for machine in all_machines:
#            # Sort by starting time.
#            assigned_jobs[machine].sort()
#            sol_line += 'Machine ' + str(machine) + ': '
#            sol_line_tasks += 'Machine ' + str(machine) + ': '

#            for assigned_task in assigned_jobs[machine]:
#                name = 'job_%i_%i' % (assigned_task.job, assigned_task.index)
#                # Add spaces to output to align columns.
#                sol_line_tasks += name + ' ' * (disp_col_width - len(name))
#                start = assigned_task.start
#                duration = jobs_data[assigned_task.job][assigned_task.index][1]

#                sol_tmp = '[%i,%i]' % (start, start + duration)
#                # Add spaces to output to align columns.
#                sol_line += sol_tmp + ' ' * (disp_col_width - len(sol_tmp))

#            sol_line += '\n'
#            sol_line_tasks += '\n'

#        print(sol_line_tasks)
#        print('Task Time Intervals\n')
#        print(sol_line)






