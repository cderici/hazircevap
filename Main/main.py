# -*- coding: utf-8 -*-

import sys, os, codecs
#sys.path.append('utils')

### PARSER ###
sys.path.append('parserInterface')
from parserWrapper import parse
from sysUtil import printMsg, printResult
import cPickle as pickle

### TMP ###
from maltImporter import MaltImporter
qFilePath = '../Data/Cografya/Cografya_closeended/cog.data';
qParsedFilePath = '../Data/q_parsed.qp';

ourQuestions = MaltImporter().importMaltOutputs(qFilePath, qParsedFilePath)

### Syntactic Analysis ###
sys.path.append('analysisInterface')
from analyzer import *

### IR ###
sys.path.append('irInterface')
from indriHandler import singleIndriQuery
from queryBuilder import buildQueryFromQuestionData
from queryBuilder import buildIndriQuerySingle
from indriDocFetch import getDoc

### TRANSLATION ###
from translationInterface import translationWrapper as tw

### SUMMARIZATION ###
sys.path.append('summarizationInterface')
from summaryWrapper import summarize

debug=True


def mainParse(qText):
    return parse(qText, debug)

def mainAnalyze(qObj, forwGlass, backGlass):
    analyzer = QuestionAnalysis(qObj)

    if not forwGlass and not backGlass:
        forwGlass = Glass(ourQuestions, backwards=False)
        backGlass = Glass(ourQuestions, backwards=True)

    qFocus, qFocusRoots, qMod, qClass, qPnoun, qSubj = analyzer.fullAnalysis(backGlass, forwGlass)

    return qFocus, qFocusRoots, qMod, qClass, qPnoun, qSubj

def mainEval(questionList, answerList, parsedBefore, dataPath, topDocs=5, bypassDocs=False, bypassTrans=False):
    focusListFoundT = []
    modListFoundT = []
    classListFound = []
    transPhraseList = []
    transList = []
    relatedDocs = []
    answerFoundOrNot = []
    queries = []
    subjects = []

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

    forwGlass = Glass(ourQuestions, backwards=False)
    backGlass = Glass(ourQuestions, backwards=True)


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

        foc, focRoot, mod, qclass, pnoun, subj = mainAnalyze(qObj, forwGlass, backGlass)

        query = mainBuildQuery(qObj)
        queries.append(query)

        docIds = mainQuerySingle("singleFromWeb", topDocs)

        titles, texts = mainRelated(docIds)

        answers = answerList[count].split('/')
        #print(answers)

        if answers == []:
            found = True
        else:
            found = False

        for ans in answers:
            for text in texts:
                answer = ans.encode('utf8')
                answerParts = answer.split(' ')
                for anPart in answerParts:
                    if (anPart in text) or (anPart.lower() in text) or (anPart.upper() in text):
                        found = True
                        break
                
                if found:
                    break
            
            if found:
                break

        answerFoundOrNot.append(found)
        
        if bypassDocs:
            relatedDocs.append([topDocs*['title'], topDocs*['docText']])
        else:
            relatedDocs.append([titles,texts])


        subjTrans = []
        #making subj and foc mutual exclusive (not exactly, but anyway)
        for s in subj.split(' '):
            if s not in foc:
                subjTrans.append(s)

        if subjTrans == []:
            subjTxt = "noSubjext"
        else:
            subjTxt = " ".join(subjTrans)

        if pnoun == "":
            pTxt = "noPNoun"
        else:
            pTxt = pnoun

        phrase = "\n".join([subjTxt, pTxt, mod + " " + foc])

        #tr_splitted_list = translation.split("\n")
        """
        subj = tr_splitted_list[0]
        prop = tr_splitted_list[1]
        focmod = tr_splitted_list[2]
        """
        if bypassTrans:
            translation = []
        else:
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
        subjects.append(qObj.extractSubjectText())

        count += 1

    if not parsedBefore:
        pickle.dump(pickleParseList, open(dataPath[0:len(dataPath)-5]+".parsed", "wb"))

    if not alreadyTranslated:
        pickle.dump(pickleTransList, open(transPath, "wb"))

    return focusListFoundT, modListFoundT, classListFound, transPhraseList, transList, relatedDocs, answerFoundOrNot, queries, subjects

def mainBuildQuery(qObj, paramFile="singleFromWeb", queryInput=False):
    return buildQueryFromQuestionData(qObj, paramFile, queryInput)

def mainQuerySingle(paramFile="singleFromWeb", count=5):
    return singleIndriQuery(paramFile, count)

def mainRelated(docIDs):
    titles = []
    texts = []

    for dID in docIDs:
        # dID is a string!
        dTitle, dText = getDoc(dID)
        if dID.isdigit() and int(dID) >= 221187:
            dTitle += " (EBA)"
        titles.append(dTitle)
        texts.append(dText)

    return titles, texts

def mainTranslate(translation_cand):
    return tw.translate(translation_cand)

def mainSummarize(qText, aText, relatedTitles, relatedDocs):
    return summarize(qText, aText, relatedTitles, relatedDocs)

def mainReadDataFile(dataFilePath):
    if not os.path.isfile(dataFilePath):
        error("NOT A DATA FILE")

    questionList = []
    focList = []
    modList = []
    classList = []
    answerList = []

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
            answerList.append(pieces[5])

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

    return questionList, focList, modList, classList, parsedBefore, answerList

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

    forwGlass = Glass(ourQuestions, backwards=False)
    backGlass = Glass(ourQuestions, backwards=True)


    if debug:
        printMsg('Running Analysis')

    qF, qFR, qM, qC, qP, qS = mainAnalyze(qstnObj, forwGlass, backGlass)

    if debug:
        printMsg('Analysis DONE')
    
    print('Focus : ' + qF)
    print('Mod : ' + qM)
    print('Class : ' + qC)
    print('Pnoun : ' + qP)

    """
    TRANSLATION
    """
    #if debug:
    #printMsg('TRANSLATION')

    #translation_cand = " ".join([ qP, qM, qFR, qS])
    #translation = mainTranslate(translation_cand)
    
    #print('Phrase : %s' % translation_cand)
    #print('Translation : %s' % translation)

    """
    BUILD THE QUERY
    """
    if debug:
        printMsg('Building the Query')

    mainBuildQuery(qstnObj)

    """
    QUERY THE IR
    """

    docs = mainQuerySingle("singleFromWeb", 10)

    print(docs)

    #docTitle, docText = getDoc(docs[0])

    titles, texts = mainRelated(docs)

    #print("TITLE: " + docTitle)
    #print("TEXT: \n\n" + docText)

    summaries = mainSummarize(qText, "WRONG ANSWER", titles, texts)

    print(summaries[0])
    print(summaries[1])
    print(summaries[2])

if 'test' in sys.argv:
    #qText = u"Türkiyenin en büyük ovası hangisidir"
    qText = "Akarsuların taşıyarak oluşturdukları topraklara ne ad verilir"
    runPipeline(qText)

if 'genPreParse' in sys.argv:
    path = "/home/hazircevap/hazircevap/Data/Cografya/Cografya_closeended/cog.data"
    qList, fList, mList, cList, parsedBefore, answerList = mainReadDataFile(path)

    fListF, mListF, cListF, transPList, transList, relDocs, answerFounds, queries, subjects = mainEval(qList, answerList, parsedBefore, path)

if 'yigitSpecial' in sys.argv:

    sourcePath = "/home/hazircevap/hazircevap/Data/Cografya/Cografya_closeended/cog.data"

    outPath = "/home/hazircevap/hazircevap/Main/yigitSpecial/"

    qList, fList, mList, cList, parsedBefore, answerList = mainReadDataFile(sourcePath)

    pickleParseList = pickle.load(open(parsedBefore, "rb"))

    forwGlass = Glass(ourQuestions, backwards=False)
    backGlass = Glass(ourQuestions, backwards=True)


    for i, question in enumerate(qList):
        print("Processing Question : " + str(i))
        delim = "***********************"
        # fileStr will be flushed to the file i.txt
        fileStr = delim + "\nQuestion -> " + question + "?\n\nAnswer -> " + str(answerList[i]) + "\n" + delim + "\n"

        qParts = pickleParseList[i]

        qObj = Question(question, qParts)

        foc, focRoot, mod, qclass, pnoun, subj = mainAnalyze(qObj, forwGlass, backGlass)

        mainBuildQuery(qObj)

        docIds = mainQuerySingle("singleFromWeb", 10)

        titles, texts = mainRelated(docIds)
        
        docCount = 1
        for title, text in zip(titles, texts):
            # print(type(title))
            # print("\n\n")
            # print(type(text))
            # break
            fileStr += str(docCount) + ") " + str(title) + "\n\n" + str(text) + "\n" + delim + "\n"
            docCount += 1


        #break
        with codecs.open(outPath + str(i+1) + ".txt", "w+","utf-8") as f:
            f.write(fileStr.decode('utf-8'))
