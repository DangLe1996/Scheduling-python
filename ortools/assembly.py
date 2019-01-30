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

# Import Python wrapper for or-tools CP-SAT solver.

def Assembly_Scheduling(all_orders, groups):
    horizon = 5
    from ortools.linear_solver import pywraplp
    solver = pywraplp.Solver('CoinsGridCLP',
                             pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
    x = {}
    y = {}
    z = {}
    variable_list = []
    for o in all_orders:
        for i in o.sections:
            for j in i.qualified_groups:
                x[(i.ID,j)] = solver.IntVar(0,1, 'x[%i,%i]' % (i.ID,j))
                #variable_list.append(x[(i.ID,j)])
            for j in range(horizon):
                y[(i.ID,j)] = solver.IntVar(0,1, 'y[%i,%i]' % (i.ID,j))
                #variable_list.append(y[(i.ID,j)])
                for k in i.qualified_groups:
                    z[(i.ID,j,k)] = solver.IntVar(0,int( i.real_time), 'z[%i,%i,%i]' % (i.ID,j,k))
                    variable_list.append(z[(i.ID,j,k)])
    
    makespan = solver.IntVar(0,horizon, 'makespan')
    days_used = solver.IntVar(0,10000, 'days_used')
    for o in all_orders:
        for i in o.sections:
            solver.Add(solver.Sum([x[(i.ID,j)] for j in i.qualified_groups]) == 1) #one group
            solver.Add(solver.Sum([y[(i.ID,j)] for j in range(horizon)]) >= 1) #multiple days
            [solver.Add(makespan >= y[(i.ID,j)]*j) for j in range(horizon)]
            [solver.Add(z[(i.ID,j,k)] <= i.real_time *x[(i.ID,k)]) for j in range(horizon) for k in i.qualified_groups]
            [solver.Add(z[(i.ID,j,k)] <= i.real_time *y[(i.ID,j)]) for j in range(horizon) for k in i.qualified_groups]
            solver.Add(solver.Sum([z[(i.ID,j,k)]for j in range(horizon) for k in i.qualified_groups]) == int( i.real_time))
    solver.Add(days_used == solver.Sum([y[(i.ID,j)]for j in range(horizon) for o in all_orders for i in o.sections]) )
    for k in groups.number:
        expr = []
        for j in range(horizon):
            for o in all_orders:
                for i in o.sections:
                    if k in i.qualified_groups:
                        expr.append(z[(i.ID,j,k)])
            solver.Add(solver.Sum(expr[r] for r in range(len(expr))) <= groups.capacity[k])
            expr.clear()


    solver.Minimize(makespan + days_used)
    #solver.Minimize(makespan )
    solver.Solve()
    best = round(makespan.SolutionValue())
    print(round(days_used.SolutionValue()))
    print(best)
    for variable in variable_list:
        if variable.solution_value() > 0:
            print(('%s = %f' % (variable.name(), variable.solution_value())))
    print('finish')