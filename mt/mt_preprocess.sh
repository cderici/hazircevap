#!/bin/bash
moses_path="/opt/moses"
corpus_path="/home/hazircevap/moses/corpus"

function tokenize_BU_corpus {
    $moses_path/scripts/tokenizer/tokenizer.perl -l en < $corpus_path/BU_en.txt > $corpus_path/BU.tok.en
    $moses_path/scripts/tokenizer/tokenizer.perl -l tr < $corpus_path/BU_tr.txt > $corpus_path/BU.tok.tr
}

echo 'usage: . mt_preprocess.sh'
echo ''
echo 'tokenize_BU_corpus'
echo 'move_lines ~/Datasets/snap/splited-07/tweets2009-07-splitedag ~/Datasets/snap/splited-07/tweets2009-07-splitedaf 3'
echo ''
echo 'traverse ~/Datasets/snap/splited-07/'
echo 'traverse_and_move /home/cagil/Datasets/snap/splited/splited-09/'
echo ''
echo 'delete_first_n_line test/from.txt test/from2.txt 1'
echo ''
echo 'split_files test/from.txt test/from'

#move_lines $1 $2 $3
#traverse $1

#head -n 6 /home/cagil/Datasets/snap/splited-07//tweets2009-07-splitedag > from.txt
#tail -n 5 /home/cagil/Datasets/snap/splited-07//tweets2009-07-splitedaf > to.txt
#move_lines from.txt to.txt 3
