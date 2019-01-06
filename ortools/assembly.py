


from __future__ import print_function
import pandas as pd
import collections
from random import randint

# Import Python wrapper for or-tools CP-SAT solver.
from ortools.sat.python import cp_model



df = pd.read_csv('assembly-input-1.csv')
number_of_orders = len(df)



class assemly_group():
     useage = 0
     def __init__(self, number):
         self.number = int(number)
       
     def update(self,value):
         self.useage = self.useage + int(value)



all_groups = []
useage = []


for i in range(4):
    group = []
    group.append(i)
    group.append(0)
    all_groups.append(assemly_group(i))
    useage.append(group)





#def assembly_schedule():
#    #all_orders.sort(key = lambda x: x.priority, reverse = False)
#    for i in range(len(all_orders)):
#        group = randint(0,3)
#        all_orders[i].set_group(group)
#        all_groups[group].update( all_orders[i].a_time)



def MinimalJobshopSat():
    #Create the model
    model = cp_model.CpModel()
    machine_count = 1 + max(task[0] for job in jobs_data for task in job)
    all_machines = range(machine_count)
    jobs_count = len(jobs_data) #count how many jobs there is
    all_jobs = range(jobs_count)

    #Compute horizon
    horizon = sum(task[1]  for job in jobs_data for task in job)
    print(horizon)

    #data type container
    #create a namedtuple that name task_type with three input parameter of start, end and interval.
    task_type = collections.namedtuple('task_type', 'start end interval')
    #similar to the one above, with three variables of start, job and index. 
    #assigned task type is used to store solution. Not needed to define the problem. 
    assigned_task_type = collections.namedtuple('assigned_task_type', 'start job index')

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
    
    #create and add disjunctive constraints
    for machine in all_machines:
        intervals = []
        for job in all_jobs:
            for task_id, task in enumerate(jobs_data[job]):
                if task[0] == machine:
                    intervals.append(all_tasks[job,task_id].interval)
        #add nonoverlapping constraint for each machine. 
        model.AddNoOverlap(intervals)

    #Add precedent constraint
    for job in all_jobs:
        for task_id in range(0,len(jobs_data[job]) -1 ):
            model.Add(all_tasks[job, task_id + 1].start >= all_tasks[job, task_id].end)

    #makespan objective
    obj_var = model.NewIntVar(0,horizon,'makespan')
    model.AddMaxEquality(obj_var,[all_tasks[(job,len(jobs_data[job]) - 1)].end for job in all_jobs])
    model.Minimize(obj_var)

    #solve_model
   
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30.0
    status = solver.Solve(model)

    if status == cp_model.FEASIBLE:
        print('Feasible Schedule Length: %i' % solver.ObjectiveValue())
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
        print()





#assembly_schedule()


#print(df['Current Status'])

