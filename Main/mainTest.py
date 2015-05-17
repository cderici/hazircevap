# -*- coding: utf-8 -*-

import sys, os
#sys.path.append('utils')

### PARSER ###
sys.path.append('parserInterface')
from parserWrapper import parse
from sysUtil import printMsg, printResult
import cPickle as pickle

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

### TRANSLATION ###
from translationInterface import translationWrapper as tw
from clirInterface import retrieve_from_english

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

    qFocus, qFocusRoots, qMod, qClass, qPnoun, qSubj = analyzer.fullAnalysis(backGlass, forwGlass)

    return qFocus, qFocusRoots, qMod, qClass, qPnoun, qSubj

def mainEval(questionList, parsedBefore, dataPath, topDocs=5):
    focusListFoundT = []
    modListFoundT = []
    classListFound = []
    transPhraseList = []
    transList = []
    relatedDocs = []

    count = 0 # will be used to index pickle dumps

    if parsedBefore:
        pickleParseList = pickle.load(open(parsedBefore, "rb"))
    else:
        pickleParseList = []

    transPath = dataPath[0:len(dataPath)-5]+".translations"
    alreadyTranslated = os.path.isfile(transPath)
    if alreadyTranslated:
        pickleTransList = pickle.load(open(transPath, "rb"))
    else:
        pickleTransList = []

    for question in questionList:

        #qstn = Question(qText, qParts)
        if parsedBefore:
            # grap the parts from the parsedBefore directory
            ## load pickle list
            qParts = pickleParseList[count]

            qObj = Question(question, qParts)
        else:
            qObj = mainParse(question)

            pickleParseList.append(qObj.questionParts)

        foc, focRoot, mod, qclass, pnoun, subj = mainAnalyze(qObj)

        mainBuildQuery(qObj)

        docIds = mainQuerySingle("singleFromWeb", topDocs)

        titles, texts = mainRelated(docIds)

        relatedDocs.append([titles,texts])

        phrase = " ".join([pnoun, mod, focRoot, subj])

        if alreadyTranslated:
            translation = pickleTransList[count]
        else:
            translation = mainTranslate(phrase)
            pickleTransList.append(translation)

        focusListFoundT.append(foc)
        modListFoundT.append(mod)
        classListFound.append(qclass)
        transPhraseList.append(phrase)
        transList.append(translation)

        count += 1

    if not parsedBefore:
        pickle.dump(pickleParseList, open(dataPath[0:len(dataPath)-5]+".parsed", "wb"))

    if not alreadyTranslated:
        pickle.dump(pickleTransList, open(transPath, "wb"))

    return focusListFoundT, modListFoundT, classListFound, transPhraseList, transList, relatedDocs

def mainBuildQuery(qObj, paramFile="singleFromWeb"):
    return buildQueryFromQuestionData(qObj, paramFile)

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

def mainTranslate(translation_cand):
    return tw.translate(translation_cand)

def mainReadDataFile(dataFilePath):
    if not os.path.isfile(dataFilePath):
        error("NOT A DATA FILE")

    questionList = []
    focList = []
    modList = []
    classList = []

    """
    FORMAT:

    qText|focus|mod|coarseClass|fineClass|Answer
    """

    with open(dataFilePath, 'r') as dataFile:
        for line in dataFile:
            pieces = line.split("|")
            questionList.append(pieces[0])
            focList.append(pieces[1].split(" "))
            modList.append(pieces[2].split(" "))
            classList.append(pieces[3])

    """ CHECKSUM
    q = len(questionList)
    f = len(focList)
    m = len(modList)
    c = len(classList)

    if not (q == f and q == m and q == c):
        print("SOMETHING IS WRONG HERE: " + str(q) + " - " + str(f) + " - " + str(m) + " - " + str(c))
    else:
        print("ZIP SHOULD BE FINE")
    """

    # look for the dataFilePath+Parsed directory
    # ./.../.../cog.data -> look for -> ./.../.../cogParsed/
    parsedBefore = False
    if os.path.isfile(dataFilePath[0:len(dataFilePath)-5]+".parsed"):
        parsedBefore = dataFilePath[0:len(dataFilePath)-5]+".parsed"

    return questionList, focList, modList, classList, parsedBefore

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

    qF, qFR, qM, qC, qP, qS = mainAnalyze(qstnObj)

    if debug:
        printMsg('Analysis DONE')

    print('Subject : ' + qS)
    print('Mod : ' + qM)
    print('Focus : ' + qF)
    print('FR : ' + qFR)
    print('Class : ' + qC)
    print('Pnoun : ' + qP)

    """
    TRANSLATION
    """

    """
    if debug:
        printMsg('TRANSLATION')

    translation_titles = [ "Subject\t: ", 'Pnoun\t: ' , 'Mod + Focus\t: ']
    translation_cand = "\n".join([ qS, qP, qM +" "+ qFR])
    translation = mainTranslate(translation_cand)

    print('Phrases :\n %s' % translation_cand)

    tr_splitted_list = translation.split("\n")
    for i in range(len(tr_splitted_list)):
        print("Translation of %s %s" %(translation_titles[i],tr_splitted_list[i]))
    """
    if debug:
        printMsg('CLIR')

    docs = retrieve_from_english.main(qText)
    for doc in docs:
        if doc:
            print(doc.split("\n")[0])

    if debug:
        printMsg('CLIR ENDED')


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

if 'genPreParse' in sys.argv:
    path = "/home/hazircevap/hazircevap/Data/Biyoloji/Biyoloji_closeended/bio.data"
    qList, fList, mList, cList, parsedBefore = mainReadDataFile(path)

    fListF, mListF, cListF, transPList, transList = mainEval(qList, parsedBefore, path)
