from __future__ import print_function
import pandas as pd
import collections
import random 
import math
from machining import MachineShopScheduling, AssemblyScheduling, best_fit
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

try:
    f= open("output.csv","a")
    f.write('Order, Assigned Group, Start Date, Start Time, Finish day, Finish time, Assembly Time, Status \n')
except PermissionError:
    print('Please close the file output.csv and return the program')
    ans = input("Press any button to exit")
    exit()


all_sections = []
map_order = {}
solution ={}

def map_oder_input(sub):
    map_order[sub.Order].add_section(sub)
    try:
        map_order[sub.Order].a_time += math.ceil(getattr(sub,'Real Time'))
    except TypeError or ValueError :
         pass
def read_data_assembly(filename):
    
#order_input = pd.read_csv('order_input.csv')
    fields = ['Order', 'Line', 'Status', 'Sched. Ship Date',
             'Real Status' , 'Real Time', 'Promised' , 'ISSUE','Missing Materials', 'Production Group' ]
    #section_input = pd.read_csv("Axis-Assembly-Input.csv", skiprows = 1)
    try:
        assembly_input = pd.read_csv(filename, skipinitialspace=True, usecols=fields)
    except FileNotFoundError:
        print('Invalid file input or file does not exist, please check again')
        return 0
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
            if int(sub.Status) :
                map_oder_input(sub)
    return 1

    
capacity = {
    1: 21, 
    4: 21,
    7: 21,
    10: 14, 
    12: 14,
    15: 14,
    18: 14

    
}

useage= {
    1: 0, 
    4: 0,
    7: 0,
    10: 0, 
    12: 0,
    15: 0, 
    18: 0
    }
def assign_date(assembly_orders,file_output,type):
        
    output = ['number', 'group', 'start_day', 'start', 'finish_day', 'finish', 'a_time', 'Status']
    line = []
    if type == 'generate':
        for o in assembly_orders:
            assembly_orders.sort(key = attrgetter('group', 'start'), reverse=False)
            value = math.floor((o.start)/ (60*capacity[o.group]))
            setattr(o, 'start_day', value )
            value = math.floor((o.finish) / (60*capacity[o.group]))
     
            setattr(o, 'finish_day', value )
            
            solution[o.number] = o
            useage[o.group] = useage[o.group] +  o.a_time
            for i in output:
                line += str(getattr(o,i))
                line += ","   
            line += "\n"
            line = ''.join(line)
        file_output.write(line)
    else:
        for key, o in assembly_orders.items():
            value = math.floor((o.start)/ (60*capacity[o.group]))
            setattr(o, 'start_day', value )
            value = math.floor((o.finish) / (60*capacity[o.group]))
     
            setattr(o, 'finish_day', value )
            for i in output:
                line += str(getattr(o,i))
                line += ","   
            line += "\n"
            line = ''.join(line)
        file_output.write(line)


        
     
       

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
              #ord.qualified_group = getattr(ord.sections[0],'Production Group')
              if(ord.Status == 1):
                  ord.qualified_group = foo[0]
              else:
                ord.qualified_group = foo[: random.randint(1, 4)]
        print("Number of Order with assembly status {} is {} ".format(i, len(assembly_orders)))
        if len(assembly_orders) > 0:
            AssemblyScheduling(assembly_orders, useage)
            assign_date(assembly_orders,f,'generate')
        assembly_orders.clear()
    print("fnish")



#read_data_assembly()
#generate_assembly_schedule()
##best_fit(solution, useage)
#print('finish')

def main():
    while(1):
        choice = input("Please enter 1 for assembly and 2 for machine shop scheduling:  ")
        if choice == '1':
            filename = input("Please enter assembly input file name in .csv format:  ")

            if read_data_assembly(filename) :
                generate_assembly_schedule()
                print(useage)
                best_fit(solution, useage)
                assign_date(solution,f,'iterate')
                print(useage)
                f.write('after \n')

            break
        elif choice == '2':
            print('Feature is not developed yet.')
            break
        else: print("Wrong choice, please enter 1 or 2 only")

if __name__ == "__main__":
    main()



