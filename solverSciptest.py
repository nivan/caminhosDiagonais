from pyscipopt import Model
import pyscipopt
import util
import math
from collections import OrderedDict 

def printFunc(name,m):
     """prints results"""
     print("* %s *" % name)
     objSet = bool(m.getObjective().terms.keys())
     print("* Is objective set? %s" % objSet)
     if objSet:
         print("* Sense: %s" % m.getObjectiveSense())
     for v in m.getVars():
         if v.name != "n":
             print("%s: %d" % (v, round(m.getVal(v))))
     print("\n")

if True:
    graph = [[1,2],[1,3],[1,5],[2,5],[4,5]]
    numVertices = 5
    name = 'aleat1'
    h = math.ceil((numVertices-1)/4.0)

    #
    model = Model("lp graph %s" % (name,))
    model.setPresolve(pyscipopt.SCIP_PARAMSETTING.OFF)
    model.setHeuristics(pyscipopt.SCIP_PARAMSETTING.OFF)
    model.disablePropagation()

    #
    paths            = util.generateAllPaths(h)
    constraints      = {}
    modelVariables   = {}
    modelConstraints = OrderedDict()
    xos = []
    for path in paths:
        result = util.generateConstraints(path,h)
        for key in result:
            constraint = result[key]
            constraints[key] = constraint
            
            #create variables
            for vv in constraint['variables']:
                v = tuple(vv)
                if not (v in modelVariables):
                    varName = util.getVariableName(v)
                    modelVariables[v] = model.addVar(vtype="C", name=varName)
                    
            #create constraint
            if constraint['entryType'] == 3:
                ## create xo
                i = constraint['variables'][0][0]
                j = constraint['variables'][1][0]
                k = constraint['variables'][2][0]
                xoName = 'xo_%d_%d_%d' % (i,j,k)
                if not (xoName in modelVariables):
                    modelVariables[xoName] = model.addVar(vtype="C", name=xoName, lb=0)
                    xos.append(xoName)
                ## create constraints
                v0 = modelVariables[tuple(constraint['variables'][0])]
                v1 = modelVariables[tuple(constraint['variables'][1])]
                v2 = modelVariables[tuple(constraint['variables'][2])]
                xo = modelVariables[xoName]
                modelConstraints[key] = model.addCons(constraint['signs'][0]*v0 +
                                                      constraint['signs'][1]*v1 +
                                                      constraint['signs'][2]*v2 +
                                                      xo
                                                          <= constraint['rightSide'])

            elif constraint['entryType'] == 2:
                #create xo
                i = constraint['variables'][0][0]
                j = constraint['variables'][0][1]
                xoName = 'xo_%d_%d ' % (i,j)
                if not (xoName in modelVariables):
                    modelVariables[xoName] = model.addVar(vtype="C", name=xoName, lb=0)
                    xos.append(xoName)
                #create constraint
                v0 = modelVariables[tuple(constraint['variables'][0])]
                v1 = modelVariables[tuple(constraint['variables'][1])]
                xo = modelVariables[xoName]
                modelConstraints[key] = model.addCons(constraint['signs'][0]*v0 +
                                                      constraint['signs'][1]*v1 +
                                                      xo
                                                          <= constraint['rightSide'])
            else:
                #create xo
                i = constraint['variables'][0][0]
                j = constraint['variables'][1][0]
                k = constraint['variables'][2][0]
                l = constraint['variables'][3][0]
                xoName = 'xo_%d_%d_%d_%d ' % (i,j,k,l)
                if not (xoName in modelVariables):
                    modelVariables[xoName] = model.addVar(vtype="C", name=xoName, lb=0)
                    xos.append(xoName)
                #
                v0 = modelVariables[tuple(constraint['variables'][0])]
                v1 = modelVariables[tuple(constraint['variables'][1])]
                v2 = modelVariables[tuple(constraint['variables'][2])]
                v3 = modelVariables[tuple(constraint['variables'][2])]
                xo = modelVariables[xoName]
                modelConstraints[key] = model.addCons(constraint['signs'][0]*v0 +
                                                      constraint['signs'][1]*v1 +
                                                      constraint['signs'][2]*v2 +
                                                      constraint['signs'][3]*v3 +
                                                      xo
                                                          <= constraint['rightSide'])

    print(modelVariables.keys())
    #
    exp = 0
    for edge in graph:
        v = modelVariables[tuple(edge)]
        exp += v
    for name in xos:
        v = modelVariables[name]
        exp += v
    model.setObjective(exp, "maximize")
    model.writeProblem("prod1_scip.lp") #xx
    model.optimize()
    if model.getStatus() == "optimal":
        print("Optimal value:", model.getObjVal())
        print("Dual Solution:")
        for name in modelConstraints.keys():
            print(name,model.getDualsolLinear(modelConstraints[name]))
    else:
        print("Problem could not be solved to optimality")
else:
    model = Model("Simple linear optimization")

    model.setPresolve(pyscipopt.SCIP_PARAMSETTING.OFF)
    model.setHeuristics(pyscipopt.SCIP_PARAMSETTING.OFF)
    model.disablePropagation()

    x_1 = model.addVar(vtype="C", name="x1")
    x2 = model.addVar(vtype="C", name="x2")
    x3 = model.addVar(vtype="C", name="x3")


    c1 = model.addCons(2*x_1 + x2 + x3 <= 60)
    c2 = model.addCons(x_1 + 2*x2 + x3 <= 60)
    model.addCons(x3 <= 30)


    model.setObjective(15*x_1 + 18*x2 + 30*x3, "maximize")
    model.writeProblem("prod1_scip.lp") #xx
    model.optimize()


    print(model.getDualsolLinear(c1))

    if model.getStatus() == "optimal":
        print("Optimal value:", model.getObjVal())
        print("Solution:")
        print(" x1 = ", model.getVal(x_1))
        print(" x2 = ", model.getVal(x2))
        print(" x3 = ", model.getVal(x3))
    else:
        print("Problem could not be solved to optimality")

