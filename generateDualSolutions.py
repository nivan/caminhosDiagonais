from pyscipopt import Model
import pyscipopt
import util
import math
import sys
from collections import OrderedDict 
import os.path
import json

def solveFile(lpFileName,graphFileName,outDirectory):
    #
    model = Model("lp graph")
    model.setPresolve(pyscipopt.SCIP_PARAMSETTING.OFF)
    model.setHeuristics(pyscipopt.SCIP_PARAMSETTING.OFF)
    model.disablePropagation()
    model.readProblem(lpFileName)
    model.optimize()

    graphFile = json.load(open(graphFileName))
    
    
    f = open(outDirectory + '/dualSolution_' + graphFile['name'] + '.json' ,'w')
    
    if model.getStatus() == "optimal":
        output = {'name':graphFile['name'],
                  'edges':graphFile['edges'],
                  'vertices':graphFile['numVertices'],
                  'dualVariables':[]
        }

        #
        #print("Optimal value:", model.getObjVal())
        #print("Dual Solution:")
        for name in model.getConss():
            if not(model.getDualsolLinear(name) == 0):
                #print(name,-model.getDualsolLinear(name))
                output['dualVariables'].append([str(name),-model.getDualsolLinear(name)])
        f.write(json.dumps(output))
    else:
        f.write("Problem could not be solved to optimality")

    f.close()

def solveExperiment(directory,expName):
    i = 0
    while True:
        lpName    = directory + '/' + ('%s_%d.lp'%(expName,i))
        graphName = directory + '/' + ('graph_%s_%d.json'%(expName,i))
        if os.path.exists(lpName) and os.path.exists(graphName):
            solveFile(lpName,graphName,directory)
            i += 1
        else:
            break
    
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print(sys.argv)
    else:
        solveExperiment(sys.argv[1],sys.argv[2])
