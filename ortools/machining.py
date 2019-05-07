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
from datetime import datetime,date, timedelta 

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
    def __init__(self, index ):
        self.index = index
        self.tasks = {}
        self.sequence = []
        self.start = {}
        self.finish = {}
    def update_time(self,attr, task_type):
        self.tasks[attr] = task_type
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
    'saw' : ['Extrusion cut double saw','Saw Cycle Time',' ' ],
    'body_a' : ['BA STATUS', 'BA Time','ToDo' ],
    'welding' : ['Welding Corners','Welding Time', 'ToDo'] ,
    'punch': ['Punch Holes', 'Punching Cycle Time',  'ToDo'],

    }
    cnc_condition = ['CNC Holes', 'Asymmetric (CNC)', 'CNC Controls']
    #sequence = ['saw', 'mill', 'punch', 'welding', 'body_a', 'lens']
    
    fields_input = {
        'Order': 'Order', 
        'Line': 'Line',
        'Status': 'Status', 
        'Priority': 'Sched Date Priority', 
        'Ship_date': 'Scheduled Ship Date',
        'SD': 'SD vs Bom'
        }
    status_rank = {
        'Wiring Started': 1,
        'Machine Shop Finished' : 2,
        'Machine Shop Started': 3,
        'Scheduled/Released': 4

        }
    good_status = [
        'Wiring Started',
        'Machine Shop Finished',
        'Machine Shop Started',
        'Scheduled/Released'
        ]
  

class machine_scheduling():
    today = 0
    SORT_ORDER = {}
    map_order ={}
    solution_machining = []
    
    @classmethod
    def extract_data(cls,machining_input):
        good_status = [
        'Wiring Started',
        'Machine Shop Finished',
        'Machine Shop Started',
        'Scheduled/Released'
        ]
        SORT_ORDER = {}
        sequence = ['saw', 'mill', 'punch', 'welding', 'body_a', 'lens']
        for index, i in enumerate(sequence):
                cls.SORT_ORDER[i] = index
        fields = ['Order', 'Line', 'Status', 'Scheduled Ship Date', 'SD vs Bom', 'Saw Cycle Time', 'Welding Time', 'Lens Cycle Time'
                  ,'Extrusion cut double saw' , 'BA STATUS', 'MSLens', 'Welding Corners', 'CNC Holes', 'Asymmetric (CNC)', 'CNC Controls',
                  'Punching Cycle Time', 'CNC Cycle Time', 'BA Time', 'Punch Holes']
        index = 0
        for index, row in machining_input.iterrows():
            if row['SD vs Bom'] == True and row['Status'] in good_status:
                if row['Order'] not in cls.map_order :
                    ord = order(row['Order'])
                    setattr(ord, 'status', sub_order.status_rank[row['Status']])
                    cls.map_order[int(row['Order'])] = ord
                sub = sub_order(row['Line'])
                for value in fields:
                    try:
                        setattr(sub, value, int(row[value]))
                    except:
                        setattr(sub, value, row[value])
                for i in sequence:
                    if i in sub.machine_status_dict and not pd.isna(getattr(sub,sub.machine_status_dict[i][1])):
                        if i == 'saw' and pd.isna( getattr(sub,sub.machine_status_dict[i][0]) ):
                           setattr(sub, i,math.ceil(float(getattr(sub,sub.machine_status_dict[i][1]))))
                           if math.ceil(float(getattr(sub,sub.machine_status_dict[i][1]))) > 0 : 
                                sub.sequence.append(cls.SORT_ORDER[i])
                  
                        elif getattr(sub,sub.machine_status_dict[i][0]) ==sub.machine_status_dict[i][2] :
                            setattr(sub, i,math.ceil(float(getattr(sub,sub.machine_status_dict[i][1]))))
                            if math.ceil(float(getattr(sub,sub.machine_status_dict[i][1]))) > 0 : 
                                sub.sequence.append(cls.SORT_ORDER[i])
                        else: setattr(sub,i , 0)
                try: 
                    if getattr(sub,'MSLens') == 'ToDo' and not pd.isna(getattr(sub,'Lens Cycle Time')): 
                        setattr(sub, 'lens', math.ceil(float(getattr(sub,'Lens Cycle Time'))))
                        if math.ceil(float(getattr(sub,'Lens Cycle Time'))) > 0: 
                            sub.sequence.append(cls.SORT_ORDER['lens'])
                except  TypeError:
                    setattr(sub, 'lens', 0)
                for i in sub.cnc_condition:
                    if getattr(sub,i) == 'ToDo' :
                        try:
                            setattr(sub, 'mill', math.ceil(float(getattr(sub,'CNC Cycle Time'))))
                            if math.ceil(float(getattr(sub,'CNC Cycle Time'))) > 0 :
                                sub.sequence.append(cls.SORT_ORDER['mill'])
                        except ValueError:
                            pass
                        break
                    else: 
                        setattr(sub, 'mill',0)
        
        
            sub.sequence.sort()
            cls.map_oder_input_machinig(sub)
            index = index + 1
        
        print('file input sucessfully')
        return 1
    @classmethod
    def map_oder_input_machinig(cls,sub):
        if sub not in cls.map_order[sub.Order].sections:
            cls.map_order[sub.Order].add_section(sub)
            if int(sub.status_rank[sub.Status]) <  int(cls.map_order[sub.Order].status):
               cls.map_order[sub.Order].status = sub.status_rank[sub.Status]
    @classmethod
    def read_data_excel(cls,filename, today, sheet):
        
        formatter_string = "%d.%m.%Y" 
        today = pd.to_datetime(today, format=formatter_string)
        cls.today = today
        try:
            data_file = pd.read_excel(filename, sheet_name=sheet)
        except FileNotFoundError:
            print('Invalid file input or file does not exist, please check again')
            return 0
        cls.extract_data(data_file)
        return 1
    @classmethod
    def generate_machining_schedule(cls):
        maching_orders = []
        for i in range(3,5):
        
            for keys, values in cls.map_order.items():
                if values.status == i:
                    maching_orders.append(values)
        print("Number of Order to machine are: {}".format( len(maching_orders)))
        cls.MachineShopScheduling(maching_orders)
        cls.solution_machining.extend( maching_orders)
        maching_orders.clear()

    @classmethod
    def MachineShopScheduling(cls,all_orders):
        sequence = ['saw', 'mill', 'punch', 'welding', 'body_a', 'lens']
    
 
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
                                    start_var = model.NewIntVar(0,horizon,'start_%i_%i_%i' %(o.ID,s.Line, task_id))
                                    duration = math.ceil (getattr(s,attr))
                                    end_var = model.NewIntVar(0,horizon,'end_%i_%i_%i' %(o.ID,s.Line, task_id))
                                    interval_var = model.NewIntervalVar(start_var,duration,end_var,'interval_%i_%i_%i'%(o.ID,s.Line,task_id))  
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

    @classmethod
    def output_machine(cls,file_output, today): 
        output = ['number', 'Status']
        seq = ['saw', 'mill', 'punch', 'welding', 'body_a', 'lens']
        output.extend(seq)
        line = []
        today = datetime.strptime( today,"%d.%m.%Y" )
        try:
                sequence = ['Saw', 'Mill', 'Punch', 'Welding', 'Body Assemly', 'Lens']
                ofile= open(file_output,"w")
                line = ['Order,Line , Status,']
                for i in sequence:
                    line += i
                    line += ' Date '
                    line += ','
                    line += i
                    line += ' Time '
                    line += ','
                line +='\n'
                line = ''.join(line)
                #ofile.write(line)
        except PermissionError:
                print('Please close the file output.csv and return the program')
                ans = input("Press any button to exit")
                exit()
        #useage_after = useage.fromkeys(capacity_machine, 0)
        for o in cls.solution_machining:
            for s in o.sections:
                line += str( o.ID)
                line += ','
                line += str( s.Line)
                line += ','
                line += str( o.status)
                line += ','
                day_now = 0
                for attr in seq:
                    
                    try:
                        if getattr(s,attr) > 0:
                            day = math.floor(s.start[attr]/ (60*7*3))
                            minute = s.start[attr] - day*60*7*3
                            if day_now == 0:
                                day_now = day
                            line +=  str(today + timedelta( days = day_now) + timedelta(minutes = minute))
                            day_now = day_now + 1
                            line +=  str(day)
                            line += ','
                            line += str(getattr(s,attr))
                            line += ','
                        else:
                            line += '-'
                            line += ','
                            line += '-'
                            line += ','
                    except AttributeError:
                            line += '-'
                            line += ','
                            line += '-'
                            line += ','
                line += "\n"
        line = ''.join(line)
        ofile.write(line)
    
#machine_scheduling.read_data_excel("machine_input.xlsx","1.1.2019",'Data')


def main():
    machine_scheduling.read_data_excel("machine_new_sample.xlsx","1.1.2019","Sheet3")
    #machine_scheduling.read_data_csv('machine_input.csv', '10.10.2019')
    machine_scheduling.generate_machining_schedule()
    machine_scheduling.output_machine('output.csv',"1.1.2019")
def generate_machine_schedule(file, today):
    machine_scheduling.read_data_excel(file,today,'Data')
    machine_scheduling.generate_machining_schedule()
    machine_scheduling.output_machine('output.csv',today)

    #machine_scheduling.read_data_csv(file, today)
    #machine_scheduling.MachineShopScheduling()
    #machine_scheduling.output_machine('output.csv',today)

if __name__ == "__main__":
    main()