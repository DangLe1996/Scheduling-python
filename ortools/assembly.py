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
    horizon = 10
    from ortools.linear_solver import pywraplp
    solver = pywraplp.Solver('CoinsGridCLP',
                             pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
    x = {}
    y = {}
    for o in all_orders:
        for i in o.sections:
            for j in i.qualified_groups:
                x[(i.ID,j)] = solver.IntVar(0,1, 'x[%i,%i]' % (i.ID,j))
            for j in range(horizon):
                y[(i.ID,j)] = solver.IntVar(0,1, 'y[%i,%i]' % (i.ID,j))
    #x = [[solver.IntVar(0,1, 'x[%i,%i]' % (i.ID,j)) for j in i.qualified_groups] for o in all_orders for i in o.sections]  
    #y = [[solver.IntVar(0,1, 'y[%i,%i]' % (i.ID,j)) for j in range(horizon)] for o in all_orders for i in o.sections]    
    makespan = solver.IntVar(0,horizon, 'makespan')
    for o in all_orders:
        for i in o.sections:
            solver.Add(solver.Sum([x[(i.ID,j)] for j in i.qualified_groups]) == 1) #one group
            solver.Add(solver.Sum([y[(i.ID,j)] for j in range(horizon)]) >= 1) #multiple days
            [solver.Add(makespan >= y[(i.ID,j)]*j) for j in range(horizon)]
    for j in groups.number:
        expr = []
        val = []
        for o in all_orders:
            for i in o.sections:
                if j in i.qualified_groups:
                    expr.append(x[(i.ID,j)])
                    val.append(i.real_time)
        solver.Add(solver.Sum(expr[r]*val[r] for r in range(len(expr))) <= groups.capacity[j])
        expr.clear()
        val.clear()
        #[[solver.Add(solver.Sum([y[i.ID][j] for j in range(horizon)]) >= 1)] for i in o.sections]
        #solver.Add(makespan >= y[i.ID][j]*j for j in range(horizon) for i in o.sections)
    solver.Minimize(makespan)
    solver.Solve()
    best = round(makespan.SolutionValue())
    print(best)
    print('finish')