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
        #'Group' : 'Production Group',
        'Group' : 'Production Group Axis',
        'Resolve': 'Issue Resolved'
        }

    def __init__(self, index ):
        self.index = index
        self.group_assigned = 0
        self.amount_assigned = {}
    

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
            ID = str(row[sub_order.fields_input['Order']]) + str(max(0,row[sub_order.fields_input['Ship_date']].dayofyear))
            if row[sub_order.fields_input['Status']] not in sub_order.status_rank and row[sub_order.fields_input['Complete']] == 'Complete':
                if ID not in cls.bad_orders:
                        cls.bad_orders.append(ID)
                for i in sub_order.dbug_value:
                        line += str(row[sub_order.fields_input[i]])
                        line +=','
                line += '\n'
            elif not ( row[sub_order.fields_input['Status']] in sub_order.status_rank and row[sub_order.fields_input['Complete']] == 'Complete' and (pd.isnull(row[sub_order.fields_input['Issue']]) or row[sub_order.fields_input['Issue']] == 0)): 
                allowed_status = ['Machine Shop Finished', 'Wiring Started', 'Packaging Finished', 'Given to Shipping']
                if row[sub_order.fields_input['Complete']] == 'Partial' and row[sub_order.fields_input['Status']] in allowed_status and (pd.isnull(row[sub_order.fields_input['Issue']]) or row[sub_order.fields_input['Issue']] == 0):
                    pass
                elif ( row[sub_order.fields_input['Resolve']] == False):
                    if ID not in cls.bad_orders:
                        cls.bad_orders.append(ID)

                    for i in sub_order.dbug_value:
                        line += str(row[sub_order.fields_input[i]])
                        line +=','
                    line += '\n' 
        line = ''.join(line)
        print('Number of bad orders are ', len(cls.bad_orders))
        d_file.write(line)
        for index, row in data_file.iterrows():
            order_ID = str(row[sub_order.fields_input['Order']]) + str(max(0,row[sub_order.fields_input['Ship_date']].dayofyear))
            if order_ID not in cls.bad_orders:
                try:
                    r = float(row[sub_order.fields_input['Time']])
                    sub = sub_order(index)
                    for index, value in sub_order.fields_input.items():
                        setattr(sub, index, row[value])
                    if type(sub.Group) == str:
                        quali = list(map(int, sub.Group.split(',')))
                        sub.Group = quali
                    setattr(sub,'delta', max(0, sub.Ship_date.dayofyear - today.dayofyear))
                    ID = int(str(sub.Order) + str(sub.delta) )
                    if(ID not in cls.map_order):
                        ord = order(ID)
                        setattr(ord, 'priority', 5)
                        setattr(ord,'assembly_seq', 7 )
                        setattr(ord,'number', row[sub_order.fields_input['Order']] )
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
                except KeyError as e:
                    pass
                    #if str(e) in allowed_status:
                    #    pass
                    #else: print ('I got a KeyError - reason "%s"' % str(e))
                except Exception as e: 
                        print('Order ', row['Order'], ' ', row['Line'], ' has bad value input')
               
                        print(e)
                     
        line2 = []
        for index, ord in cls.map_order.items():
            if len(ord.sections) > 0:
                
                setattr(ord, 'delta', ord.sections[0].delta)
                if ord.assembly_seq == 7:
                    for s in ord.sections:
                       if s.assembly_seq == 7:
                            for i in sub_order.dbug_value:
                                line2 += str(getattr(s,i) )
                                line2 +=','
                            line2 += '\n'
                if ord.assembly_seq < 7:
                    cls.order_rank[ord.assembly_seq].append(ord)
                    setattr(ord, 'group', ord.sections[0].Group)
                    cls.solution.append(ord)
        line2 = ''.join(line2)
        status_7.write(line2)    
        print('Number of good orders are ', len(cls.solution))
        print('File input sucessfully')
        return 1


    @classmethod
    def Case1(cls,groups, output):
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
    def case4_output(cls,groups, output):
        import operator
        try:
            ofile= open(output,"w")
            ofile.write('Order, Line, Assigned Group, Start Date,Amount , Ship day, Assembly Time\n')
        except PermissionError:
            print('Please close the file output.csv and return the program')
            ans = input("Press any button to exit")
            exit()

        
        date= {
            1: 0, 
            4: 0,
            7: 0,
            10: 0, 
            12: 0,
            15:0, 
            18:0
            }
        #cls.best_fit()
        for index, list in assembly_scheduling.order_rank.items():
            if index == 7:
                break
            #print("index is " , index)
            max_date= {
            1: 0, 
            4: 0,
            7: 0,
            10: 0, 
            12: 0,
            15:0, 
            18:0
            }
            
            for order in list:
                for s in order.sections:
                    try:
                        for list, item in s.amount_assigned.items():
                            line = []
                            line += str(s.Order) + ","
                            line += str(s.Line) + ","
                            line += str(list[1]) + ","
                            setattr(s, 'start_day', cls.today + pd.Timedelta(list[0] + date[list[1]], unit='d'))
                            line += str( s.start_day) + ","
                            line += str(item) + ","
                            max_date[list[1]] = max(list[0], max_date[list[1]])
                            line += str(s.Ship_date) + ","
                            line += str(s.Time) + ","
                            line += str(index) + ","
                            line += '\n'
                            line = ''.join(line)
                            ofile.write(line)
                    except Exception as e:
                        print(e)
                        pass
            for key, value in max_date.items():
                date[key] += value + 1
                #print (date[key])

 
        line = ''.join(line)
        ofile.write(line)
   
       
     
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
    #@classmethod
    #def best_fit(cls):
    #    #useage = {
    #    #    1: 0, 
    #    #    4: 0,
    #    #    7: 0,
    #    #    10: 0, 
    #    #    12: 0,
    #    #    15:0, 
    #    #    18:0

    #    #    }
    #    #for index, list in assembly_scheduling.order_rank.items():
    #    #     for o in list:
    #    #        if(o.Status > 1):
    #    #            for s in o.sections:
    #    #                for item, amount in s.amount_assigned.items():
    #    #                    if(g != o.group):
    #    #                        if(useage[o.group] - useage[g] >= o.a_time):
    #    #                            useage[o.group] -= o.a_time
    #    #                            useage[g] += o.a_time
    #    #                            o.group = g
    #    #        else:
    #    #            for s in o.sections:
    #    #                for item, amount in s.amount_assigned.items():
    #    #                    useage[s.group_assigned] += amount
    #    print('finish')


    @classmethod
    def Case4(cls,all_orders, groups):
        if len(all_orders) > 0:
            print("Amount of orders is ",len(all_orders))
            #horizon = len(all_orders)
            horizon = 5
            from ortools.linear_solver import pywraplp
            solver = pywraplp.Solver('CoinsGridCLP',
                                     pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
            sub_to_group = {} #assign sub order to a group
            order_to_date = {} #assign order to date
            sub_amount_to_group = {} #amount of sub order assign to group g
            flow_time = {} #the flow time of order in the system
            finish_time_order = {} #finish time of order
            order_lateness = {} #finish time of order
            variable_list = []
            for o in all_orders:
                flow_time[o.ID] = solver.IntVar(0,horizon, 'flow[%i]'  %(o.ID)) 
                finish_time_order[o.ID] = solver.IntVar(0,horizon, 'finish[%i]'  %(o.ID))
                order_lateness[o.ID] = solver.IntVar(0,horizon, 'late[%i]'  %(o.ID))
                for j in range(horizon):
                        order_to_date[(o.ID,j)] = solver.IntVar(0,1, 'y[%i,%i]'  %(o.ID,j))
                        variable_list.append(order_to_date[(o.ID,j)])
                for i in o.sections:
                    if i.Time < 0:
                        o.sections.remove(i)
                    try:
                        for j in i.Group:
                            sub_to_group[(i.ID,j)] = solver.IntVar(0,1, 'x[%i,%i]' % (i.ID,j))
                    except:
                        sub_to_group[(i.ID,i.Group)] = solver.IntVar(0,1,'x%i%i' %(i.ID,i.Group))
                    for j in range(horizon):

                        try:
                            for k in i.Group:
                                sub_amount_to_group[(i.ID,j,k)] = solver.IntVar(0,max(0,int(i.Time)), 'z[%i,%i,%i]' % (i.ID,j,k))
                        except:
                            sub_amount_to_group[(i.ID,j,i.Group)] = solver.IntVar(0,max(0,int(i.Time)), 'z[%i,%i,%i]' % (i.ID,j,i.Group))
                    
           
            makespan = solver.IntVar(0,horizon, 'makespan')
            days_used = solver.IntVar(0,len(all_orders), 'days_used')
            total_lateness = solver.IntVar(0,horizon*4, 'total_lateness')
            for o in all_orders:
                solver.Add(finish_time_order[o.ID] <= o.delta + order_lateness[o.ID])
                [solver.Add(finish_time_order[o.ID] >= order_to_date[(o.ID,j)]*j)for j in range(horizon)]
                [solver.Add(order_to_date[(o.ID,j)]*j + flow_time[o.ID] >= order_to_date[(o.ID,j_prime)]* j_prime) for j in range(horizon) for j_prime in range(horizon) if j_prime != j ]
                #solver.Add(flow_time[o.ID] <= 10)
                solver.Add(solver.Sum([order_to_date[(o.ID,j)] for j in range(horizon)]) <= horizon) #multiple days
                solver.Add(solver.Sum([order_to_date[(o.ID,j)] for j in range(horizon)]) >= 1)
                [solver.Add(makespan >= order_to_date[(o.ID,j)]*j) for j in range(horizon)]
   
                for i in o.sections:
                    
                    try:
                        solver.Add(solver.Sum([sub_to_group[(i.ID,j)] for j in i.Group]) == 1) #each section is assigned to only 1 group
                        [solver.Add(solver.Sum([sub_amount_to_group[(i.ID,j,k)] for j in range(horizon)]) <= i.Time *sub_to_group[(i.ID,k)])  for k in i.Group]
                        [solver.Add(solver.Sum([sub_amount_to_group[(i.ID,j,k)]for k in i.Group]) <= i.Time *order_to_date[(o.ID,j)]) for j in range(horizon) ]
                        solver.Add(solver.Sum([sub_amount_to_group[(i.ID,j,k)]for j in range(horizon) for k in i.Group]) == int( i.Time))
                    except:
                        k = i.Group
                        solver.Add( sub_to_group[(i.ID,k)] == 1) #each section is assigned to only 1 group
                        [solver.Add(sub_amount_to_group[(i.ID,j,k)] <= i.Time *sub_to_group[(i.ID,k)]) for j in range(horizon)]
                        [solver.Add(sub_amount_to_group[(i.ID,j,k)] <= i.Time *order_to_date[(o.ID,j)]) for j in range(horizon)]
                        solver.Add(solver.Sum([sub_amount_to_group[(i.ID,j,k)]for j in range(horizon)]) == int( i.Time))
            #solver.Add(days_used == solver.Sum([order_to_date[(o.ID,j)]for j in range(horizon) for o in all_orders ]) )
            solver.Add(days_used == solver.Sum([flow_time[(o.ID)] for o in all_orders ]) )

            #capacity constraint
            for k, avail_hour in groups.capacity.items():
                for j in range(horizon):
                    expr = []
                    for o in all_orders:
                        for i in o.sections:
                            try: 
                                if k in i.Group:
                                    expr.append(sub_amount_to_group[(i.ID,j,k)])
                            except:
                               if i.Group == k:
                                    expr.append(sub_amount_to_group[(i.ID,j,k)])
                    solver.Add(solver.Sum(expr[r] for r in range(len(expr))) <= avail_hour*60)
                    expr.clear()

            solver.Add(total_lateness == solver.Sum([order_lateness[o.ID] for o in all_orders]) )
            solver.Minimize(makespan + days_used + total_lateness)
            #solver.Minimize(makespan + days_used)
            #solver.Minimize(makespan)
            solver.SetTimeLimit(100000)
            status = solver.Solve()
            print('Number of variables =', solver.NumVariables())
            print('Number of constraints =', solver.NumConstraints())

            if status == solver.OPTIMAL or status == solver.FEASIBLE:
                #gap = solver.RELATIVE_MIP_GAP
                #print("GAP param: %f" % gap)
                print('makespan is %i' %(round(makespan.SolutionValue())))
                print('total_flow_time is %i' %(round(days_used.SolutionValue())))
                for o in all_orders:
                    #print('Amount of late for order %i is %i' %(o.ID, order_lateness[o.ID].solution_value()))
                    for s in o.sections:
                        for j in range(horizon):
                            for k in s.Group:
                                if sub_amount_to_group[(s.ID,j,k)].solution_value() > 0:
                                    s.amount_assigned[(j,k)] = sub_amount_to_group[(s.ID,j,k)].solution_value()
                                    s.group_assigned = k
         

def schedule_case_4(file,date,sheet):
    
    assembly_scheduling.read_data_excel(file, date,sheet)
    groups.capacity_input('System_Files/capacity.csv')
    for index, list in assembly_scheduling.order_rank.items():
        print(len(list))
        assembly_scheduling.Case4(list,groups)
        if index == 6: break
    assembly_scheduling.best_fit()
    assembly_scheduling.case4_output(groups,'output.csv')
    return 1
  
def schedule_case_1(file,date,sheet):

    assembly_scheduling.read_data_excel(file, date,sheet)
    groups.capacity_input('System_Files/capacity.csv')
    assembly_scheduling.Case1(groups,'output.csv')
    return 1

if __name__ == "__main__":
    schedule_case_1('test/feb18.xlsx','18.02.2019','Production Meeting')











#def test_one_groups():

#    assembly_scheduling.read_data_excel('test1.xlsx', '12.02.2019','Sheet3')
#    groups.capacity_input('capacity.csv')
#    #assembly_scheduling.Case1(groups,'output.csv')
#    for index, list in assembly_scheduling.order_rank.items():
#        print(len(list))
#        assembly_scheduling.Case4(list,groups)
#        if index == 1: break
#    return 1

#def test_schedule_76910(file,date,sheet):

#    assembly_scheduling.read_data_excel(file, date,sheet)
#    groups.capacity_input('capacity.csv')
#    assembly_scheduling.Case1(groups,'output.csv')
#    return 1

#def test_after(file,date,sheet):

#    assembly_scheduling.read_data_excel(file, date,sheet)
#    groups.capacity_input('capacity.csv')
#    assembly_scheduling.Case1(groups,'output.csv')
#    return 1
#def test_schedule_77356(value):

#    assembly_scheduling.read_data_excel('Feb14-check.xlsx', '14.02.2019',str(value))
#    groups.capacity_input('capacity.csv')
#    assembly_scheduling.Case1(groups,'output.csv')
#    return 1
#def main2():
#    qualified_orders = {}
#    qualified_orders = assembly_scheduling.read_data_assembly('a_input.csv','14/02/2019')
#    groups.capacity_input('capacity.csv')
#    for index, list in qualified_orders.items():
#        if index < 7:
#            assembly_scheduling.Case4(list, groups)

#def main1():
    
#    assembly_scheduling.read_data_excel('feb12.xlsx', '12.02.2019','Production Meeting')
#    groups.capacity_input('capacity.csv')
#    #assembly_scheduling.Case1(groups,'output.csv')
#    for index, list in assembly_scheduling.order_rank.items():
#        print(len(list))
#        assembly_scheduling.Case4(list,groups)
#        if index == 1: break
#    assembly_scheduling.case4_output(groups,'output.csv')
#def test_multiple_groups(file,date,sheet):
    
#    assembly_scheduling.read_data_excel(file, date,sheet)
#    groups.capacity_input('capacity.csv')
#    #assembly_scheduling.Case1(groups,'output.csv')
#    for index, list in assembly_scheduling.order_rank.items():
#        print(len(list))
#        assembly_scheduling.Case4(list,groups)
#        if index == 6: break
#    assembly_scheduling.case4_output(groups,'output.csv')
#    return 1

#if __name__ == '__main__':
#    test_schedule_77356()