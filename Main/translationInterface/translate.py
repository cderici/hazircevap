#!/usr/bin/python
import os, sys
from subprocess import Popen, PIPE, STDOUT

moses_dir = "/opt/moses/"
moses_run = moses_dir +'bin/moses'

param_dir = "/home/hazircevap/moses/working/"

def translate(param_filename,lang="en"):
    #print("BEGIN: translate " + str(paramFileName))

    """ sample query:
    nohup nice /opt/moses/bin/moses            \
    -f /home/cagil/working/filtered-ted_test_tr-en/moses.ini   \
    < /home/cagil/corpus/ted_test_tr-en.tok.tr               \
    > ~/moses/working/ted_test_tr-en.translated.en         \
    2> ~/moses/working/ted_test_tr-en.out
    """
    in_filename =  os.path.join(param_dir, str(param_filename))
    out_filename =  os.path.join(param_dir, str(param_filename)+".translated."+lang)
    log_filename =  os.path.join(param_dir, str(param_filename)+".log")
    with open(in_filename,"r") as infile, open(out_filename,"wb") as out, open(log_filename,"wb") as err:
        query = Popen([moses_run + ' -f /home/cagil/working/filtered-ted_test_tr-en/moses.ini'],
                      stdin=infile, stdout=out, stderr=err, shell=True,
                      preexec_fn=lambda: os.nice(9))


def main(argv):
    if len(argv) < 2:
        sys.stderr.write("Usage: %s <filename>\n" % (argv[0],))
        return 1

    if not os.path.exists(os.path.join(param_dir,str(argv[1]))):
        sys.stderr.write("ERROR: File %r was not found in %s!\n" % (argv[1],param_dir))
        return 1
    translate(argv[1])

if __name__ == "__main__":
    sys.exit(main(sys.argv))
