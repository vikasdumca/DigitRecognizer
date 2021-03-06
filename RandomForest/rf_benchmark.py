from numpy import *
from math import log
import operator
import copy

def calcShannonEnt(dataSet):
    numEntries = len(dataSet)
    labelCounts = {}
    for featVec in dataSet:
        currentLabel = featVec[-1]
        if currentLabel not in labelCounts.keys(): labelCounts[currentLabel] = 0
        labelCounts[currentLabel] += 1
    shannonEnt = 0.0
    for key in labelCounts:
        prob = float(labelCounts[key])/numEntries
        shannonEnt -= prob * log(prob, 2) # log base 2
    return shannonEnt

def splitDataSet(dataSet, axis, value):
    retDataSet = []
    for featVec in dataSet:
        if featVec[axis] == value:
            reducedFeatVec = featVec[:axis]     # chop out axis used for splitting
            reducedFeatVec.extend(featVec[axis+1:])
            retDataSet.append(reducedFeatVec)
    return retDataSet


def chooseBestFeatureToSplit(dataSet):
    print 'best fit..'
    numFeatures = len(dataSet[0]) - 1      
    baseEntropy = calcShannonEnt(dataSet)
    bestInfoGain = 0.0; bestFeature = -1
    for i in range(numFeatures):        
        featList = [example[i] for example in dataSet]
        uniqueVals = set(featList)       
        newEntropy = 0.0
        for value in uniqueVals:
            subDataSet = splitDataSet(dataSet, i, value)
            prob = len(subDataSet)/float(len(dataSet))
            newEntropy += prob * calcShannonEnt(subDataSet)
        infoGain = baseEntropy - newEntropy     
        if (infoGain > bestInfoGain):       
            bestInfoGain = infoGain         
            bestFeature = i
    return bestFeature                      


def majorityCnt(classList):
    classCount={}
    for vote in classList:
        if vote not in classCount.keys(): classCount[vote] = 0
        classCount[vote] += 1
    sortedClassCount = sorted(classCount.iteritems(), key=operator.itemgetter(1), reverse=True)
    return sortedClassCount[0][0]

def createTree(dataSet,labels):
    classList = [example[-1] for example in dataSet]


    if classList.count(classList[0]) == len(classList):
        return classList[0]
    if len(dataSet[0]) == 1: 
        return majorityCnt(classList)


    bestFeat = chooseBestFeatureToSplit(dataSet)
    bestFeatLabel = labels[bestFeat]
    myTree = {bestFeatLabel:{}}

    print bestFeat

    del(labels[bestFeat])
    featValues = [example[bestFeat] for example in dataSet]


    uniqueVals = set(featValues)
    for value in uniqueVals:
        subLabels = labels[:]       
        myTree[bestFeatLabel][value] = createTree(splitDataSet(dataSet, bestFeat, value),subLabels)
    return myTree


def classify(inputTree,featLabels,testVec):
    firstStr = inputTree.keys()[0]
    secondDict = inputTree[firstStr]
    featIndex = featLabels.index(firstStr)
    key = testVec[featIndex]
    valueOfFeat = secondDict[key]

    if isinstance(valueOfFeat, dict):
        classLabel = classify(valueOfFeat, featLabels, testVec)
    else: classLabel = valueOfFeat
    return classLabel


def createDataSet(train_file):
    dataSet = []
    f=open(train_file , 'r')
    labels=f.readline().split(',')
    del(labels[0])
    labels[783] = labels[783].split('\r\n')[:1][0]
    for line in f:
        l=line.split(',')
        l[784]=l[784].split('\r\n')[:1][0]
        l.append(l[0])
        del(l[0])
        dataSet.append(l)
    return dataSet, labels


def main():
    dataSet,labels = createDataSet('train.csv')
    labels1=copy.deepcopy(labels)



    print 'creating tree ....'
    mytree = createTree(dataSet, labels1)

    f=open('test.csv')
    out=open('rf_benchmark.csv', 'w')
    f.readline()
    out.write('ImageId,Label\n')

    i=1
    reject = 0
    for line in f:
        line=line.split(',')
        line[783]=line[783].split('\r\n')[:1][0]
        p_res=1
        try:
            p_res = classify(mytree,labels,line)
        except Exception:
            p_res =  -1
            reject+=0

        out.write('%d,%s\n'%(i,p_res))
        print ('classifiedDigit is : %s'%p_res)
        i=i+1

    print reject
if __name__=='__main__':
    main()
