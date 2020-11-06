import json
import math
import sys

def partitionToStr(prt):
    left = []
    right = []
    for key in prt:
        if prt[key] == 0:
            left.append(key)
        else:
            right.append(key)

    left.sort()
    right.sort()
    return ",".join(left) + " | " + ",".join(right)

def nodeToStr(n,niMax,sumZeta):
    shape = 'ellipse'
    if 'optimum' in n:
        shape = 'pentagon'
    elif not(n['isValid']) or (n['ni'] > niMax):
        shape = 'box'

    ni = str(n['ni']) if 'ni' in n else 'X'
    label = '"%d\n%s\nni=%s/%d\nSumOmega=%.2f\nsumZeta=%.2f\ndiff=%.2f"' % (n['id'],partitionToStr(n['partition']),ni,niMax,n['sumOmega'],sumZeta,sumZeta-n['sumOmega'])

    return 'n%d [shape=%s,label=%s]' % (n['id'],shape, label)

def edgeToStr(i,j,dualVariable):
    return 'n%d -- n%d [label="%s -> %.2f"]' % (i,j,dualVariable[0],dualVariable[1])

def main(fname):
    obs = json.load(open(fname))
    dualVariables = obs['dualVariables']
    niMax = obs['root']['niMax']
    sumZeta = obs['root']['sumZeta']
    nodesToProcess = [obs['root']]
    #print(nodesToProcess[0].keys())
    aux = ['graph G {','graph [ordering="out"];']
    edges = []
    while len(nodesToProcess) > 0:
        node = nodesToProcess.pop()
        level = math.floor(math.log2(node['id']))
        dv = dualVariables[level]
        aux.append(nodeToStr(node,niMax,sumZeta))
        if not(node['leftC'] == None):
            nodesToProcess.append(node['leftC'])
            edges.append(edgeToStr(node['id'],2*node['id'],dv))
        if not(node['rightC'] == None):
            nodesToProcess.append(node['rightC'])
            edges.append(edgeToStr(node['id'],2*node['id']+1,dv))
    aux = aux + edges
    aux.append('}')
    print('\n'.join(aux))

if __name__ == '__main__':
    main(sys.argv[1])
