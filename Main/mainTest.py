# -*- coding: utf-8 -*-

import sys
#sys.path.append('utils')

### PARSER ###
sys.path.append('parserInterface')
from parserWrapper import parse
from sysUtil import printMsg, printResult

### TMP ###
from maltImporter import MaltImporter
qFilePath = '../Data/q.q';
qParsedFilePath = '../Data/q_parsed.qp';

ourQuestions = MaltImporter().importMaltOutputs(qFilePath, qParsedFilePath)

### IR ###
sys.path.append('irInterface')
from indriHandler import singleIndriQuery
from queryBuilder import buildQueryFromQuestionData
from queryBuilder import buildIndriQuerySingle
from indriDocFetch import getDoc
from translationInterface import translationWrapper as tw

### Syntactic Analysis ###
sys.path.append('analysisInterface')
from analyzer import *

debug=True


def mainParse(qText):
    return parse(qText, debug)

def mainAnalyze(qObj):
    analyzer = QuestionAnalysis(qObj)

    forwGlass = Glass(ourQuestions, backwards=False)
    backGlass = Glass(ourQuestions, backwards=True)

    qFocus, qMod, qClass, qPnoun = analyzer.fullAnalysis(backGlass, forwGlass)

    return qFocus, qMod, qClass, qPnoun

def mainBuildQuery(qObj):
    return buildQueryFromQuestionData(qObj)

def mainQuerySingle(paramFile="singleFromWeb", count=5):
    return singleIndriQuery(paramFile, count)

def mainRelated(docIDs):
    titles = []
    texts = []

    for dID in docIDs:
        dTitle, dText = getDoc(dID)
        titles.append(dTitle)
        texts.append(dText)

    return titles, texts

def runPipeline(questionInput):
    """
    TAKE THE QUESTION
    """
    if debug:
        printMsg('Obtaining Question')

    #qText = "Türkiye Şampiyonluğu'nu kazandıktan sonra 80 kg serbestte 1980 Dünya Şampiyonluğu'nu elde etti."
#qText = sys.argv[1]
    qText = questionInput

    if debug:
        printResult('Success', qText)

    """
    BUILD THE QUESTION OBJECT
    """
    qstnObj = parse(qText, debug)

    """
    ANALYSE THE QUESTION
    """

    if debug:
        printMsg('Running Analysis')

    qF, qM, qC, qP = mainAnalyze(qstnObj)

    if debug:
        printMsg('Analysis DONE')

    print('Focus : ' + qF)
    print('Mod : ' + qM)
    print('Class : ' + qC)
    print('Pnoun : ' + qP)

    translation_cand = " ".join([ qF, qM, qC, qP])
    translation = tw.translate(translation_cand)

    print('[%s] -> %s' %(translation_cand,translation))

    #focus, mod = returnFocusMod(
    """
    BUILD THE QUERY
    """

    if debug:
        printMsg('Building the Query')

    mainBuildQuery(qstnObj)

    """
    QUERY THE IR
    """

    docs = mainQuerySingle()

    print(docs)

    docTitle, docText = getDoc(docs[0])

    print("TITLE: " + docTitle)
    print("TEXT: \n\n" + docText)

if 'test' in sys.argv:
    qText = "Türkiyenin en büyük ovası hangisidir"
    runPipeline(qText)
