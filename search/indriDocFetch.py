from subprocess import Popen, PIPE, STDOUT

indriDir = "/home/hazircevap/IR/indri-5.0/"
dumpindex = indriDir + 'dumpindex/dumpindex'

indexDir = indriDir + 'wikipediaIndex/'

def getDoc(docID):
    
    dump = Popen([dumpindex + ' ' + indexDir + ' dt ' + str(docID)], stdout=PIPE, stderr=PIPE, shell=True)

    #print(dumpindex + ' ' + indexDir + ' dt ' + str(docID))

    stdout, stderr = dump.communicate()

    return stdout
