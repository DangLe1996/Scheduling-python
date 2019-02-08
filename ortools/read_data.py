from __future__ import print_function
import pandas as pd
import collections
import random 
import math
#from machining import MachineShopScheduling, AssemblyScheduling, best_fit
import time
from operator import attrgetter
from datetime import datetime,date, timedelta 

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
   

class sub_order(order):
  
     def __init__(self, index ):
        #self.order_number = order_number
        #self.line = line
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
    'Wiring Started': 1,
    'Machine Shop Finished' : 2,
    'Machine Shop Started': 3,
    'Scheduled/Released': 4

    }
capacity = {
    #1: 21, 
    #4: 21,
    #7: 21,
    #10: 14, 
    #12: 14,
    #15:14, 
    #18:14

    
}
all_sections = []
map_order = {}
solution =[]
solution_machining = []
def map_oder_input(sub):
    if sub not in map_order[sub.ID].sections:
        if map_order[sub.ID].priority > priority_rank [getattr(sub,'Promised')] :
            map_order[sub.ID].priority = priority_rank [getattr(sub,'Promised')]
        map_order[sub.ID].add_section(sub)
        try:
            map_order[sub.ID].a_time += math.ceil(float(getattr(sub,'Real Time')))
        except TypeError or ValueError :
             pass

def map_oder_input_machinig(sub):
    if sub not in map_order[sub.Order].sections:
        map_order[sub.Order].add_section(sub)
        if status_rank[sub.Status] <  map_order[sub.Order].status:
           map_order[sub.Order].status = sub.Status


machine_status_dict = {
    'saw' : ['Extrusion cut double saw','Saw Cycle Time',False  ],
    'body_a' : ['BA Status', 'HousingCycle Time',False ],
    'welding' : ['Welding Status','Welding Cycle Time', 'ToDo'] ,
    'punch': ['Punching Required', 'Puching Cycle time',  3],
    #'mill': ['Milling Required', 'Milling Cycle time', 2]
    }

cnc_condition = ['CNC Holes', 'CNC MR', 'CNC Controls']
sequence = ['saw', 'mill', 'punch', 'welding', 'body_a', 'lens']
def read_data_machine(filename):
    SORT_ORDER = {}
   
    
    for index, i in enumerate(sequence):
            SORT_ORDER[i] = index
    fields = ['Order', 'Line', 'Status', 'Scheduled Ship Date', 'SD vs BOM', 'Saw Cycle Time', 'Welding Cycle Time', 'Lens Cycle Time'
              ,'Extrusion cut double saw' , 'BA Status', 'MSLens', 'Welding Status', 'CNC Holes', 'CNC MR', 'CNC Controls',
              'Puching Cycle time', 'Milling Cycle time', 'HousingCycle Time', 'Punching Required']
            
    try:
        machining_input = pd.read_csv(filename, skipinitialspace=True, usecols=fields)
    except FileNotFoundError:
        print('Invalid file input or file does not exist, please check again')
        return 0
   
    index = 0
    for index, row in machining_input.iterrows():
        if row['SD vs BOM'] == True :
            if(row['Order'] not in map_order):
                ord = order(row['Order'])
                setattr(ord, 'status', status_rank[row['Status']])
                map_order[row['Order']] = ord
            sub = sub_order(row['Line'])
            for value in fields:
                setattr(sub, value, row[value])
            for i in sequence:
                if i in machine_status_dict:
                    if getattr(sub,machine_status_dict[i][0]) ==machine_status_dict[i][2] :
                        setattr(sub, i,math.ceil(float(getattr(sub,machine_status_dict[i][1]))))
                        if math.ceil(float(getattr(sub,machine_status_dict[i][1]))) > 0 : 
                            sub.sequence.append(SORT_ORDER[i])
                    else: setattr(sub,i , 0)
            try: 
                if math.isnan(getattr(sub,'MSLens'))  :
                    setattr(sub, 'lens', math.ceil(float(getattr(sub,'Lens Cycle Time'))))
                    if math.ceil(float(getattr(sub,'Lens Cycle Time'))) > 0: 
                        sub.sequence.append(SORT_ORDER['lens'])
            except  TypeError:
                setattr(sub, 'lens', 0)
            for i in cnc_condition:
                if getattr(sub,i) == 'Ready' :
                    try:
                        setattr(sub, 'mill', math.ceil(float(getattr(sub,'Milling Cycle time'))))
                        if math.ceil(float(getattr(sub,'Milling Cycle time'))) > 0 :
                            sub.sequence.append(SORT_ORDER['mill'])
                    except ValueError:
                        pass
                    break
                else: 
                    setattr(sub, 'mill',0)
        formatter_string = "%m/%d/%Y" 
        datetime_object = datetime.strptime(getattr(sub,'Scheduled Ship Date'), formatter_string)
        setattr(sub,'ship_date', datetime_object.date())
        sub.sequence.sort()
        map_oder_input_machinig(sub)
        index = index + 1
        
    print('File input sucessfully')
    return 1






def read_data_assembly(filename, today):

    
#order_input = pd.read_csv('order_input.csv')
    fields = ['Order', 'Line', 'Status', 'Sched. Ship Date',
             'Real Status' , 'Real Time', 'Promised' , 'ISSUE','Missing Materials', 'Production Group', 'Complete/Partial' ]
    #section_input = pd.read_csv("Axis-Assembly-Input.csv", skiprows = 1)
    try:
        assembly_input = pd.read_csv(filename, skipinitialspace=True, usecols=fields)
        capacity_input = pd.read_csv('capacity.csv', skipinitialspace=True)
    except FileNotFoundError:
        print('Invalid file input or file does not exist, please check again')
        return 0
    #print("{} and  {} ".format(assembly_input['Production Group'], assembly_input['Order']))
    try:
        d_file= open("debug.csv","w")
        status_7= open("status_7.csv","w")
        status_7.write('Order, Line, Status, Promised, Scheduled Ship Date, Issue, Missing Materials \n')
        d_file.write('Order, Line, Status, Promised, Scheduled Ship Date, Issue, Missing Materials \n')
    except PermissionError:
        print('Please close the file debug.csv and return the program')
        ans = input("Press any button to exit")
        exit()
    for index, row in capacity_input.iterrows():
       capacity[row["Group"]] = row["Capacity"]
    dbug_value = ['Order', 'Line','Status','Promised', 'Sched. Ship Date', 'ISSUE','Missing Materials', 'Complete/Partial'  ]
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
    line = []
    bad_orders = []
    good_value = ['0', float('NaN')]
    for index, row in assembly_input.iterrows():
        if row['Order'] not in bad_orders:
            if not ( row['Status'] in status_rank and row['Complete/Partial'] == 'Complete' and  (pd.isnull(row['ISSUE']) or row['ISSUE'] == '0')):
                bad_orders.append(row['Order'])
                for i in dbug_value:
                    line += str(row[i])
                    line +=','
                line += '\n' 
        elif row['Order'] in bad_orders:
            if not ( row['Status'] in status_rank and row['Complete/Partial'] == 'Complete' and  (pd.isnull(row['ISSUE']) or row['ISSUE'] == '0')):
                bad_orders.append(row['Order'])
                for i in dbug_value:
                    line += str(row[i])
                    line +=','
                line += '\n' 
    line = ''.join(line)
    d_file.write(line)


    for index, row in assembly_input.iterrows():
        if row['Order'] not in bad_orders:
            try:
                r = float(row['Real Time'])
                #if(row['Status'] in status_rank and row['ISSUE'] in good_value ): and row['Complete/Partial'] == 'Complete'
                #and  (pd.isnull(row['ISSUE']) or row['ISSUE'] == 0) and row['Complete/Partial'] == 'Complete'
                if row['Status'] in status_rank and row['Complete/Partial'] == 'Complete'and  (pd.isnull(row['ISSUE']) or row['ISSUE'] == '0'):
                
                    sub = sub_order(index)
            
                    for value in fields:
                        setattr(sub, value, row[value])
                    setattr(sub, 'priority', priority_rank[sub.Promised])
                    formatter_string = "%d.%m.%Y" 
                    datetime_object = datetime.strptime(getattr(sub,'Sched. Ship Date'), formatter_string)
                    setattr(sub,'ship_date', datetime_object.date())
                    setattr(sub,'real_stat', sub.Status)
                    setattr(sub,'delta', (datetime_object - today).days)
                    value = [0,(datetime_object - today).days]
                    ID = int(str(int(row['Order'])) + str(max(value)))
                    if(ID not in map_order):
                        ord = order(ID)
                        setattr(ord, 'priority', 5)
                        map_order[ID] = ord
                    setattr(sub,'ID', ID )
                    setattr(sub, 'group', getattr(sub,'Production Group'))
                    if status_rank[sub.Status] == 1 :
                        sub.Status = 1
                    elif status_rank[sub.Status] == 2:
                        try:
                            if pd.isnull(row['Missing Materials']):
                                sub.Status = 2  
                            
                            elif getattr(sub,'Missing Materials') == '=+Cartridge':
                                sub.Status = 3

                            else :sub.Status = 7
                        except TypeError:
                            sub.Status = 7
                    elif status_rank[sub.Status] == 3:
                        if getattr(sub,'Missing Materials') == '=+lens' or pd.isnull(row['Missing Materials']):
                            sub.Status = 4   
                        
                        elif getattr(sub,'Missing Materials') == 'Material+Cartridge':
                            sub.Status = 5  
                        
                        elif getattr(sub,'Missing Materials') == 'Material+lens+Cartridge+Housing':
                            sub.Status = 6
                        
                        else :sub.Status = 7
                    else :sub.Status = 7
                    if int(sub.Status) :
                        map_oder_input(sub)
                #else: 
                #    if row['Order'] not in bad_orders:
                #        if row['Order'] in map_order:
                #            map_order.pop(row['Order'],None)
                #        bad_orders.append(row['Order'])
                #        for i in dbug_value:
                #            line += str(row[i])
                #            line +=','
                #        line += '\n' 
                    #    bad_orders.remove(row['Order'])
                    #else: 
                    #    bad_orders.append(row['Order'])
            except ValueError:
                pass
    line2 = []
    for index, ord in map_order.items():
            num = []
            [num.append(s.Status) for s in ord.sections]
            pri = []
            [pri.append(s.priority) for s in ord.sections]
            setattr(ord, 'Status', max(num))
            setattr(ord, 'delta', ord.sections[0].delta)
            setattr(ord, 'priority', min(pri))
            if ord.Status == 7:
                for s in ord.sections:
                   if s.Status == 7:
                        #print(s.Order)
                        for i in dbug_value:
                            line2 += str(getattr(s,i) )
                            line2 +=','
                        line2 += str(getattr(s,'real_stat'))
                        line2 += '\n'
            if ord.Status < 7:
                setattr(ord, 'group', ord.sections[0].group)
                solution.append(ord)
    line2 = ''.join(line2)
    status_7.write(line2)           
    #line = ''.join(line)
    #d_file.write(line)
    print('File input sucessfully')
    return 1

    


useage= {
    1: 0, 
    4: 0,
    7: 0,
    10: 0, 
    12: 0,
    15:0, 
    18:0
    }
 
capacity_machine= {
    'saw': 60,
    'mill': 37,
    'punch': 7.5,
    'welding': 22.5, 
    'body_a': 30,
    'lens': 52
   
   
    }
def assign_date(assembly_orders,file_output, today):
        
    output = ['Order', 'Line', 'group','start_day', 'finish_day', 'ship_date', 'Real Time', 'Status']
    #output_order = ['start_day', 'finish_day']
    solution.sort(key = attrgetter('group', 'Status','delta', 'priority' ), reverse=False)
    line = []
    useage_after = useage.fromkeys(useage, 0)
    if len(assembly_orders) > 0:
        for o in assembly_orders:
            #o.start = useage_after[o.group]
            #useage_after[o.group]  = useage_after[o.group] +  o.a_time
            #o.finish =  useage_after[o.group]
            #setattr(o, 'start_day', math.floor((o.start)/ (60*capacity[o.group])) )
            #o.start_day = today + timedelta(days=o.start_day)  
            #setattr(o, 'finish_day', math.floor((o.finish)/ (60*capacity[o.group])) )
            #o.finish_day = today + timedelta(days=o.finish_day)
            for s in o.sections:
                s.group = int(s.group)
                start =  useage_after[s.group]
                useage_after[s.group]  = useage_after[s.group] + math.ceil(float(getattr(s,'Real Time')))
                finish =  useage_after[s.group]
                start = math.floor((start)/ (60*capacity[s.group]))
                finish =  math.floor((finish)/ (60*capacity[s.group]))
                s.start_day = today + timedelta(days=start)  
                s.finish_day = today + timedelta(days=finish)  
                for i in output:
                    line += str(getattr(s,i))
                    line += ","   
                line += "\n"
                line = ''.join(line)
        file_output.write(line)
        #print('After heuristic')
        print('Useage per group')
        print(useage_after)

def assign_date_machining(solution,file_output, today):
        
    output = ['number', 'Status']
    output.extend(sequence)
    line = []
    useage_after = useage.fromkeys(capacity_machine, 0)
    for o in solution:
        for s in o.sections:
            line += str( o.number)
            line += ','
            line += str( s.Line)
            line += ','
            line += str( o.status)
            line += ','
            for attr in sequence:
                try:
                    if getattr(s,attr) > 0:
                        line +=  str(today + timedelta( days = math.floor(s.start[attr]/ (60*7*3))))
                        line += ','
                        line += str(s.start[attr])
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
    file_output.write(line)

def assign_date_pre(assembly_orders):
    
    output = ['number', 'group', 'start_day', 'start', 'finish_day', 'finish', 'a_time', 'Status']
    for o in assembly_orders:
        assembly_orders.sort(key = attrgetter('group', 'start'), reverse=False)
        value = math.floor((o.start)/ (60*capacity[o.group]))
        setattr(o, 'start_day', value )
        value = math.floor((o.finish) / (60*capacity[o.group]))
     
        setattr(o, 'finish_day', value )
            
        solution.append( o)
        useage[o.group] = useage[o.group] +  o.a_time
   
def generate_machining_schedule():
    maching_orders = []
    for i in range(3,5):
        
        for keys, values in map_order.items():
            if values.status == i:
                maching_orders.append(values)
    print("Number of Order to machine are: {}".format( len(maching_orders)))
    MachineShopScheduling(maching_orders)
    solution_machining.extend( maching_orders)
    maching_orders.clear()
    
      

def generate_assembly_schedule(f):
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
            assign_date_pre(assembly_orders)
        assembly_orders.clear()

def main():
    #date_entry = input('Enter a date in DD/MM/YYYY format: ')
    date_entry = '02/02/2019'
    today = datetime.strptime( date_entry,"%d/%m/%Y" )
    try:
        ofile= open("assembly output.csv","w")
        ofile.write('Order, Line, Assigned Group, Start Date, Finish day, Ship day, Assembly Time, Status \n')
    except PermissionError:
        print('Please close the file output.csv and return the program')
        ans = input("Press any button to exit")
        exit()
    filename = input("Please enter assembly input file name in .csv format:  ")
    if read_data_assembly(filename, today):
       assign_date(solution,ofile, today)
    
    #while(1):
    #    choice = input("Please enter 1 for assembly and 2 for machine shop scheduling:  ")
    #    date_entry = input('Enter a date in DD/MM/YYYY format: ')
    #    today = datetime.strptime( date_entry,"%d/%m/%Y" )
    #    if choice == '1':
    #        try:
    #            ofile= open("assembly output.csv","w")
    #            ofile.write('Order, Line, Assigned Group, Start Date, Finish day, Ship day, Assembly Time, Status \n')
    #        except PermissionError:
    #            print('Please close the file output.csv and return the program')
    #            ans = input("Press any button to exit")
    #            exit()
    #        filename = input("Please enter assembly input file name in .csv format:  ")
    #        if read_data_assembly(filename, today):
    #            #generate_assembly_schedule(ofile)
    #            #print('Before Heuristic')
    #            #print(useage)
    #            ##assign_date(solution,ofile, today)
    #            #best_fit(solution, useage)
    #            assign_date(solution,ofile, today)
    #        break
        #elif choice == '2':
        #    try:
        #        seq = ['Saw', 'Mill', 'Punch', 'Welding', 'Body Assemly', 'Lens']
        #        ofile= open("machining output.csv","w")
        #        line = ['Order,Line , Status,']
        #        for i in sequence:
        #            line += i
        #            line += ' Date '
        #            line += ','
        #            line += i
        #            line += ' Time '
        #            line += ','
        #        line +='\n'
        #        line = ''.join(line)
        #        ofile.write(line)
        #    except PermissionError:
        #        print('Please close the file output.csv and return the program')
        #        ans = input("Press any button to exit")
        #        exit()
        #    filename = input("Please enter assembly input file name in .csv format: ")
        #    if read_data_machine(filename):
        #        generate_machining_schedule()    
        #        assign_date_machining(solution_machining,ofile, today)
        #        break
        #else: print("Wrong choice, please enter 1 or 2 only")

if __name__ == "__main__":
    main()



