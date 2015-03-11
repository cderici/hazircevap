import os, sys

from subprocess import Popen, PIPE, STDOUT

indriDir = "/home/hazircevap/IR/indri-5.0/"
indriRun = indriDir+'runquery/IndriRunQuery'

paramDir = "/home/hazircevap/IR/queries/"

def singleIndriQuery(paramFileName):

    #print("BEGIN: makeSingleQuery " + str(paramFileName))

    """ sample query:
    /home/.../runquery/IndriRunQuery -count=5 /home/.../queries/123
    """
    query = Popen([indriRun + ' -count=5 ' + paramDir + str(paramFileName)], stdout=PIPE, stderr=PIPE, shell=True)

    stdout, stderr = query.communicate()

    return handleOutput(stdout)


def handleOutput(queryOutput, count=5):

    tmp = queryOutput.split('\n')

    docs = []

    for line in tmp:
        if line != '':
            docs.append(line.split()[1])

    return docs
