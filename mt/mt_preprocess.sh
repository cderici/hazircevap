#!/bin/bash
moses_path="/opt/moses"
corpus_path="/home/hazircevap/moses/corpus/tr-en"
working_path="/home/hazircevap/moses/working"

function tokenize_BU_corpus {
    $moses_path/scripts/tokenizer/tokenizer.perl -l en < $corpus_path/BU_en.txt > $corpus_path/BU.tok.en
    python tokenize_tr.py $corpus_path/BU_tr.txt  $corpus_path/BU.tok.tr
}

function train_truecaser {
    $moses_path/scripts/recaser/train-truecaser.perl \
	--model $corpus_path/truecase-model.en \
	--corpus $corpus_path/BU.tok.en
    $moses_path/scripts/recaser/train-truecaser.perl \
	--model $corpus_path/truecase-model.tr \
	--corpus $corpus_path/BU.tok.tr
}

function truecase_BU {
    $moses_path/scripts/recaser/truecase.perl \
	--model $corpus_path/truecase-model.en \
	< $corpus_path/BU.tok.en \
	> $corpus_path/BU.true.en

    $moses_path/scripts/recaser/truecase.perl \
	--model $corpus_path/truecase-model.tr \
        < $corpus_path/BU.tok.tr  \
	> $corpus_path/BU.true.tr
}

function clean_BU {
    $moses_path/scripts/training/clean-corpus-n.perl \
	$corpus_path/BU.true tr en \
	$corpus_path/BU.clean 1 80
}

# the following will build an appropriate 5-gram language model, removing singletons, smoothing with improved Kneser-Ney, and adding sentence boundary symbols:
function train_lm_BU {
    mkdir $working_path/lm
    #cd $working_path/lm
    $moses_path/irstlm/bin/add-start-end.sh                 \
	< $corpus_path/BU.true.en \
	> $working_path/lm/BU.sb.en
    export IRSTLM=$moses_path/irstlm; $moses_path/irstlm/bin/build-lm.sh \
	-i $working_path/lm/BU.sb.en \
	-t ./tmp  -p -s improved-kneser-ney -n 5 -o $working_path/lm/BU.lm.en
    $moses_path/irstlm/bin/compile-lm  \
	--text=yes \
	$working_path/lm/BU.lm.en.gz \
	$working_path/lm/BU.arpa.en
    # KENLM
    $moses_path/bin/build_binary -i \
	$working_path/lm/BU.arpa.en \
	$working_path/lm/BU.blm.en
    #cd -
}

function divide_corpus {
    python divide.py  $corpus_path/BU.clean.tr $corpus_path/BU.train.clean.tr /tmp/BU.tuning.clean.tr /tmp/BU.test.clean.tr
    python divide.py  $corpus_path/BU.clean.en $corpus_path/BU.train.clean.en /tmp/BU.tuning.clean.en /tmp/BU.test.clean.en
    python divide.py  $corpus_path/BU.true.tr /tmp/BU.train.true.tr $corpus_path/BU.tuning.true.tr $corpus_path/BU.test.true.tr
    python divide.py  $corpus_path/BU.true.en /tmp/BU.train.true.en $corpus_path/BU.tuning.true.en $corpus_path/BU.test.true.en
}

function train_mt {
    nohup nice $moses_path/scripts/training/train-model.perl -cores 12 -root-dir $working_path/train \
	-corpus $corpus_path/BU.train.clean                             \
	-f tr -e en -alignment grow-diag-final-and -reordering msd-bidirectional-fe \
	-lm 0:5:$working_path/lm/BU.blm.en:8           \
	-external-bin-dir $moses_path/tools >& training.out &

}

function tuning_mt {
    nohup nice $moses_path/scripts/training/mert-moses.pl \
        $corpus_path/BU.tuning.true.tr $corpus_path/BU.tuning.true.en \
	$moses_path/bin/moses $working_path/train/model/moses.ini --mertdir $moses_path/bin/ \
	&> mert.out &
}

function binarise_models {
    mkdir $working_path/binarised-model
    $moses_path/bin/processPhraseTableMin \
	-in $working_path/train/model/phrase-table.gz -nscores 4 \
	-out $working_path/binarised-model/phrase-table
    $moses_path/bin/processLexicalTableMin \
	-in $working_path/train/model/reordering-table.wbe-msd-bidirectional-te.gz \
	-out $working_path/binarised-model/reordering-table
}

test_set_tr='$corpus_path/BU.test.true.tr'
test_set_en='$corpus_path/BU.test.true.en'
function test_mt {
    cd ~/working
    $moses_path/scripts/training/filter-model-given-input.pl             \
	$working_path/filtered-BU $working_path/mert-work/moses.ini $test_set_tr  \
	-Binarizer $moses_path/bin/processPhraseTableMin

    #You can test the decoder by first translating the test set (takes a wee while)
    #then running the BLEU script on it:

    nohup nice $moses_path/bin/moses            \
	-f $working_path/filtered-BU/moses.ini   \
	< $test_set_tr                \
	> $working_path/BU.test.translated.en        \
	2> test.out
    $moses_path/scripts/generic/multi-bleu.perl \
	-lc $test_set_en
	< $working_path/BU.test.translated.en
}

echo 'usage: . mt_preprocess.sh'
echo ''
echo 'tokenize_BU_corpus'
echo ''
echo 'train_truecaser'
echo ''
echo 'truecase_BU'
echo ''
echo 'clean_BU'
echo ''
echo 'train_lm_BU > lm_out.txt 2>&1'
echo ''
echo 'divide_corpus'
echo ''
echo 'train_mt'
echo ''
echo 'tuning_mt'
echo ''
echo ''
echo ''
echo ''

#move_lines $1 $2 $3
#traverse $1

#head -n 6 /home/cagil/Datasets/snap/splited-07//tweets2009-07-splitedag > from.txt
#tail -n 5 /home/cagil/Datasets/snap/splited-07//tweets2009-07-splitedaf > to.txt
#move_lines from.txt to.txt 3
