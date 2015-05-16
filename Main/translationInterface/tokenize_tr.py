from __future__ import print_function
import nltk,codecs,sys,os
##
# python ~/hazircevap/Main/translationInterface/tokenize_tr.py ~/moses/corpus/TED/ted.train.tr ~/moses/corpus/TED/ted.train.tok.tr
##
def tokenize_tr(in_filename,out_filename):
    sys.stdout.write("Nltk word_tokenize\nLanguage: tr\n")
    tokens = []
    with codecs.open(in_filename,"r", 'utf-8') as infile, codecs.open(out_filename,"wb", 'utf-8') as out:
        for line in infile.readlines():
            tokens=nltk.word_tokenize(line)
            print(" ".join(tokens),file=out)
            #tokens.append("\n")
            #out.write(" ".join(tokens))

def main(argv):
    if len(argv) < 3:
        sys.stderr.write("Usage: %s <filename> infile outfile\n" % (argv[0],))
        return 1

    #if not os.path.exists(os.path.join(param_dir,str(argv[1]))):
        #sys.stderr.write("ERROR: File %r was not found in %s!\n" % (argv[1],param_dir))
    if not os.path.exists(argv[1]):
        sys.stderr.write("ERROR: File %r was not found!\n" % argv[1])
        return 1
    tokenize_tr(argv[1],argv[2])

if __name__ == "__main__":
    sys.exit(main(sys.argv))
