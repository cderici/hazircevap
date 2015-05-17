import os, sys

from subprocess import Popen, PIPE, STDOUT

indriDir = "../IR/indri-5.0/"
indriRun = indriDir+'runquery/IndriRunQuery'

#paramDir = "/home/hazircevap/IR/queries/"
paramDir = "../IR/queries/"

def massIndriQuery(listOfqObj, count=5):
    relatedDocIDs = []

    for qObj, i in enumerate(listOfqObj):
        paramFname = str(i) + ".massquery"
        relatedDocIDs.append(singleIndriQuery(paramFname, count))
        # clean the mass queries, we're done with them
        os.remove(paramDir+str(i)+".massquery")

    return relatedDocIds
    

def singleIndriQuery(paramFileName, count=5):

    #print("BEGIN: makeSingleQuery " + str(paramFileName))

    """ sample query:
    /home/.../runquery/IndriRunQuery -count=5 /home/.../queries/123
    """
    query = Popen([indriRun + ' -count=' + str(count) + ' ' + paramDir + str(paramFileName)], stdout=PIPE, stderr=PIPE, shell=True)

    stdout, stderr = query.communicate()
    #print(stdout)
    #print(stderr)
    if stderr:
        sys.stderr.write("[ParamFileName:%s] %s\n" %(paramFileName,stderr))
        return None

    return handleOutput(stdout, count)


def handleOutput(queryOutput, count=5):

    tmp = queryOutput.split('\n')

    docs = []

    for line in tmp:
        if line != '':
            docs.append(line.split()[1])

    return docs
