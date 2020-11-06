import json
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

def nodeToStr(n):
    shape = 'ellipse'
    if 'optimum' in n:
        shape = 'pentagon'
    elif not(n['isValid']):
        shape = 'box'

    ni = str(n['ni']) if 'ni' in n else 'X'
    label = '"%d\n%s\nni=%s"' % (n['id'],partitionToStr(n['partition']),ni)

    return 'n%d [shape=%s,label=%s]' % (n['id'],shape, label)

def edgeToStr(i,j):
    return 'n%d -- n%d' % (i,j)

def main(fname):
    obs = json.load(open(fname))
    nodesToProcess = [obs['root']]
    #print(nodesToProcess[0].keys())
    aux = ['graph G {','graph [ordering="out"];']
    edges = []
    while len(nodesToProcess) > 0:
        node = nodesToProcess.pop()
        aux.append(nodeToStr(node))
        if not(node['leftC'] == None):
            nodesToProcess.append(node['leftC'])
            edges.append(edgeToStr(node['id'],2*node['id']))
        if not(node['rightC'] == None):
            nodesToProcess.append(node['rightC'])
            edges.append(edgeToStr(node['id'],2*node['id']+1))
    aux = aux + edges
    aux.append('}')
    print('\n'.join(aux))

if __name__ == '__main__':
    main(sys.argv[1])
