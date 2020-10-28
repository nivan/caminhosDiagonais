import math
import random
import collections
import sympy as sym
import binSolver
import util
import sys
import os
import json

def getIndices(v):
  name = str(v)[3:]
  index = name.find('_')
  i = int(name[0:index])
  j = int(name[(index+1):])
  return (i,j)

def positionVertices(equations,partition):
  for key in equations:
    if equations[key] == 0 or equations[key] == 1:
      i,j = getIndices(key)
      if i in partition and not(j in partition):
        #position j
        partition[j] = (partition[i] + equations[key])%2
      elif j in partition and not(i in partition):
        #position i
        partition[i] = (partition[j] + equations[key])%2
  return partition

def createVariable(i,j):
    return sym.Symbol('xa_%d_%d' % (i,j))

def createVariables(varDict,indices):
    for index in indices:
        if not(index in varDict):
            varDict[tuple(index)] = createVariable(index[0],index[1])

def isSolutionValid(s):
  if s == []:
    return True
  else:
    for key in s:
      value = s[key]
      if not(isinstance(value, sym.numbers.Zero) or isinstance(value, sym.numbers.One) or isinstance(value, sym.symbol.Symbol)):
        return False
    #
    return True

def normalizeSolution(s):
  if isSolutionValid(s):
    return s
  else:
    return s

def validateNode(node,variables):
    equations = node['system'][0]
    vars = [variables[t] for t in node['system'][1]]
    solution = binSolver.solveSystem(equations,vars)
    #
    if len(solution) > 0:
      aux = sym.solve(equations,vars)
      if len(aux) > 0:
        for key in aux:
          if not (key in solution):
            solution[key] = aux[key]
    #
    node['solution'] = solution
    node['isValid'] = (len(solution) > 0)

def buildSeedSystem(seed,variables):
    equations = []
    myVars    = set()
    for i in seed:
        for j in seed:
            if i >= j:
                continue
            value = 1
            if seed[i] == seed[j]:
                value = 0
            #
            newVariable = sym.Symbol('xa_%d_%d' % (i,j))
            variables[(i,j)] = newVariable
            myVars.add((i,j))
            
            equations.append(newVariable-value)
    return [equations,myVars]

def computeNi(graph,partition):
  counter = 0
  for edge in graph:
    if (edge[0] in partition) and (edge[1] in partition) and (partition[edge[0]] == partition[edge[1]]):
      counter += 1
  return counter

def buildTree(seed,dualVariables,inequalities,nuOmega,h,inputGraph,debug):
    debug = False
    niMax = len(inputGraph) - nuOmega
    variables    = {}
    levSize      = {}
    visitedNodes = {}
    root = {'seed': seed, 'partition':seed, 'isValid': False, 
          'yaccum':0, 'xaccum':0,'id':1,'leftC':None,'rightC':None,'ni':computeNi(inputGraph,seed),
          'system':buildSeedSystem(seed,variables), 'newVariables':[]}
    
    #print(root['system'])
    nodesToProcess = []
    nodesToProcess.append(root)
    
    while len(nodesToProcess) > 0:
        currentNode = nodesToProcess.pop()
        #
        if not(currentNode['id'] in visitedNodes):
          visitedNodes[currentNode['id']] = 1
          level = math.floor(math.log2(currentNode['id']))
          if not(level in levSize):
            levSize[level] = 1
          else:
            levSize[level] += 1

        # check inconsistencies
        if debug:
            print(currentNode['id'],currentNode['system'])
            halt
        if not (currentNode['isValid']):
            validateNode(currentNode,variables)

        #exchance system by its solution
        positionVertices(currentNode['solution'],currentNode['partition'])
        currentNode['ni'] = computeNi(inputGraph,currentNode['partition'])

        if len(currentNode['partition']) == 4*h:
          if debug:
            print('****** FOUND TERMINAL NODE')
            print('     Terminal: ', currentNode['ni'],niMax,currentNode['system'],currentNode['solution'],currentNode['partition'])
          
          if currentNode['ni'] > niMax:
            continue
          else:
            #position last node
            #
            print("  Testing Terminal Node")
            partTest = dict(currentNode['partition'])
            partTest[4*h+1] = 0
            valueLeft  = computeNi(inputGraph,partTest)
            cutSize = len(inputGraph) - valueLeft
            if cutSize == nuOmega:
              #found solution
              currentNode['partition'] = partTest
              return (True,currentNode,levSize,root)
            #
            partTest[4*h+1] = 1
            valueRight = computeNi(inputGraph,partTest)
            cutSize = len(inputGraph) - valueRight
            if cutSize == nuOmega:
              #found solution
              currentNode['partition'] = partTest
              return (True,currentNode,levSize,root)
            #
            continue

        #
        if debug:    
          print('     Middle: ', currentNode['system'],currentNode['solution'],currentNode['partition'])
        
        #
        currentNode['system'][0] = [sym.Eq(t,currentNode['solution'][t]) for t in currentNode['solution']]

        #        
        if debug:
          print('     After: ', currentNode['ni'],niMax, currentNode['system'],currentNode['solution'])

        #  
        if currentNode['isValid'] and (currentNode['ni'] <= niMax):
            #
            id          = currentNode['id']
            levelOnTree = math.floor(math.log2(id))
            dualVar     = dualVariables[levelOnTree]
            inequality  = inequalities[dualVar[0]]
            pairs       = [tuple(sorted(t)) for t in inequality['variables']]
            signal      = inequality['signs']
            createVariables(variables,pairs)
            #
            if currentNode['leftC'] == None:
                # go to left
                ## create left node
                #
                eqRightSide = None
                if inequality['rightSide'] == 2:
                    eqRightSide = 0
                else:
                    eqRightSide = -2
                
                #
                newEquation  = None
                newVariables = set([])
                if inequality['entryType'] == 3:
                    newEquation = signal[0]*variables[pairs[0]]+signal[1]*variables[pairs[1]]+signal[2]*variables[pairs[2]]-eqRightSide
                    newVariables.add(pairs[0])
                    newVariables.add(pairs[1])
                    newVariables.add(pairs[2])
                else:
                    newEquation = signal[0]*variables[pairs[0]]+signal[1]*variables[pairs[1]]+signal[2]*variables[pairs[2]]+signal[3]*variables[pairs[3]]-eqRightSide
                    newVariables.add(pairs[0])
                    newVariables.add(pairs[1])
                    newVariables.add(pairs[2])
                    newVariables.add(pairs[3])
                
                newSystem = []
                newSystem.append(currentNode['system'][0][:])
                newSystem.append(currentNode['system'][1].copy())
                notSeenYetVars = [t for t in newVariables if not(t in newSystem[1])]
                newSystem[0].append(newEquation)
                newSystem[1] = newSystem[1].union(newVariables)
                #
                leftNode = {'seed': seed, 'partition':dict(currentNode['partition']), 'isValid': False,'yaccum':0, 
                            'xaccum':0,'id':2*id,'leftC':None,'rightC':None, 'system':newSystem,'newVariables':notSeenYetVars}
                currentNode['leftC'] = leftNode 
                ## push currentNode
                nodesToProcess.append(currentNode)
                ## push leftNode
                nodesToProcess.append(leftNode)
            else:
                #go to right
                #
                eqRightSide = None
                if inequality['rightSide'] == 2:
                    eqRightSide = 2
                else:
                    eqRightSide = 0
                
                #
                newEquation  = None
                newVariables = set([])
                if inequality['entryType'] == 3:
                    newEquation = signal[0]*variables[pairs[0]]+signal[1]*variables[pairs[1]]+signal[2]*variables[pairs[2]]-eqRightSide
                    newVariables.add(pairs[0])
                    newVariables.add(pairs[1])
                    newVariables.add(pairs[2])
                else:
                    newEquation = signal[0]*variables[pairs[0]]+signal[1]*variables[pairs[1]]+signal[2]*variables[pairs[2]]+signal[3]*variables[pairs[3]]-eqRightSide
                    newVariables.add(pairs[0])
                    newVariables.add(pairs[1])
                    newVariables.add(pairs[2])
                    newVariables.add(pairs[3])
                
                #newSystem = currentNode['system'][:]
                newSystem[0].append(newEquation)
                newSystem[1] = newSystem[1].union(newVariables)
                
                newSystem = []
                newSystem.append(currentNode['system'][0][:])
                newSystem.append(currentNode['system'][1].copy())
                newSystem[0].append(newEquation)
                notSeenYetVars = [t for t in newVariables if not(t in newSystem[1])]
                newSystem[1] = newSystem[1].union(newVariables)
                
                
                ## create rightNode
                rightNode = {'seed': seed, 'partition':dict(currentNode['partition']), 'isValid': False,'yaccum':0, 
                            'xaccum':0,'id':2*id+1,'leftC':None,'rightC':None, 'system':newSystem,'newVariables':notSeenYetVars}
                currentNode['rightC'] = rightNode
                ## push rightNode
                nodesToProcess.append(rightNode)
    return (False,None,levSize,root)

def getNodeDict(_node):
  nodeDict = {}
  nodesToProcess = []
  nodesToProcess.append(_node)
    
  while len(nodesToProcess) > 0:
    currentNode = nodesToProcess.pop()
    #to make it serializable
    currentNode['systemVariables'] = currentNode['system'][1]
    currentNode['system'] = [str(x) for x in currentNode['system'][0]]
    currentNode.pop('solution',None)
    currentNode.pop('newVariables',None)
    currentNode.pop('systemVariables',None)
    currentNode.pop('yaccum',None)
    currentNode.pop('xaccum',None)
    currentNode.pop('xaccum',None)
    currentNode['partition'] = { int(key):int(currentNode['partition'][key]) for key in currentNode['partition']}
    
    
    #
    nodeDict[currentNode['id']] = currentNode
    if currentNode['leftC']:
      nodesToProcess.append(currentNode['leftC'])

    if currentNode['rightC']:
      nodesToProcess.append(currentNode['rightC'])

  return nodeDict

def mainAlgorithm(dualVariables,inequalities,nuOmega,h,inputGraphEdges,inputGraphName,saveFiles,verbose,directory='./'):
    seeds = [{1:0,2:0,(4*h):0},
             {1:0,2:0,(4*h):1},
             {1:0,2:1,(4*h):0},
             {1:0,2:1,(4*h):1}]
    
    for seed in seeds:
        #build root
        print(' -------- Processing Seed',seed)
        found,solution,treeLevels,rootNode = buildTree(seed,dualVariables,inequalities,nuOmega,h,inputGraphEdges,verbose)
        #print(treeLevels)
        maxWidth = treeLevels[max(treeLevels, key=treeLevels.get)]
        print(" ******** Max width: ",maxWidth)

        if saveFiles:
          myNodes = getNodeDict(rootNode)
          experiment = {'seed':seed,'treeWidths':treeLevels,'nuOmega':nuOmega,'root':rootNode}
          #print(experiment)
          try:
            os.mkdir('%s/%s'%(directory,inputGraphName))
          except:
            pass
          outfile = open(directory+('%s/tree_%s_%d_%d%d%d.json' %(inputGraphName,inputGraphName,nuOmega,seed[1],seed[2],seed[4*h])),'w')
          json.dump(experiment, outfile)
          outfile.close()

        if found:
          return (True,solution)
    
    return (False,None)

def solveFileInput(inputFile,directory):
    problemDefinition = json.load(open(inputFile))

    name          = problemDefinition['name']
    vertices      = problemDefinition['vertices']
    edges         = problemDefinition['edges']
    dualVariables = problemDefinition['dualVariables']

    #
    h             = math.ceil((vertices-1)/4.0)
    paths = util.generateAllPaths(h)
    constraints = {}
    for path in paths:
        result = util.generateConstraints(path,h)
        for key in result:
            constraints[key] = result[key]

    #
    #print(constraints)
    currentNi = len(edges)
    verbose = False
    
    while currentNi >= 0:
        print('Current Ni',currentNi)
        result,node = mainAlgorithm(dualVariables,constraints,currentNi,h,edges,name,True,verbose,directory)
        if result:
            print('============RESULT FOUND ============',
                  "\n","Partition: ", node['partition'],'\n',
                  'MAXCUT: ',(len(edges)-computeNi(edges,node['partition'])))
            break
        else:
            currentNi -= 1

def solveExperiment(directory,expName):
  i = 0
  while True:
    dualName = directory + '/dualSolution_' + ('%s_%d.json'%(expName,i))
    if os.path.exists(dualName):
      solveFileInput(dualName,directory)
      i += 1
    else:
      break
  
if __name__ == '__main__':
  if len(sys.argv) != 3:
    print(sys.argv)
  else:
    solveExperiment(sys.argv[1],sys.argv[2])
