import re
import codecs

queryDir = '/home/hazircevap/IR/queries/'

indexDir = '/home/hazircevap/IR/indri-5.0/wikipediaIndex/'
index_dir_tr = "/home/hazircevap/vikiIndex/"
# terms are list of strings
def buildIndriQuerySingle(qID, terms):

    #terms = question.questionText.split()

    termsText = " ".join(terms)
    buildIndriQuerySingleFromQuestion(qID, termsText)


def buildIndriQuerySingleFromQuestion(qID, termsText):
    termsText = re.sub("[,]", '', termsText)
#    termsText_decoded = termsText#.decode('utf-8')
    queryText = """<parameters>
<index>""" + indexDir + """</index>

<query>
<number>0</number>
<text>#combine("""

    #queryText += termsText_decoded + ')'
    queryText += termsText + ')'

    queryText += """</text>
</query>
</parameters>
"""

    with codecs.open(queryDir + str(qID), 'w+', 'utf-8') as qFile:
        qFile.write(queryText)
