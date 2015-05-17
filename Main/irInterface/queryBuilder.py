# -*- coding: utf-8 -*-

import re
import codecs

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

queryDir = '../IR/queries/'

indexDir = '../IR/indri-5.0/vikiEBAindex/'

def massBuildQuery(listOfQobj):

    for qobj, i in enumerate(listOfobj):
        queryFname = str(i) + ".massquery"
        buildQueryFromQuestionData(qobj, queryFileName=queryFname)

def buildQueryFromQuestionData(qObj, queryFileName="singleFromWeb", queryInput=False):

    if queryInput: # is provided..
        # bypass the query building phrase and write directly the given query string
        return buildIndriQuerySingle(queryFileName, queryInput, True)

    qTermsListF = qObj.extract_Terms_Text_List()
    qTermsListRoot = qObj.extract_Terms_Root_List() # redundant
    qFocusList = qObj.extract_Focus_Text_List()
    qModList = qObj.extract_Mod_Text_List()
    qPnounList = qObj.extract_Prop_Noun_List()

    qSubjs = qObj.extractSubjectList()
    qSubjTexts = qObj.extractSubjectList()

    finalString = ""

    termsKalan = []
    exWords = qObj.exclusionWords
    exWords.extend(['_', 've'])

    # excluding question words from the initial list
    qTermsList = [term for term in qTermsListF if term not in exWords]

    for term in qTermsList:
        if term not in qFocusList and term not in qPnounList and term not in qSubjTexts and term != ".":
            notInMod = True
            for mods in qModList:
                if term in mods:
                    notInMod = False
            if notInMod:
                termsKalan.append(term)


    if termsKalan != []:
        #kalanRoot = qObj.findRootsOf(termsKalan)

        finalString += "0.5 " + " 0.5 ".join(termsKalan)


    if qModList == [] and qFocusList != []:
        finalString += " 1.0 #ud" + str(len(qFocusList)) + "(" + " ".join(qFocusList) + ")"
    else:
        modStringAll = ""
        for mods in qModList:
            for focus in qFocusList:
                modString = " 1.0 #ud2(" + " ".join(mods) + " " + focus + ")"
                modStringAll += modString + ""

        finalString += modStringAll

    pNounStr = ""
    for pnoun in qPnounList:
        pNounStr += " 2.0 " + pnoun

    qSubjsList = [term for term in qSubjs if term not in exWords]
    qSubjsList.reverse()
    if qSubjsList != []:
        subjStr = " 1.5 #od" + str(len(qSubjsList)) + "(" + " ".join(qSubjsList) + ")"
    #subjStr = " 1.5 " + " 1.5 ".join(qSubjsList)
        finalString += subjStr

    if qPnounList != []:
        finalString += pNounStr

    return buildIndriQuerySingle(queryFileName, finalString, True)

# terms are list of strings
# if directQueryText=True, then terms IS the pregenerated query string, function just plugs it into the query
def buildIndriQuerySingle(queryFileNameStr, terms, directQueryText=False):

    #terms = question.questionText.split()

    if directQueryText:
        termsText = terms
    else:
        termsText = "1.0 " + " 1.0 ".join(terms)

        termsText = re.sub("[,]", '', termsText)

    queryText = """
<parameters>
<index>""" + indexDir + """</index>

<query>
<number>0</number>
<text>#weight("""

    queryText += termsText + ')'


    queryText += """</text>
</query>
</parameters>
"""

    with codecs.open(queryDir + queryFileNameStr, 'w+', 'utf-8') as qFile:
        qFile.write(queryText.decode('utf-8'))

    #print("Build Query Written : " + str(termsText))
    return termsText

### ENGLISH ###
###############
index_dir_tr = '../IR/indri-5.0/wikipediaIndex/'

def buildIndriQuerySingle_en(qID, question):
    terms = question.split()
    termsText = " ".join(terms)
    buildIndriQuerySingleFromQuestion_en(qID, termsText)

def buildIndriQuerySingleFromQuestion_en(qID, termsText):
    termsText = re.sub("[,]", '', termsText)
    #    termsText_decoded = termsText#.decode('utf-8')
    queryText = """<parameters>
    <index>""" + index_dir_tr + """</index>

    <query>
    <number>0</number>
    <text>#combine("""
    queryText += termsText + ')'
    queryText += """</text>
    </query>
    </parameters>
    """
    with codecs.open(queryDir + str(qID), 'w+', 'utf-8') as q_file:
        q_file.write(queryText)
