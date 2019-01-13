from __future__ import print_function
import pandas as pd
import collections
from machining import MachineShopScheduling
import time

order_input = pd.read_csv('order_input.csv')
section_input = pd.read_csv("section_input.csv", skiprows = 1)
number_of_orders = len(order_input)

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
  
     def __init__(self, order_number):
        self.order_number = order_number
        self.tasks = {}
        self.start = []
        self.finish = []
     def update_time(self,attr, task_type):
        self.tasks[attr] = task_type
       

all_orders = []
all_sections = []
map_order = {}
map_section = {}
dict_order_attribute = {
   
    'status' : 'Status',
    'priority' : 'Priority',
    'duedate' : 'Duedate',
    'quantity': 'Quantity',
    'issue' : 'Issue', 
    'ca': 'Cartidge Available?',
    'cr': 'Cartridge Required?',
    'lens': 'Lens', 
    'body_a' : 'Body Assembly',
    'saw': 'Saw Finished'
    }

sequence_attribute = ['mill', 'punch', 'welding', 'house_a', 'lens_cut', 'lens_a', 'manu', 'assembly']
sequence_input = ['Milling', 'Punching', 'Welding', 'Housing Assembly', 'Lens Cut'
                  , 'Lens Assembly', 'Manufacturing', 'Final Assembly']


dict_sub_order_attribute = {
    'section': 'Section',
    }
for i in range(len(sequence_input)):
    dict_sub_order_attribute[sequence_attribute[i] + '_qty'] = sequence_input[i] +' Quantity'
    dict_sub_order_attribute[sequence_attribute[i] + '_time'] = sequence_input[i] +' Time'
groups = ['Group 1', 'Group 2', 'Group 3', 'Group 4']
sequence = ['mill', 'punch', 'welding', 'house_a', 'lens_cut', 'lens_a', 'manu']

for index, row in order_input.iterrows():
    s = order(row['Order'])
    for key, value in dict_order_attribute.items():
        if(str.isdigit(str(row[value]))):
            setattr(s, key, int(row[value]))
        else: setattr(s, key, row[value])
    for g in groups:
        if(row[g] > 0):
           s.set_group(int(row[g]))
    all_orders.append(s)
    map_order[int(row['Order'])] = s
   



for index, row in section_input.iterrows():
    sub = sub_order(int(row['Order']))
    for i in range(len(sequence_input)):
        setattr(sub, sequence_attribute[i] + '_total_time', (int(row[sequence_input[i] +' Quantity'] * row[sequence_input[i] +' Time'] )))
    for key, value in dict_sub_order_attribute.items():
        setattr(sub, key, int(row[value]))
    map_order[int(row['Order'])].add_section(sub)
    all_sections.append(sub)
    

jobs_data = []
allowed_status = ['Machine Shop Started', 'Machine Shop Not Started']
#for s in all_sections:
#   job = []
 
#   for index, attr in enumerate(sequence): #enumerator
#        task = []
#        task.append(index)
#        task.append(getattr(s,attr))
#        job.append(task)
       
#   jobs_data.append(job) 


if(MachineShopScheduling(all_orders)):

    f= open("output.txt","w+")

    for o in all_orders:
        if o.status in allowed_status:
            f.write("%d ," % o.number)
            #print(o.number)
            for s in o.sections:
                f.write("%d ," %s.section)
                #print(s.section)
                for m in range(len(sequence)):
                    f.write("%d, " %(s.start[m] ))
                    f.write("%d, " %( s.finish[m]))
                    #print (s.start[m], s.finish[m])
                f.write(" \n")
            
#for i in range( len(sequence)):
#    print(sequence[i])
#    for o in all_orders:
#        for s in o.sections:
#                print (o.number, s.section, s.start[i], s.finish[i])
    


#MinimalJobshopSat(jobs_data, all_orders)