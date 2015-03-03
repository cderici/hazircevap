from __future__ import print_function
import nltk,codecs,sys,os

#  5% 10% 85% -> 1 2 31
def divide(in_filename,training,tuning,test):
    sys.stdout.write("Divide corpus into training test and tuning sets\n")
    tokens = []
    with codecs.open(in_filename,"r", 'utf-8') as infile, codecs.open(training,"wb", 'utf-8') as tr , codecs.open(tuning,"wb", 'utf-8') as tu, codecs.open(test,"wb", 'utf-8') as te:
        i = 0
        for line in infile.readlines():
            if i < 31:
                out = tr
            elif i < 33:
                out = te
            else:
                out = tu
            i += 1
            i %= 34
            tokens=nltk.word_tokenize(line)
            print(" ".join(tokens),file=out)
            #tokens.append("\n")
            #out.write(" ".join(tokens))

def main(argv):
    if len(argv) < 5:
        sys.stderr.write("Usage: %s <filename> infile training tuning test \n" % (argv[0],))
        return 1

    #if not os.path.exists(os.path.join(param_dir,str(argv[1]))):
        #sys.stderr.write("ERROR: File %r was not found in %s!\n" % (argv[1],param_dir))
    if not os.path.exists(argv[1]):
        sys.stderr.write("ERROR: File %r was not found!\n" % argv[1])
        return 1
    divide(argv[1],argv[2],argv[3],argv[4])

if __name__ == "__main__":
    sys.exit(main(sys.argv))
