from __future__ import print_function
import nltk,io,sys,os

TUNING = 0.8  # *5 4
TEST = 1.2    # *5 6
TRAINING = 98 # *5 490
FACTOR = 5
def divide(in_filename,training,tuning,test):
    sys.stdout.write("Divide corpus into training test and tuning sets\n")
    tokens = []
    with io.open(in_filename,encoding='utf-8') as infile, io.open(training, mode="w", encoding='utf-8') as tr , io.open(tuning,mode="w", encoding='utf-8') as tu, io.open(test,mode="w", encoding='utf-8') as te:
        i = 0
        line = infile.readline()
        while line:
            if i < TEST*FACTOR:
                out = te
            elif i < (TEST+TUNING)*FACTOR:
                out = tu
            else:
                out = tr
            i += 1
            i %= FACTOR*100
            tokens=nltk.word_tokenize(line)
            print(" ".join(tokens),file=out)
            line = infile.readline()
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
