# -*- coding: UTF-8 -*-

'''
Created on 2016年7月26日

@author: hylovedd
'''
from org_ailab_cluster.association.apriori import aprioriAss
from org_ailab_seg.word2vec.wordVecOpt import wordVecOpt
from org_ailab_tools.cache import ROOT_PATH


def prodFieldW2VModel(modelStoragePath, corpusFilePath, dimension_size=100):
    wordVecOptObj = wordVecOpt(modelStoragePath, size=dimension_size)
    model = wordVecOptObj.initTrainWord2VecModel(corpusFilePath)
    
    return model

# need not
def loadW2VModelFromDisk(modelStoragePath):
    wordVecOptObj = wordVecOpt(modelStoragePath)
    model = wordVecOptObj.loadModelfromFile(modelStoragePath)
    
    return model

def loadEntitiesFromDict(dictPath):
    fr = open(dictPath, 'r')
    entities = []
    entities.extend(line[:line.find('\n')].replace(' ', '/').decode('utf-8') for line in fr)  # clean the newline character
    
    return entities

def freqDataSetFromW2V(modelStoragePath, entities, scanTopN):
    '''
    entity must look like 'XXXX/?'
    entity in entities list must be unique
    '''
    
    wordVecOptObj = wordVecOpt(modelStoragePath)
    w2vModel = loadW2VModelFromDisk(modelStoragePath)  # load model one time, more fast
    
    entFreqSetDic = {}
    for entity in entities:
        if entity not in w2vModel.vocab:
            print(entity + ' not in vocab!')
            continue
        entMSimList = wordVecOptObj.queryMostSimilarWordVec(w2vModel, entity, topN=scanTopN)
        
        freqTuple = (entity,)
        freqProbScoreSum = 0.0
        for msEnt in entMSimList:
            if msEnt[0] in entities:
                freqTuple += (msEnt[0],)
                freqProbScoreSum += msEnt[1]
        if freqProbScoreSum > 0.0:
            freqProbScoreAvg = freqProbScoreSum / (len(freqTuple) - 1)
            entFreqSetDic[freqTuple] = freqProbScoreAvg
#             print('add freqSet -> ' + str(freqTuple) + ': ' + str(freqProbScoreAvg))
    
    return entFreqSetDic

def aprioriAssFromEntities(entFreqSetDic, MinSupport, MinConf, rulesStorePath=None):
    '''
    'rulesStorePath' is path + write type, divided by '='
    '''
    aprioriObj = aprioriAss(minSupport=MinSupport, minConf=MinConf)
    
    assRules = aprioriObj.findAssFromFreqSet(entFreqSetDic, p2p=True)
    
    if rulesStorePath != None:
        writeRules = u''
        for rules in assRules:
            writeRules += (rules[0] + ' -> ' + rules[1] + ': ' + str(rules[2]) + '\n')
        fw = open(rulesStorePath.split(u'=')[0], rulesStorePath.split(u'=')[1])
        fw.write(writeRules)
        fw.close()
    
    return assRules

def relationBtwEntities(modelStoragePath, entityStr1, entityStr2, scanTopN, pureFilterTopN=100):
    '''
    '''
    
    wordVecOptObj = wordVecOpt(modelStoragePath)
    w2vModel = loadW2VModelFromDisk(modelStoragePath)  # load model one time, more fast
    
    if entityStr1 not in w2vModel.vocab or entityStr2 not in w2vModel.vocab:
        print('some entities not in vocab!')
        return []
    
    posEntities = [entityStr1, entityStr2]
    negEntities = []
    # filter out the high score word from entity2, make relation from entities more pure
    if pureFilterTopN > 0:
        pureWordTuples = wordVecOptObj.queryMostSimilarWordVec(w2vModel, entityStr2, pureFilterTopN)
        negEntities.extend(e[0] for e in pureWordTuples)
    relationWordTuples = wordVecOptObj.queryMSimilarVecswithPosNeg(w2vModel, posEntities, negEntities, topN=scanTopN)
    
    return relationWordTuples
    
if __name__ == '__main__':
    modelStoragePath = ROOT_PATH.root_win64 + u'word2vec\\zongheword2vecModel.vector'
    corpusFilePath = ROOT_PATH.root_win64 + u'med_seg\\5医学综合\\'
    
    w2vModel = prodFieldW2VModel(modelStoragePath, corpusFilePath, dimension_size=150)

#     w2vModel = loadW2VModelFromDisk(modelStoragePath)
    
    wordVecOptObj = wordVecOpt(modelStoragePath)
    print(u'train time: ' + str(w2vModel.total_train_time))
    print(u'model dimensionality size: ' + str(w2vModel.vector_size))
    print(u'process corpus num : ' + str(w2vModel.corpus_count))
    wordStr = u'乳腺炎/n'
    print(u'Train model and word vec object: ' + wordStr)
    print(wordStr not in w2vModel.vocab)
    
    if wordStr in w2vModel.vocab:
        queryList = wordVecOptObj.queryMostSimilarWordVec(w2vModel, wordStr, topN=100)
        for e in queryList:
            print e[0], e[1]
            
        print(u'word in vector space:----------------------------------------------------')
        vector = wordVecOptObj.getWordVec(w2vModel, wordStr)
        print(vector)
