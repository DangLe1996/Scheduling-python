from __future__ import print_function
import pandas as pd
import collections
from machining import MinimalJobshopSat, MachineShopScheduling


order_input = pd.read_csv('order_input.csv')
section_input = pd.read_csv("section_input.csv", skiprows = 1)
number_of_orders = len(order_input)

class order():
    def __init__(self, number, priority, duedate, status, a_time):
        self.sections = []
        self.number = number
        self.priority = priority
        self.duedate = duedate
        self.status = status
        self.a_time = a_time
        self.qualified_group = []
    def set_group(self,group):
        self.group = group
    def add_section(self,value):
        self.sections.append(value)
        self.a_time += value.final_a
    def update_time(self, start, finish, interval):
        self.start = start
        self.finish = finish

class sub_order():
  
     def __init__(self, order_number, section, mill, punch, welding, house_a, lens_cut, lens_a, manu, final_a):
        self.order_number = order_number
        self.section = section
        self.mill = mill
        self.punch = punch
        self.welding = welding
        self.house_a = house_a
        self.lens_cut = lens_cut
        self.lens_a = lens_a
        self.manu = manu
        self.final_a = final_a
        self.tasks = {}
        self.start = []
        self.finish = []
     def update_time(self,attr, task_type):
        self.tasks[attr] = task_type
       




all_orders = []
all_sections = []
map_order = {}
map_section = {}
#dict_order_attribute{
#    'mill' : 
#    }
sequence = ['mill', 'punch', 'welding', 'house_a', 'lens_cut', 'lens_a', 'manu']

for index, row in order_input.iterrows():
    #print(row['Unnamed: 7'])
    all_orders.append(order(int(row['Order']), int(row['Priority']), int(row['Duedate']), row['Status'], int(row['Assembly Time'])))
    map_order[int(row['Order'])] = all_orders[-1]



for index, row in section_input.iterrows():
    sub = sub_order(int(row['Order']),int(row['Section']),int(row['Milling']),
                                                       int(row['Punching']),int(row['Welding']),int(row['Housing Assembly']),
                                                       int(row['Lens Cut']),int(row['Lens Assembly']) 
                                                       ,int(row['Manufacturing parts']),int(row['Final Assembly']))
    all_sections.append(sub)
    
    map_order[int(row['Order'])].sections.append(sub)
    #print(map_order[int(row['Order'])])

    #map_section[int(row['Section'])] = int(row['Order'])
    #print(row)

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
            
#for i in range( len(sequence)):
#    print(sequence[i])
#    for o in all_orders:
#        for s in o.sections:
#                print (o.number, s.section, s.start[i], s.finish[i])
    


#MinimalJobshopSat(jobs_data, all_orders)