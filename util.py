import math
import random
import collections
import sympy as sym
from sympy import FiniteSet

def normalizeEntry(entry):
    _min = entry[0]
    _index = 0
    
    for i in range(len(entry)):
        if entry[i] < _min:
            _min = entry[i]
            _index = i
    
    return entry[_index:] + entry[0:_index]

def generateFirstPath(h):
    #
    numNewEntries = 8*h-2
    first   = [1,2,4*h]
    seed    = first + [3]
    result  = [first,seed]
    counter = 0
    #
    for t in range(4*h-4):
        newEntry = [t for t in result[-1]]
        if counter % 2 == 0:
            newEntry[1] = (newEntry[1] + 2)%(4*h)
        else:
            newEntry[3] = (newEntry[3] + 2)%(4*h)
        result.append(newEntry)
        counter+=1
    #
    mid1 = [1,4*h,4*h-1]
    result.append(mid1)
    ##########################
    #
    mid2    = [1,4*h,2]
    result.append(mid2)
    seed    = mid2 + [4*h-1]
    result.append(seed)
    counter = 0
    for t in range(4*h-4):
        newEntry = [t for t in result[-1]]
        if counter % 2 == 0:
            newEntry[1] = (newEntry[1] - 2)%(4*h)
        else:
            newEntry[3] = (newEntry[3] - 2)%(4*h)
        result.append(newEntry)
        counter+=1
    
    #
    last = [1,2,3]
    result.append(last)
    
    return [normalizeEntry(t) for t in result]
  
def step(t,h,m):
    result = (t+2)%m
    return 4*h if result == 0 else result 

def processEntry(entry, h, m):
    return [step(t,h,m) for t in entry]

def generateAllPaths(h):
    numPaths = 2*h
    modulo   = 4*h
    paths    = []

    #first path
    firstPath = generateFirstPath(h)
    paths = []
    paths.append(firstPath)

    #
    for i in range(1,numPaths):
        prevPath = paths[i-1]
        newPath = [processEntry(t,h,modulo) for t in prevPath]
        paths.append([normalizeEntry(t) for t in newPath])
    #
    return paths   

####################################################

def getSign(num):
    return ('+' if num == 1 else '-')

def getVariableName(indices):
    newIndices = indices
    return 'xa_%d_%d' % (newIndices[0],newIndices[1])

def constraintToString(constraint):
    signs     = [getSign(t) for t in constraint['signs']]
    variables = [getVariableName(t) for t in constraint['variables']]
    aux       = ''
    for i in range(len(signs)):
        aux += (signs[i] + ' ' + variables[i] + ' ')
        
    if constraint['entryType'] == 3:
        i = constraint['variables'][0][0]
        j = constraint['variables'][1][0]
        k = constraint['variables'][2][0]
        aux += '+ xo_%d_%d_%d ' % (i,j,k) 
    elif constraint['entryType'] == 2:
        i = constraint['variables'][0][0]
        j = constraint['variables'][0][1]
        aux += '+ xo_%d_%d ' % (i,j) 
    else:
        i = constraint['variables'][0][0]
        j = constraint['variables'][1][0]
        k = constraint['variables'][2][0]
        l = constraint['variables'][3][0]
        aux += '+ xo_%d_%d_%d_%d ' % (i,j,k,l) 
    
    return constraint['name'] + ': ' +  aux + ' <= ' + str(constraint['rightSide'])

import collections 
def generateConstraints (path,h):
  inequalities = collections.OrderedDict()
  for entry in path:
    if len(entry) == 3:
      i = entry[0]
      j = entry[1]
      k = entry[2]
      #yuijkn0: + xij + xjk + xki + xoijk <= 2
      name = "yu_%d_%d_%dn0" % (i,j,k)
      inequalities[name] = {'name':name,"type":"CD","entryType":3,"variables":[[i,j],[j,k],[k,i]],"signs":[1,1,1],"rightSide":2}
      #yuijkp1: + xij - xjk - xki + xoijk <= 0
      name = "yu_%d_%d_%dp1" % (i,j,k)
      inequalities[name] = {'name':name,"type":"CD","entryType":3,"variables":[[i,j],[j,k],[k,i]],"signs":[1,-1,-1],"rightSide":0}
      #yuijkp2: - xij + xjk - xki + xoijk <= 0
      name = "yu_%d_%d_%dp2" % (i,j,k)
      inequalities[name] = {'name':name,"type":"CD","entryType":3,"variables":[[i,j],[j,k],[k,i]],"signs":[-1,1,-1],"rightSide":0}
      #yuijkp3: - xij - xjk + xki + xoijk <= 0
      name = "yu_%d_%d_%dp3" % (i,j,k)
      inequalities[name] = {'name':name,"type":"CD","entryType":3,"variables":[[i,j],[j,k],[k,i]],"signs":[-1,-1,1],"rightSide":0}
    else:
      i = entry[0]
      j = entry[1]
      k = entry[2]
      l = entry[3]
      #yuijkln1: - xij + xjk + xkl + xli + xoijkl <= 2
      name = "yu_%d_%d_%d_%dn1" % (i,j,k,l)
      inequalities[name] = {'name':name,"type":"CD","entryType":4,"variables":[[i,j],[j,k],[k,l],[l,i]],"signs":[-1,1,1,1],"rightSide":2}
      #yuijkln2: + xij - xjk + xkl + xli + xoijkl <= 2
      name = "yu_%d_%d_%d_%dn2" % (i,j,k,l)
      inequalities[name] = {'name':name,"type":"CD","entryType":4,"variables":[[i,j],[j,k],[k,l],[l,i]],"signs":[1,-1,1,1],"rightSide":2}
      #yuijkln3: + xij + xjk - xkl + xli + xoijkl <= 2
      name = "yu_%d_%d_%d_%dn3" % (i,j,k,l)
      inequalities[name] = {'name':name,"type":"CD","entryType":4,"variables":[[i,j],[j,k],[k,l],[l,i]],"signs":[1,1,-1,1],"rightSide":2}
      #yuijkln4: + xij + xjk + xkl - xli + xoijkl <= 2
      name = "yu_%d_%d_%d_%dn4" % (i,j,k,l)
      inequalities[name] = {'name':name,"type":"CD","entryType":4,"variables":[[i,j],[j,k],[k,l],[l,i]],"signs":[1,1,1,-1],"rightSide":2}
      #yuijklp1: +xij - xjk - xkl - xli + xoijkl <= 0
      name = "yu_%d_%d_%d_%dp1" % (i,j,k,l)
      inequalities[name] = {'name':name,"type":"CD","entryType": 4, "variables": [[i,j],[j,k],[k,l],[l,i]], "signs": [1,-1,-1,-1], "rightSide": 0}
      #yuijklp2: -xij + xjk - xkl - xli + xoijkl <= 0
      name = "yu_%d_%d_%d_%dp2" % (i,j,k,l)
      inequalities[name] = {'name':name,"type":"CD","entryType": 4, "variables": [[i,j],[j,k],[k,l],[l,i]], "signs": [-1,1,-1,-1], "rightSide": 0}
      #yuijklp3: -xij - xjk + xkl - xli + xoijkl <= 0
      name = "yu_%d_%d_%d_%dp3" % (i,j,k,l)
      inequalities[name] = {'name':name,"type":"CD","entryType": 4, "variables": [[i,j],[j,k],[k,l],[l,i]], "signs": [-1,-1,1,-1], "rightSide": 0}
      #yuijklp4: -xij - xjk - xkl + xli + xoijkl <= 0
      name = "yu_%d_%d_%d_%dp4" % (i,j,k,l)
      inequalities[name] = {'name':name,"type":"CD","entryType": 4, "variables": [[i,j],[j,k],[k,l],[l,i]], "signs": [-1,-1,-1,1], "rightSide": 0}
  
  #central triangles
  for pp in range(4*h):
    i = (pp+1)%(4*h)
    i = 4*h if i == 0 else i
    j = 4*h+1
    k = (i+1)%(4*h) 
    k = 4*h if k == 0 else k
    indices = normalizeEntry([i,j,k])
    i,j,k = indices
    #yuijkn0: + xij + xjk + xki + xoijk <= 2
    name = "yu_%d_%d_%dn0" % (i,j,k)
    inequalities[name] = {'name':name,"type":"tripla","entryType":3,"variables":[[i,j],[j,k],[k,i]],"signs":[1,1,1],"rightSide":2}
    #yuijkp1: + xij - xjk - xki + xoijk <= 0
    name = "yu_%d_%d_%dp1" % (i,j,k)
    inequalities[name] = {'name':name,"type":"tripla","entryType":3,"variables":[[i,j],[j,k],[k,i]],"signs":[1,-1,-1],"rightSide":0}
    #yuijkp2: - xij + xjk - xki + xoijk <= 0
    name = "yu_%d_%d_%dp2" % (i,j,k)
    inequalities[name] = {'name':name,"type":"tripla","entryType":3,"variables":[[i,j],[j,k],[k,i]],"signs":[-1,1,-1],"rightSide":0}
    #yuijkp3: - xij - xjk + xki + xoijk <= 0
    name = "yu_%d_%d_%dp3" % (i,j,k)
    inequalities[name] = {'name':name,"type":"tripla","entryType":3,"variables":[[i,j],[j,k],[k,i]],"signs":[-1,-1,1],"rightSide":0}

  #centrail digonos
  if False: #removendo digonos
    for i in range(4*h):
      #
      name = "yu_" + str(i+1) + '_' + str(4*h+1) +"p1"
      inequalities[name] = {'name':name,"type":"digonos","entryType": 2, "variables": [[i+1,4*h+1],[4*h+1,i+1]], "signs": [1,-1], "rightSide": 0}
      #
      name = name = "yu_" + str(i+1) + '_' + str(4*h+1) +"n1"
      inequalities[name] = {'name':name,"type":"digonos","entryType": 2, "variables": [[i+1,4*h+1],[4*h+1,i+1]], "signs": [-1,1], "rightSide": 0}
    
  #
  return inequalities

def generateXos(constraints):
  variables = {}
  for key in constraints:
    constraint = constraints[key]
    #
    if constraint['entryType'] == 3:
      i = constraint['variables'][0][0]
      j = constraint['variables'][1][0]
      k = constraint['variables'][2][0]
      name = 'xo_%d_%d_%d' % (i,j,k)
      if not (name in variables):
        variables[name] = 1
    elif constraint['entryType'] == 2:
      i = constraint['variables'][0][0]
      j = constraint['variables'][0][1]
      name = 'xo_%d_%d' % (i,j)
      if not (name in variables):
        variables[name] = 1
    else:
      i = constraint['variables'][0][0]
      j = constraint['variables'][1][0]
      k = constraint['variables'][2][0]
      l = constraint['variables'][3][0]
      name = 'xo_%d_%d_%d_%d' % (i,j,k,l)
      if not (name in variables):
        variables[name] = 1

  return variables.keys()
 


def generateBounds(constraints):
  variables = {}
  resultXa = [];
  resultXo = []
  for key in constraints:
    constraint = constraints[key]
    for variable in constraint['variables']:
      name = getVariableName(variable)
      if not (name in variables):
        variables[name] = 1
        resultXa.append(name + ' free')
    #
    if constraint['entryType'] == 3:
      i = constraint['variables'][0][0]
      j = constraint['variables'][1][0]
      k = constraint['variables'][2][0]
      name = 'xo_%d_%d_%d' % (i,j,k)
      if not (name in variables):
        variables[name] = 1
        resultXo.append('xo_%d_%d_%d >= 0' % (i,j,k))
    elif constraint['entryType'] == 2:
      i = constraint['variables'][0][0]
      j = constraint['variables'][0][1]
      name = 'xo_%d_%d' % (i,j)
      if not (name in variables):
        variables[name] = 1
        resultXo.append('xo_%d_%d >= 0' % (i,j))
    else:
      i = constraint['variables'][0][0]
      j = constraint['variables'][1][0]
      k = constraint['variables'][2][0]
      l = constraint['variables'][3][0]
      name = 'xo_%d_%d_%d_%d' % (i,j,k,l)
      if not (name in variables):
        variables[name] = 1
        resultXo.append('xo_%d_%d_%d_%d >= 0' % (i,j,k,l)) 

  return (resultXa,resultXo)

def testConstraints(h):
  paths = generateAllPaths(h)
  constraints = {}
  for path in paths:
    result = generateConstraints(path,h)
    for key in result:
      constraints[key] = result[key]
  constraintStrings = [constraintToString(constraints[key]) for key in constraints]
  print(len(paths),len(constraints))
  if False:
    for t in (constraintStrings):
      print(t)
    print('\n')
    print('bounds')
    print('\n')
    bounds = generateBounds(constraints)  
    for t in bounds[0]:
      print(t)
    for t in bounds[1]:
      print(t)

def generateRandomGraph(numVertices,density):
  edges = []
  for i in range(numVertices):
    for j in range(i+1,numVertices):
      if random.random() <= density:
        edges.append([i+1,j+1])
  return edges

def getObjectiveFunctionStr(graph,xos):
  
  names = [getVariableName(t) for t in graph]
  objective = " + ".join(names + xos)  
  
  return objective

def generateLPStr(graph,numVertices):
    h = math.ceil((numVertices-1)/4.0)
    #
    paths = generateAllPaths(h)
    constraints = {}
    for path in paths:
        result = generateConstraints(path,h)
        for key in result:
            constraints[key] = result[key]

    #
    constraintStrings1 = [constraintToString(constraints[key]) for key in constraints if constraints[key]['type'] == "CD"]
    constraintStrings2 = [constraintToString(constraints[key]) for key in constraints if constraints[key]['type'] == "tripla"]
    constraintStrings3 = [constraintToString(constraints[key]) for key in constraints if constraints[key]['type'] == "digonos"]
    constraintStrings = constraintStrings1 + constraintStrings2 + constraintStrings3

    xos = list(generateXos(constraints))
    #
    getObjectiveFunctionStr(graph,xos)
    #
    print("Maximize "+ getObjectiveFunctionStr(graph,xos))
    print('\n')
    print('subject to')
    print('\n')
    for t in (constraintStrings):
        print(t)
    print('\n')
    print('\n')
    print('bounds')
    print('\n')
    bounds = generateBounds(constraints)  
    for t in bounds[0]:
        print(t)
    for t in bounds[1]:
        print(t)
    print('end')

def generateLPFile(graph,numVertices, outputFilename):
    h = math.ceil((numVertices-1)/4.0)
    #
    paths = generateAllPaths(h)
    constraints = {}
    for path in paths:
        result = generateConstraints(path,h)
        for key in result:
            constraints[key] = result[key]

    #
    constraintStrings1 = [constraintToString(constraints[key]) for key in constraints if constraints[key]['type'] == "CD"]
    constraintStrings2 = [constraintToString(constraints[key]) for key in constraints if constraints[key]['type'] == "tripla"]
    constraintStrings3 = [constraintToString(constraints[key]) for key in constraints if constraints[key]['type'] == "digonos"]
    constraintStrings = constraintStrings1 + constraintStrings2 + constraintStrings3

    xos = list(generateXos(constraints))
    #
    getObjectiveFunctionStr(graph,xos)
    #
    outFile = open(outputFilename,'w')
    outFile.write("Maximize "+ getObjectiveFunctionStr(graph,xos))
    outFile.write('\n')
    outFile.write('subject to')
    outFile.write('\n')
    for t in (constraintStrings):
        outFile.write(t)
        outFile.write('\n')
    outFile.write('\n')
    outFile.write('\n')
    outFile.write('bounds')
    outFile.write('\n')
    bounds = generateBounds(constraints)  
    for t in bounds[0]:
        outFile.write(t)
        outFile.write('\n')
    for t in bounds[1]:
        outFile.write(t)
        outFile.write('\n')
    outFile.write('end')
    outFile.write('\n')
    outFile.close()
    
if __name__ == '__main__':
    testConstraints(2)
