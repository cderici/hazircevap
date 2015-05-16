# -*- coding: utf-8 -*-

import subprocess, shutil, os, sys
import codecs, nltk

#sys.path.append('../')
#sys.path.append('utils')

reload(sys)
sys.setdefaultencoding('utf-8')

from tokenize_tr import tokenize_tr
from subprocess import Popen, PIPE

"""
PROVIDED FUNCTIONS

translate
translate_file

"""

"""
TRANSLATION
Translation system translates any given phrase and returns the translation

"""
# INI_FILE = "/home/hazircevap/hazircevap/CAGIL/run5/evaluation/test.filtered.ini.2"
INI_FILE = "/home/hazircevap/hazircevap/CAGIL/run5/binarised-model/moses.ini"
def translate(text,input_lang="tr",output_lang="en",debug=False):
    if input_lang is "tr":
        text_list = text.lower().split("\n")
        text_tok = "\n".join([" ".join(nltk.word_tokenize(tokens)) for tokens in text_list])
        truecase_cmd = 'echo "'+ text_tok +'" | /opt/moses/scripts/recaser/truecase.perl --model /home/hazircevap/hazircevap/CAGIL/run5/corpus/toy.clean.1.tr -b'
        if debug:
            print(truecase_cmd)
        p = Popen(truecase_cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        text_true, stderr = p.communicate()
        if stderr:
            print("Trucase Error %s" %stderr)
            return
        translation_cmd = ['echo "'+ text_true.strip() +'" |',
                           '/opt/moses/mosesdecoder/bin/moses',
                           '-search-algorithm 1',
                           '-cube-pruning-pop-limit 5000',
                           '-s 5000',
                           '-threads 8',
                           '-t -text-type "test"',
                           '-v 0',
                           '-f %s' %INI_FILE,
                           ]
        if debug:
            print(translation_cmd)
        p = Popen(" ".join(translation_cmd), stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        text_trans, stderr = p.communicate()
        if stderr:
            print("Translation Error %s" %stderr)
            return
        markup_cmd = "echo '"+text_trans.strip()+"' | /opt/moses/scripts/ems/support/remove-segmentation-markup.perl"
        p = Popen(markup_cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
        text_clean, stderr = p.communicate()
        if stderr:
            print("Markup Error %s" %stderr)
            return
        #print("Translated text %s" %text_clean.strip())
        if debug:
            printMsg('Done')
            printResult('Translation output is ', text_clean)
        return text_clean.strip()


def translate_file(filename,raw=True,input_lang="tr",output_lang="en",debug=False):
    #filename = "/home/hazircevap/moses/corpus/cografya/cografya_questions_all.txt"
    if debug:
        printMsg('Preparing for Translation')
    if raw:
        fname_list = filename.split(".")
        fname_list[-1] = "tr"
        fname_list.insert(-1,"tok")
        tok_filename = ".".join(fname_list)
        print(tok_filename)
        tokenize_tr(filename,tok_filename)
        fname_list[-2] = "true"
        true_filename = ".".join(fname_list)
        with open(tok_filename,) as infile, open(true_filename,"w") as outfile2:
            subprocess.call(['/opt/moses/scripts/recaser/truecase.perl --model /home/hazircevap/hazircevap/CAGIL/run5/corpus/toy.clean.1.tr -b'], stdin=infile,stdout=outfile2, stderr=subprocess.STDOUT,shell=True)
        print(true_filename)
        fname_list[-2] = "trs"
        trns_filename = ".".join(fname_list)
        fname_list[-2] = "cleaned"
        clean_filename = ".".join(fname_list)
        translation_cmd = ['/opt/moses/mosesdecoder/bin/moses',
                           '-search-algorithm 1',
                           '-cube-pruning-pop-limit 5000',
                           '-s 5000',
                           '-threads 8',
                           '-t -text-type "test"',
                           '-v 0',
                           '-f %s' %INI_FILE,
                           ]
        with open(true_filename,) as infile, open(trns_filename,"w") as outfile:
            subprocess.call([" ".join(translation_cmd)],
                        stdin=infile,stdout=outfile, stderr=PIPE,shell=True)
        with open(trns_filename,) as outfile, open(clean_filename,"w") as outfile2:
            subprocess.call(["/opt/moses/scripts/ems/support/remove-segmentation-markup.perl"],
                        stdin=outfile,stdout=outfile2, stderr=PIPE, shell=True)
        #print("Translated file %s" %clean_filename)
        if debug:
            printMsg('Done')
            printResult('Translation output is written to', clean_filename)
        return clean_filename

def tokenize_file_eng(filename):
    filename = '/home/hazircevap/moses/corpus/cografya/cografya_questions_all.en.txt'
    fname_list = filename.split(".")
    fname_list[-1] = "en"
    fname_list.insert(-1,"tok")
    tok_filename = ".".join(fname_list)
    print(tok_filename)
    with open(filename,) as infile, open(tok_filename,"w") as outfile:
        subprocess.call(['/opt/moses/scripts/tokenizer/tokenizer.perl -a -l en'],stdin=infile,stdout=outfile, shell=True)
    print('Tokenized output is written to', tok_filename)

def test_blue(tr_filename,en_filename):
    with open(tr_filename,) as tr_file: #, open(en_filename,) as en_file:
        subprocess.call(['/opt/moses/scripts/generic/multi-bleu.perl '+ en_filename], stdin=tr_file, shell=True)

def check_stderr(stderr):
    if stderr:
        print(stderr)
        return
