# -*- coding: utf-8 -*-
"""
Created on Mon Dec 31 14:20:26 2018

@author: baoda
"""

from __future__ import print_function
import pandas as pd
import collections
import math
from operator import attrgetter, itemgetter
import time
from datetime import datetime,date, timedelta 

# Import Python wrapper for or-tools CP-SAT solver.

class order():
    def __init__(self, ID):
        self.ID = ID
        self.a_time = 0
        self.Status = 0
        self.sections = []
    def add_section(self,value):
        self.sections.append(value)
class sub_order():
    priority_rank = {
    'High Priority': 1,
    'Priority' : 2,
    'Regular': 3

    }
    status_rank = {
        'Wiring Started': 1,
        'Machine Shop Finished' : 2,
        'Machine Shop Started': 3,
        

       }
    dbug_value = ['Order', 'Line','Status','Priority', 
                  'Ship_date', 'Issue','Missing',
                 'Complete', 'Resolve' ]

    fields = ['Order', 'Line', 'Status', 'Scheduled Ship Date',
             'Remaining Time', 'Sched Date Priority' , 
             'Issue','Missing Materials', 'Assembly Line', 
             'Complete/Partial' ]
    fields_input = {
        'Order': 'Order', 
        'Line': 'Line',
        'Status': 'Status', 
        'Time' : 'Real Time',
        'Priority': 'Sched Date Priority', 
        'Ship_date': 'Sched. Ship Date', 
        'Issue': 'ISSUE', 
        'Missing': 'Missing Materials', 
        'Complete': 'Complete/Partial',
        'Group' : 'Production Group',
        'Resolve': 'Issue Resolved'
        }

    def __init__(self, index ):
        self.index = index
    
    

class groups():
    capacity = {}
    @classmethod
    def capacity_input(cls,filename):
        try:
            capacity_input = pd.read_csv(filename, skipinitialspace=True)
        except FileNotFoundError:
            print('Invalid file input or file does not exist, please check again')
            return 0
        for index, row in capacity_input.iterrows():
            cls.capacity[row["Group"]] = row["Capacity"]

class assembly_scheduling():
    bad_orders = []
    map_order = {}
    solution =[]
    today = 0
    order_rank = {
        1: [], 
        2: [], 
        3: [], 
        4: [], 
        5: [], 
        6: [], 
        7: []
        
        }
    @classmethod
    def read_data_excel(cls,filename, today, sheet):
        formatter_string = "%d.%m.%Y" 
   
        today = pd.to_datetime(today, format=formatter_string)
        cls.today = today
        line = []
        data_file = pd.read_excel(filename, sheet_name=sheet)
        try:
            d_file= open("debug.csv","w")
            status_7= open("status_7.csv","w")
            status_7.write('Order, Line, Status, Promised, Scheduled Ship Date, Issue, Missing Materials \n')
            d_file.write('Order, Line, Status, Promised, Scheduled Ship Date, Issue, Missing Materials \n')
        except PermissionError:
            print('Please close the file debug.csv and return the program')
            ans = input("Press any button to exit")
            exit()
        for index, row in data_file.iterrows():
            if not ( row[sub_order.fields_input['Status']] in sub_order.status_rank and row[sub_order.fields_input['Complete']] == 'Complete'): 
                if (not (pd.isnull(row[sub_order.fields_input['Issue']]) or row[sub_order.fields_input['Issue']] == 0)) or row[sub_order.fields_input['Resolve'] == True]:
                    if row[sub_order.fields_input['Order']] not in cls.bad_orders:
                        cls.bad_orders.append(row[sub_order.fields_input['Order']])
                    for i in sub_order.dbug_value:
                        line += str(row[sub_order.fields_input[i]])
                        line +=','
                    line += '\n' 
        line = ''.join(line)
        print('Number of bad orders are ', len(cls.bad_orders))
        d_file.write(line)
        for index, row in data_file.iterrows():
            if row['Order'] not in cls.bad_orders:
                try:
                    r = float(row[sub_order.fields_input['Time']])
                    sub = sub_order(index)
                    for index, value in sub_order.fields_input.items():
                        setattr(sub, index, row[value])
                    value = [0, sub.Ship_date.dayofyear - today.dayofyear]
                    setattr(sub,'delta', max(value ))
                    ID = int(str(sub.Order) + str(max(value)) )
                    if(ID not in cls.map_order):
                        ord = order(ID)
                        setattr(ord, 'priority', 5)
                        setattr(ord,'assembly_seq', 7 )
                        cls.map_order[ID] = ord
                    setattr(sub,'ID', ID )
                    if sub_order.status_rank[sub.Status] == 1 and  pd.isnull(sub.Missing):
                        setattr(sub,'assembly_seq', 1 )
                    elif sub_order.status_rank[sub.Status] == 2:
                        try:
                            if pd.isnull(sub.Missing):
                                setattr(sub,'assembly_seq', 2 ) 
                            elif sub.Missing == '=+Cartridge':
                                setattr(sub,'assembly_seq', 3 )
                            else :setattr(sub,'assembly_seq', 7 )
                        except TypeError:
                            setattr(sub,'assembly_seq', 7 )
                    elif sub_order.status_rank[sub.Status] == 3:
                        if sub.Missing == '=+lens' or pd.isnull(sub.Missing):
                            setattr(sub,'assembly_seq', 4 )   
                        
                        elif sub.Missing == 'Material+Cartridge':
                            setattr(sub,'assembly_seq', 5 )  
                        
                        elif sub.Missing == 'Material+lens+Cartridge+Housing':
                            setattr(sub,'assembly_seq', 6 )
                        
                        else :setattr(sub,'assembly_seq', 7 )
                    else :setattr(sub,'assembly_seq', 7 )

                    if row[sub_order.fields_input['Time']] >= 0:
                        cls.map_oder_input(sub)
                        sub.ID = int (str(sub.ID) + str(sub.Line))
                        
                    else:
                        print('Order ', row['Order'], ' ', row['Line'], ' has bad input: ' , row[sub_order.fields_input['Time']])
                except Exception as e: 
                    print('Order ', row['Order'], ' ', row['Line'], ' has bad input')
                    del cls.map_order[sub.ID]
                    print(e)
                     
        line2 = []
        for index, ord in cls.map_order.items():
            if len(ord.sections) > 0:
                cls.order_rank[ord.assembly_seq].append(ord)
                setattr(ord, 'delta', ord.sections[0].delta)
                if ord.assembly_seq == 7:
                    for s in ord.sections:
                       if s.assembly_seq == 7:
                            for i in sub_order.dbug_value:
                                line2 += str(getattr(s,i) )
                                line2 +=','
                            line2 += '\n'
                if ord.assembly_seq < 7:
                    setattr(ord, 'group', ord.sections[0].Group)
                    cls.solution.append(ord)
        line2 = ''.join(line2)
        status_7.write(line2)    
        print('Number of good orders are ', len(cls.solution))
        print('File input sucessfully')
       


    @classmethod
    def assign_date_before(cls,groups, output):
        try:
            ofile= open(output,"w")
            ofile.write('Order, Line, Assigned Group, Start Date, Finish day, Ship day, Assembly Time, Status \n')
        except PermissionError:
            print('Please close the file output.csv and return the program')
            ans = input("Press any button to exit")
            exit()
        output = ['Order', 'Line', 'Group','start_day', 'finish_day', 'Ship_date', 'Time', 'Status']
        cls.solution.sort(key = attrgetter('group', 'Status','delta', 'priority' ), reverse=False)
        line = []
        useage_after= {
            1: 0, 
            4: 0,
            7: 0,
            10: 0, 
            12: 0,
            15:0, 
            18:0
            }
        if len(cls.solution) > 0:
            for o in cls.solution:
                for s in o.sections:
                    try:
                        s.Group = int(s.Group)
                        start =  useage_after[s.Group]
                        useage_after[s.Group]  = useage_after[s.Group] + math.ceil(float(s.Time))
                        finish =  useage_after[s.Group]
                        start = math.floor((start)/ (60*groups.capacity[s.Group]))
                        finish =  math.floor((finish)/ (60*groups.capacity[s.Group]))
                        setattr(s, 'start_day', cls.today + pd.Timedelta(start, unit='d')  )
                        setattr(s, 'finish_day', cls.today + pd.Timedelta(finish, unit='d')  )
                        for i in output:
                            line += str(getattr(s,i))
                            line += ","   
                        line += "\n"
                        line = ''.join(line)
                    except Exception as e: 
                        pass
            ofile.write(line)
            print('Useage per group')
            print(useage_after)

    @classmethod
    def assign_date_after(cls,groups, output):
        try:
            ofile= open(output,"w")
            ofile.write('Order, Line, Assigned Group, Start Date, Finish day, Ship day, Assembly Time, Status \n')
        except PermissionError:
            print('Please close the file output.csv and return the program')
            ans = input("Press any button to exit")
            exit()
        output = ['Order', 'Line', 'Group','start_day', 'finish_day', 'Ship_date', 'Time', 'Status']
        cls.solution.sort(key = attrgetter('group', 'Status','delta', 'priority' ), reverse=False)
        line = []
        useage_after= {
            1: 0, 
            4: 0,
            7: 0,
            10: 0, 
            12: 0,
            15:0, 
            18:0
            }
        if len(cls.solution) > 0:
            for o in cls.solution:
                for s in o.sections:
                    try:
                        s.Group = int(s.Group)
                        start =  useage_after[s.Group]
                        useage_after[s.Group]  = useage_after[s.Group] + math.ceil(float(s.Time))
                        finish =  useage_after[s.Group]
                        start = math.floor((start)/ (60*groups.capacity[s.Group]))
                        finish =  math.floor((finish)/ (60*groups.capacity[s.Group]))
                        setattr(s, 'start_day', cls.today + pd.Timedelta(start, unit='d')  )
                        setattr(s, 'finish_day', cls.today + pd.Timedelta(finish, unit='d')  )
                        for i in output:
                            line += str(getattr(s,i))
                            line += ","   
                        line += "\n"
                        line = ''.join(line)
                    except Exception as e: 
                        pass
            ofile.write(line)
            print('Useage per group')
            print(useage_after)

     
    @classmethod
    def map_oder_input(cls,sub):
        if sub not in cls.map_order[sub.ID].sections:
            cls.map_order[sub.ID].priority = max(cls.map_order[sub.ID].priority,sub_order.priority_rank [sub.Priority])
            cls.map_order[sub.ID].Status = max(sub_order.status_rank[sub.Status],cls.map_order[sub.ID].Status)
            cls.map_order[sub.ID].assembly_seq = min(sub.assembly_seq, cls.map_order[sub.ID].assembly_seq)
            cls.map_order[sub.ID].add_section(sub)
            try:
                cls.map_order[sub.ID].a_time += math.ceil(sub.Time)
            except TypeError or ValueError :
                 pass

    @classmethod
    def read_data_assembly(cls,filename, today):
        today = datetime.strptime( today,"%d/%m/%Y" )
        fields = ['Job no.','Order', 'Line', 'Status', 'Sched. Ship Date',
                 'Real Status' , 'Real Time', 'Promised' , 'ISSUE',
                 'Missing Materials', 'Production Group', 'Production Group', 'Complete/Partial' ]
        try:
            assembly_input = pd.read_csv(filename, skipinitialspace=True, usecols=fields)
            d_file= open("debug.csv","w")
            d_file.write('Order, Line, Status, Promised, Scheduled Ship Date, Issue, Missing Materials \n')
        except FileNotFoundError:
            print('Invalid file input or file does not exist, please check again')
            return 0
    

        line = []
        good_value = ['0', float('NaN')]
        dbug_value = ['Order', 'Line','Status','Promised', 'Sched. Ship Date', 'ISSUE','Missing Materials', 'Complete/Partial'  ]
        for index, row in assembly_input.iterrows():
            if row['Order'] not in cls.bad_orders:
                if not ( row['Status'] in sub_order.status_rank and row['Complete/Partial'] == 'Complete' and  (pd.isnull(row['ISSUE']) or row['ISSUE'] == '0')):
                    cls.bad_orders.append(row['Order'])
                    for i in dbug_value:
                        line += str(row[i]) + ','
                    line += '\n' 
        line = ''.join(line)
        d_file.write(line)
        for index, row in assembly_input.iterrows():
            if row['Order'] not in cls.bad_orders:
                    if(row['Order'] not in cls.map_order):
                        ord = order(row['Order'])
                        setattr(ord, 'priority', 5)
                        cls.map_order[row['Order']] = ord
                    sub = sub_order(index)
            
                    for value in fields:
                        setattr(sub, value, row[value])
                    setattr(sub, 'priority', sub_order.priority_rank[sub.Promised])
                    formatter_string = "%d.%m.%Y" 
                    datetime_object = datetime.strptime(getattr(sub,'Sched. Ship Date'), formatter_string)
                    subtract = abs((datetime_object - today).days)
                    setattr(sub,'ship_date', datetime_object.date())
                    setattr(sub,'days_from_today', subtract)
                    setattr(sub,'real_time', getattr(sub,'Real Time'))
                    quali = list(map(int, getattr(sub,'Production Group').split(',')))
                    setattr(sub, 'qualified_groups',quali)
                    value = [0, subtract]
                    ID = str(row['Order']) + str(row['Line']) + str(max(value))
                    setattr(sub, 'ID',int(ID))
                    if sub_order.status_rank[sub.Status] == 1 :
                        sub.Status = 1
                    elif sub_order.status_rank[sub.Status] == 2:
                        try:
                            if math.isnan(getattr(sub,'Missing Materials')):
                                sub.Status = 2   
                            elif getattr(sub,'Missing Materials') == '=+Cartridge':
                                sub.Status = 3
                            else :sub.Status = 7
                        except TypeError:
                            sub.Status = 7
                    elif sub_order.status_rank[sub.Status] == 3:
                        if getattr(sub,'Missing Materials') == '=+lens':
                            sub.Status = 4     
                        if getattr(sub,'Missing Materials') == 'Material+Cartridge':
                            sub.Status = 5  
                        if getattr(sub,'Missing Materials') == 'Material+lens+Cartridge+Housing':
                            sub.Status = 6
                        else :sub.Status = 7
                    else :sub.Status = 7
                    cls.map_oder_input(sub)
        print('File input sucessfully')
        for index, ord in cls.map_order.items():
            cls.order_rank[ord.Status].append(ord);
        return cls.order_rank


    def schedule(all_orders, groups):
        if len(all_orders) > 0:
            horizon = 5
            from ortools.linear_solver import pywraplp
            solver = pywraplp.Solver('CoinsGridCLP',
                                     pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
            x = {} #assign sub order to a group
            y = {} #assign order to date
            z = {} #amount of sub order assign to group g
            f = {} #the flow time of order in the system
            h = {} #finish time of order
            variable_list = []
            for o in all_orders:
                f[o.ID] = solver.IntVar(0,horizon, 'flow[%i]'  %(o.ID))
                h[o.ID] = solver.IntVar(0,horizon, 'finish[%i]'  %(o.ID))
                for j in range(horizon):
                        y[(o.ID,j)] = solver.IntVar(0,1, 'y[%i,%i]'  %(o.ID,j))
                        variable_list.append(y[(o.ID,j)])
                for i in o.sections:
                    if type(i.Group) == list:
                        x = {(i.ID,j): solver.IntVar(0,1, 'x[%i,%i]' % (i.ID,j)) for j in i.Group}
                    else:
                        x[(i.ID,i.Group)] = solver.IntVar(0,1,'x%i%i' %(i.ID,i.Group))
                    for j in range(horizon):
                        #y[(i.ID,j)] = solver.IntVar(0,1, 'y[%i,%i]'  %(i.ID,j))
                        #variable_list.append(y[(i.ID,j)])
                        if type(i.Group) == list:
                            z = {(i.ID,j,k): solver.IntVar(0,int( i.Time), 'z[%i,%i,%i]' % (i.ID,j,k)) for k in i.Group}
                        else: z[(i.ID,j,i.Group)] = solver.IntVar(0,max(0,int(i.Time)), 'z[%i,%i,%i]' % (i.ID,j,i.Group))
                        #for k in i.group:
                        #    z[(i.ID,j,k)] = solver.IntVar(0,int( i.real_time), 'z[%i,%i,%i]' % (i.ID,j,k))
                        #variable_list.append(z[(i.ID,j,k)])
           
            makespan = solver.IntVar(0,horizon, 'makespan')
            days_used = solver.IntVar(0,1000, 'days_used')
            for o in all_orders:
                [solver.Add(y[(o.ID,j)]*j + f[o.ID] >= y[(o.ID,j_prime)]* j_prime) for j in range(horizon) for j_prime in range(horizon) if j_prime != j ]
                solver.Add(f[o.ID] <= 5)
                solver.Add(solver.Sum([y[(o.ID,j)] for j in range(horizon)]) <= 5) #multiple days
                solver.Add(solver.Sum([y[(o.ID,j)] for j in range(horizon)]) >= 1)
                [solver.Add(makespan >= y[(o.ID,j)]*j) for j in range(horizon)]
   
                for i in o.sections:
                    
                    if type(i.Group) == list:
                        solver.Add(solver.Sum([x[(i.ID,j)] for j in i.Group]) >= 1)
                        [solver.Add(z[(i.ID,j,k)] <= i.Time *x[(i.ID,k)]) for j in range(horizon) for k in i.Group]
                        [solver.Add(z[(i.ID,j,k)] <= i.Time *y[(o.ID,j)]) for j in range(horizon) for k in i.Group]
                        solver.Add(solver.Sum([z[(i.ID,j,k)]for j in range(horizon) for k in i.Group]) == int( i.Time))
                    else:
                        k = i.Group
                        solver.Add( x[(i.ID,k)] == 1) #one group
                        [solver.Add(z[(i.ID,j,k)] <= i.Time *x[(i.ID,k)]) for j in range(horizon)]
                        [solver.Add(z[(i.ID,j,k)] <= i.Time *y[(o.ID,j)]) for j in range(horizon)]
                        solver.Add(solver.Sum([z[(i.ID,j,k)]for j in range(horizon)]) == int( i.Time))
            #solver.Add(days_used == solver.Sum([y[(o.ID,j)]for j in range(horizon) for o in all_orders ]) )
            solver.Add(days_used == solver.Sum([f[(o.ID)] for o in all_orders ]) )
            for k, avail_hour in groups.capacity.items():
                expr = []
                for j in range(horizon):
                    for o in all_orders:
                        for i in o.sections:
                            if type(i.Group) == list and k in i.Group:
                                expr.append(z[(i.ID,j,k)])
                            elif i.Group == k:
                                expr.append(z[(i.ID,j,k)])
                    solver.Add(solver.Sum(expr[r] for r in range(len(expr))) <= avail_hour*60)
                    expr.clear()


            solver.Minimize(makespan + days_used)
            #solver.Minimize(makespan)
            solver.SetTimeLimit(10000)
            solver.Solve()
            print(round(makespan.SolutionValue()))
            print(round(days_used.SolutionValue()))
            #for o in all_orders:
            #    print(f[o.ID].SolutionValue())
            #print(best)
        #for variable in variable_list:
        #    if variable.solution_value() > 0:
        #        print(('%s = %f' % (variable.name(), variable.solution_value())))
def main1():
    
    assembly_scheduling.read_data_excel('feb12.xlsx', '12.02.2019','Production Meeting')
    groups.capacity_input('capacity.csv')
    #assembly_scheduling.assign_date_before(groups,'output.csv')
    for index, list in assembly_scheduling.order_rank.items():
        print(len(list))
        assembly_scheduling.schedule(list,groups)
     
def main2():
    qualified_orders = {}
    qualified_orders = assembly_scheduling.read_data_assembly('a_input.csv','14/02/2019')
    groups.capacity_input('capacity.csv')
    for index, list in qualified_orders.items():
        if index < 7:
            assembly_scheduling.schedule(list, groups)

if __name__ == '__main__':
    main1()