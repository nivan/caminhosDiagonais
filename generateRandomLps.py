import util
import sys
import json

def main(numGraphs,experimentName,numVertices,density,outputDir):

    for i in range(numGraphs):
        graph = util.generateRandomGraph(numVertices,density)
        name = '%s_%d' % (experimentName,i)
        util.generateLPFile(graph,numVertices, outputDir+'/%s_%d.lp' % (experimentName,i))
        jsonGraph = {'edges':graph,'numVertices':numVertices,'name':name}
        auxName = 'graph_%s_%i.json'%(experimentName,i)
        f = open(outputDir + '/' + auxName,'w')
        f.write(json.dumps(jsonGraph))
if __name__ == '__main__':
    if len(sys.argv) != 6:
        print(sys.argv)
    else:
        main(int(sys.argv[1]),sys.argv[2],int(sys.argv[3]),float(sys.argv[4]),sys.argv[5])
