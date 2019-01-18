from __future__ import print_function
import pandas as pd
import collections
import random 
import math
from machining import MachineShopScheduling, AssemblyScheduling
import time
from operator import attrgetter


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

f= open("output.csv","a")
f.write('Order, Assigned Group, Start Date, Start Time, Finish day, Finish time, Assembly Time \n')


all_sections = []
map_order = {}


def map_oder_input(sub):
    map_order[sub.Order].add_section(sub)
    map_order[sub.Order].a_time += math.ceil(getattr(sub,'Real Time'))
def read_data_assembly():
    
#order_input = pd.read_csv('order_input.csv')
    fields = ['Order', 'Line', 'Status', 'Sched. Ship Date',
             'Real Status' , 'Real Time', 'Promised' , 'ISSUE','Missing Materials' ]
    #section_input = pd.read_csv("Axis-Assembly-Input.csv", skiprows = 1)
    assembly_input = pd.read_csv("Schedule-10.01.2019.csv", skipinitialspace=True, usecols=fields)
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
        if(row['Status'] in status_rank and row['ISSUE'] in good_value):
            if(row['Order'] not in map_order):
                ord = order(row['Order'])
                map_order[row['Order']] = ord
            sub = sub_order(index)
            
            for value in fields:
                setattr(sub, value, row[value])
            setattr(sub, 'priority', priority_rank[sub.Promised])
     
            if status_rank[sub.Status] == 1 :
                sub.Status = 1
            elif status_rank[sub.Status] == 2:
                if getattr(sub,'Missing Materials') in good_value:
                    sub.Status = 2   
                elif getattr(sub,'Missing Materials') == '+Cartridge':
                    sub.Status = 3
                else :sub.Status = 7
            elif status_rank[sub.Status] == 3:
                if getattr(sub,'Missing Materials') == '+lens':
                    sub.Status = 4     
                if getattr(sub,'Missing Materials') == 'Material+Cartridge':
                    sub.Status = 5  
                if getattr(sub,'Missing Materials') == 'Material+lens+Cartridge+Housing':
                    sub.Status = 6
                else :sub.Status = 7
            else :sub.Status = 7
            map_oder_input(sub)

    

#number_of_orders = len(order_input)
capacity = {
    1: 21, 
    4: 21,
    7: 21,
    10: 14, 
    12: 14

    
}

useage= {
    1: 0, 
    4: 0,
    7: 0,
    10: 0, 
    12: 0
    }
def assign_date(assembly_orders,f, status):
    assembly_orders.sort(key = attrgetter('group', 'start'), reverse=False)
    output = ['number', 'group', 'start_day', 'start', 'finish_day', 'finish', 'a_time']
    line = []
    for o in assembly_orders:
        #if(status > 1):
        #    o.start = o.start + useage[o.group]
        #    o.finish = o.start + o.a_time
        value = math.floor((o.start)/ (60*capacity[o.group]))
        setattr(o, 'start_day', value )
        value = math.floor((o.finish) / (60*capacity[o.group]))
     
        setattr(o, 'finish_day', value )
        useage[o.group] = useage[o.group] +  o.a_time
        for i in output:
            line += str(getattr(o,i))
            line += ","    
        line += "\n"
        line = ''.join(line)
    f.write(line)
        
        #print (s.start[m], s.finish[m])
       

def generate_assembly_schedule():
    assembly_orders = []
    for i in range(1,7):
        for index, ord in map_order.items():
              num = []
              [num.append(s.Status) for s in ord.sections]
              setattr(ord, 'Status', max(num))
              if ord.Status == i :
                  assembly_orders.append(ord)
              foo = [1,4,7,10,12]
              random.shuffle(foo)
              if(ord.Status == 1):
                  ord.qualified_group = foo[0]
              else:
                ord.qualified_group = foo[: random.randint(1, 4)]
        print("Number of Order with assembly status {} is {} ".format(i, len(assembly_orders)))
        if len(assembly_orders) > 0:
            AssemblyScheduling(assembly_orders)
            assign_date(assembly_orders,f, i)
        assembly_orders.clear()
    print("fnish")



read_data_assembly()
generate_assembly_schedule()
print('finish')




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