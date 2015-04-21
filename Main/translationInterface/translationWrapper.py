# -*- coding: utf-8 -*-

import subprocess, shutil, os, sys
import codecs

#sys.path.append('../')
#sys.path.append('utils')

reload(sys)
sys.setdefaultencoding('utf-8')

from tokenize_tr import tokenize_tr

"""
PROVIDED FUNCTIONS

translate
translate_file

"""

"""
TRANSLATION
Translation system translates any given phrase and returns the translation

"""
def translate(text,input_lang="tr",output_lang="en"):
    if input_lang is "tr":
        pass

def translate_file(filename,raw=True,input_lang="tr",output_lang="en",debug=False):
    filename = "/home/hazircevap/moses/corpus/cografya/cografya_questions_all.txt"
    if debug:
        printMsg('Preparing for Translation')
    if raw:
        fname_list = filename.split(".")
        fname_list[-1] = "tr"
        fname_list.insert(-1,"tok")
        tok_filename = ".".join(fname_list)
        print(tok_filename)
        tokenize_tr(filename,tok_filename)
        fname_list[-2] = "low"
        low_filename = ".".join(fname_list)
        print(low_filename)
        with open(tok_filename,) as infile, open(low_filename,"w") as outfile:
            subprocess.call(['/opt/moses/scripts/tokenizer/lowercase.perl'],stdin=infile,stdout=outfile, shell=True)
        fname_list[-2] = "trs"
        trns_filename = ".".join(fname_list)
        translation_cmd = ['/opt/moses/mosesdecoder/bin/moses',
                           '-search-algorithm 1',
                           '-cube-pruning-pop-limit 5000',
                           '-s 5000',
                           '-threads 8',
                           '-t -text-type "test"',
                           '-v 0',
                           '-f /home/hazircevap/hazircevap/CAGIL/run5/evaluation/test.filtered.ini.2']
        with open(low_filename,) as infile, open(trns_filename,"w") as outfile:
            subprocess.call([" ".join(translation_cmd)],
                        stdin=infile,stdout=outfile, shell=True)
        fname_list[-2] = "true"
        true_filename = ".".join(fname_list)
        with open(trns_filename,) as infile, open(true_filename,"w") as outfile:
            subprocess.call(['/opt/moses/scripts/recaser/truecase.perl --model /home/hazircevap/hazircevap/CAGIL/run5/corpus/toy.clean.1.tr -b'],
                        stdin=infile,stdout=outfile, shell=True)
        print("Translated file %s" %true_filename)
        if debug:
            printMsg('Done')
            printResult('Translation output is written to', true_filename)

def tokenize_file_eng(filename):
    filename = '/home/hazircevap/moses/corpus/cografya/cografya_questions_all.en.txt'
    fname_list = filename.split(".")
    fname_list[-1] = "en"
    fname_list.insert(-1,"tok")
    tok_filename = ".".join(fname_list)
    print(tok_filename)
    with open(filename,) as infile, open(tok_filename,"w") as outfile:
        subprocess.call(['/opt/moses/scripts/tokenizer/tokenizer.perl -a -l en'],stdin=infile,stdout=outfile, shell=True)
