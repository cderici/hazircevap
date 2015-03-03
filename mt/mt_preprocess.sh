#!/bin/bash
moses_path="/opt/moses"
corpus_path="/home/hazircevap/moses/corpus"

function tokenize_BU_corpus {
    $moses_path/scripts/tokenizer/tokenizer.perl -l en < $corpus_path/BU_en.txt > $corpus_path/BU.tok.en
    python tokenize_tr.py $corpus_path/BU_tr.txt  $corpus_path/BU.tok.tr
}

function train_truecaser {
    $moses_path/scripts/recaser/train-truecaser.perl --parallel \
	--model $corpus_path/truecase-model.en \
	--corpus $corpus_path/BU.tok.en
    $moses_path/scripts/recaser/train-truecaser.perl \
	--model $corpus_path/truecase-model.fr \
	--corpus $corpus_path/BU.tok.tr
}

echo 'usage: . mt_preprocess.sh'
echo ''
echo 'tokenize_BU_corpus'
echo ''
echo 'train_truecaser'
echo ''
echo ''
echo ''
echo ''

#move_lines $1 $2 $3
#traverse $1

#head -n 6 /home/cagil/Datasets/snap/splited-07//tweets2009-07-splitedag > from.txt
#tail -n 5 /home/cagil/Datasets/snap/splited-07//tweets2009-07-splitedaf > to.txt
#move_lines from.txt to.txt 3
