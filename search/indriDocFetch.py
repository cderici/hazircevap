from subprocess import Popen, PIPE, STDOUT

indriDir = "/home/hazircevap/IR/indri-5.0/"
dumpindex = indriDir + 'dumpindex/dumpindex'

indexDir = indriDir + 'wikipediaIndex/'

indexDir_tr = "/home/hazircevap/vikiIndex/"


def getDoc(docID):

    dump = Popen([dumpindex + ' ' + indexDir + ' dt ' + str(docID)], stdout=PIPE, stderr=PIPE, shell=True)

    #print(dumpindex + ' ' + indexDir + ' dt ' + str(docID))

    stdout, stderr = dump.communicate()

    return stdout

def getDocTr(docID):
    dump = Popen([dumpindex + ' ' + indexDir_tr + ' dt ' + str(docID)], stdout=PIPE, stderr=PIPE, shell=True)

    #print(dumpindex + ' ' + indexDir_tr + ' dt ' + str(docID))

    stdout, stderr = dump.communicate()

    return stdout
