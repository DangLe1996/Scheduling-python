from __future__ import print_function
import pandas as pd
import collections
import random 
import math
from machining import MachineShopScheduling, AssemblyScheduling
import time



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
        self.start = []
        self.finish = []
     def update_time(self,attr, task_type):
        self.tasks[attr] = task_type
       

assembly_orders = []
all_sections = []
map_order = {}
def read_data_assembly():
    
#order_input = pd.read_csv('order_input.csv')
    fields = ['Order', 'Line', 'Status', 'Sched. Ship Date',
             'Real Status' , 'Real Time', 'Promised' ,'Missing Materials' ]
    #section_input = pd.read_csv("Axis-Assembly-Input.csv", skiprows = 1)
    assembly_input = pd.read_csv("Axis-Assembly-Input.csv", skipinitialspace=True, usecols=fields)
    priority_rank = {
    'High Priority': 1,
    'Priority' : 2,
    'Regular': 3

    }
    status_rank = {
        'Wiring Started': 1,
        'Machine Shop Finished' : 2,
        'Scheduled/Released': 3, 
        'Machine Shop Started': 4

        }
    for index, row in assembly_input.iterrows():
        if(row['Status'] in status_rank):
            if(row['Order'] not in map_order):
                ord = order(row['Order'])
                map_order[row['Order']] = ord
            sub = sub_order(index)
            for value in fields:
                setattr(sub, value, row[value])
            setattr(sub, 'priority', priority_rank[sub.Promised])
            sub.Status = status_rank[sub.Status]
            map_order[sub.Order].add_section(sub)
            map_order[sub.Order].a_time += math.ceil(getattr(sub,'Real Time'))

    

#number_of_orders = len(order_input)


def generate_assembly_schedule(args):
    for i in range(1,3):
        for index, value in map_order.items():
              num = []
              [num.append(s.Status) for s in value.sections]
              setattr(value, 'Status', max(num))
              if value.Status == i :
                  assembly_orders.append(value)
              foo = [1,2,3,4]
              random.shuffle(foo)
              value.qualified_group = foo[: random.randint(1, 4)]
        AssemblyScheduling(assembly_orders)
        assembly_orders.clear()
    print("fnish")
   
read_data_assembly()
generate_assembly_schedule()

#map_section = {}
#dict_order_attribute = {
   
#    'status' : 'Status',
#    'priority' : 'Priority',
#    'duedate' : 'Duedate',
#    'quantity': 'Quantity',
#    'issue' : 'Issue', 
#    'ca': 'Cartidge Available?',
#    'cr': 'Cartridge Required?',
#    'lens': 'Lens', 
#    'body_a' : 'Body Assembly',
#    'saw': 'Saw Finished'
#    }

#sequence_attribute = ['mill', 'punch', 'welding', 'house_a', 'lens_cut', 'lens_a', 'manu', 'assembly']
#sequence_input = ['Milling', 'Punching', 'Welding', 'Housing Assembly', 'Lens Cut'
#                  , 'Lens Assembly', 'Manufacturing', 'Final Assembly']


#dict_sub_order_attribute = {
#    'section': 'Section',
#    }
#for i in range(len(sequence_input)):
#    dict_sub_order_attribute[sequence_attribute[i] + '_qty'] = sequence_input[i] +' Quantity'
#    dict_sub_order_attribute[sequence_attribute[i] + '_time'] = sequence_input[i] +' Time'
#groups = ['Group 1', 'Group 2', 'Group 3', 'Group 4']
#sequence = ['mill', 'punch', 'welding', 'house_a', 'lens_cut', 'lens_a', 'manu']

#for index, row in order_input.iterrows():
#    s = order(row['Order'])
#    for key, value in dict_order_attribute.items():
#        if(str.isdigit(str(row[value]))):
#            setattr(s, key, int(row[value]))
#        else: setattr(s, key, row[value])
#    for g in groups:
#        if(row[g] > 0):
#           s.set_group(int(row[g]))
#    all_orders.append(s)
#    map_order[int(row['Order'])] = s
   



#for index, row in section_input.iterrows():
#    sub = sub_order(int(row['Order']))
#    for i in range(len(sequence_input)):
#        setattr(sub, sequence_attribute[i] + '_total_time', (int(row[sequence_input[i] +' Quantity'] * row[sequence_input[i] +' Time'] )))
#    for key, value in dict_sub_order_attribute.items():
#        setattr(sub, key, int(row[value]))
#    map_order[int(row['Order'])].add_section(sub)
#    all_sections.append(sub)
    

#jobs_data = []
#allowed_status = ['Machine Shop Started', 'Machine Shop Not Started']
#for s in all_sections:
#   job = []
 
#   for index, attr in enumerate(sequence): #enumerator
#        task = []
#        task.append(index)
#        task.append(getattr(s,attr))
#        job.append(task)
       
#   jobs_data.append(job) 


#if(MachineShopScheduling(all_orders)):

#    f= open("output.txt","w+")

#    for o in all_orders:
#        if o.status in allowed_status:
#            f.write("%d ," % o.number)
#            #print(o.number)
#            for s in o.sections:
#                f.write("%d ," %s.section)
#                #print(s.section)
#                for m in range(len(sequence)):
#                    f.write("%d, " %(s.start[m] ))
#                    f.write("%d, " %( s.finish[m]))
#                    #print (s.start[m], s.finish[m])
#                f.write(" \n")
#                input("Press enter to exit ;)")
            
#for i in range( len(sequence)):
#    print(sequence[i])
#    for o in all_orders:
#        for s in o.sections:
#                print (o.number, s.section, s.start[i], s.finish[i])
    


#MinimalJobshopSat(jobs_data, all_orders)