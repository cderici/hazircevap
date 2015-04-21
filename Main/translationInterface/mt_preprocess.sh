#!/bin/bash
moses_path="/opt/moses"
moses_dec_path="/opt/moses/mosesdecoder"
moses_script_dir="/opt/moses/scripts"
irstlm_path="$moses_path/irstlm-5.80.08"
corpus_path="/home/hazircevap/moses/corpus/tr-en"
working_path="/home/hazircevap/moses/working"
log_dir="/home/hazircevap/moses/working/logs"

check_exists () {
    if [ ! -f $1 ]; then
	echo "$1 : File not found!"
    fi
}

# /home/hazircevap/moses/corpus/tr-en/BU-ALT.tr
# /home/hazircevap/moses/corpus/tr-en/BU-ALT.en
function tokenize_BU_corpus {
    $moses_script_dir/tokenizer/tokenizer.perl -l en < $corpus_path/BU-ALT.en > $corpus_path/BU-ALT.tok.en
    python tokenize_tr.py $corpus_path/BU-ALT.tr  $corpus_path/BU-ALT.tok.tr
}

function train_truecaser {
    $moses_path/scripts/recaser/train-truecaser.perl \
	--model $corpus_path/truecase-model.en \
	--corpus $corpus_path/BU-ALT.tok.en
    $moses_path/scripts/recaser/train-truecaser.perl \
	--model $corpus_path/truecase-model.tr \
	--corpus $corpus_path/BU-ALT.tok.tr
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
    mkdir -p $working_path/lm
    #cd $working_path/lm
    $irstlm_path/bin/add-start-end.sh                 \
	< $corpus_path/BU.true.en \
	> $working_path/lm/BU.sb.en
    export IRSTLM=$irstlm_path; $irstlm_path/bin/build-lm.sh \
	-i $working_path/lm/BU.sb.en \
	-t ./tmp  -p -s improved-kneser-ney -n 5 -o $working_path/lm/BU.lm.en
    $irstlm_path/bin/compile-lm  \
	--text=yes \
	$working_path/lm/BU.lm.en.gz \
	$working_path/lm/BU.arpa.en
    # KENLM
    $moses_dec_path/bin/build_binary -i \
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

lang_model_en="$working_path/lm/BU.blm.en"
n_gram=5

set_working_path(){
    working_path="$1"
}

set_corpus_path(){
    corpus_path="$1"
}

function train_mt {
    mkdir -p $working_path/train
    nohup nice $moses_path/scripts/training/train-model.perl -cores 12 -root-dir $working_path/train \
	-corpus $corpus_path/BU.train.clean   \
	-max-phrase-length 5 \
	-f tr -e en -alignment grow-diag-final-and -reordering msd-bidirectional-fe \
	-lm 0:$n_gram:$lang_model_en:8           \
	-external-bin-dir $moses_path/tools >& $log_dir/training.out &
}

function tuning_mt {
    mkdir -p $working_path/tuning/mert-work
    nohup nice $moses_path/scripts/training/mert-moses.pl \
        $corpus_path/BU.tuning.true.tr $corpus_path/BU.tuning.true.en \
	$moses_dec_path/bin/moses $working_path/train/model/moses.ini \
	--working-dir $working_path/tuning/mert-work  --mertdir $moses_dec_path/bin/ \
	-root-dir $working_path/tuning --decoder-flags="-threads 8 -v 0" &> $log_dir/tuning_mert.out &
    tail -n 2 $working_path/tuning/mert-work/run*.mert.log
}

function tune_BU-ALT {
    nohup nice $moses_path/scripts/training/mert-moses.pl \
    /home/hazircevap/moses/corpus/tr-en/BU-ALT.tuning.tok.tr /home/hazircevap/moses/corpus/tr-en/BU-ALT.tuning.tok.en \
	$moses_dec_path/bin/moses /home/hazircevap/hazircevap/CAGIL/run4/model/moses.ini.1 \
	--working-dir /home/hazircevap/hazircevap/CAGIL/run4/tuning/mert-work  --mertdir $moses_dec_path/bin/ \
	-root-dir /home/hazircevap/hazircevap/CAGIL/run4/tuning --decoder-flags="-threads 8 -v 0" &> tuning_mert.out &
}

function binarise_models {
    pt_file="$working_path/train/model/phrase-table.gz"
    reord_file="$working_path/train/model/reordering-table.wbe-msd-bidirectional-fe.gz"
    check_exists $pt_file
    check_exists $reord_file
    mkdir -p $working_path/binarised-model
    $moses_dec_path/bin/processPhraseTableMin \
	-in $pt_file -nscores 4 \
	-out $working_path/binarised-model/phrase-table
    $moses_dec_path/bin/processLexicalTableMin \
	-in  $reord_file \
	-out $working_path/binarised-model/reordering-table
    echo "You should edit moses.ini file http://www.statmt.org/moses/?n=Advanced.RuleTables#ntoc3"
    #cp /home/hazircevap/moses/working/tuning/mert-work/moses.ini /home/hazircevap/moses/working/binarised-model/
}

test_set_tr="$corpus_path/BU.test.clean.tr"
test_set_en="$corpus_path/BU.test.clean.en"
function test_filter {
    $moses_path/scripts/training/filter-model-given-input.pl             \
	$working_path/filtered-BU $working_path/tuning/mert-work/moses.ini $test_set_tr  \
	-binarizer $moses_dec_path/bin/processPhraseTableMin

    #You can test the decoder by first translating the test set (takes a wee while)
    #then running the BLEU script on it:
}

function test_mt_BU {
    nohup nice $moses_dec_path/bin/moses            \
	-f $working_path/filtered-BU/moses.ini   \
	-i $test_set_tr                \
	> $working_path/BU.test.translated.en        \
	2> $log_dir/test-translation.out
    $moses_path/scripts/generic/multi-bleu.perl \
	-lc $test_set_en < $working_path/BU.test.translated.en
}
function test_mt_alt {
    nohup nice $moses_dec_path/bin/moses  \
	-f $working_path/filtered-BU/moses.ini   \
	-i $working_path/filtered-BU/input.20031 \
	> $working_path/BU.test.translated.en   \
	2> $log_dir/test-translation.out
    $moses_path/scripts/generic/multi-bleu.perl \
	-lc $test_set_en \
	< $working_path/BU.test.translated.en  >& $log_dir/test-bleu.out &
}
binary_ini="$working_path/binarised-model/moses.ini"
binary_ini="/home/hazircevap/hazircevap/CAGIL/run4/model/moses.ini.1"
translate(){
#    echo $1 | /opt/moses/mosesdecoder/bin/moses -f /home/hazircevap/moses/working/binarised-model/moses.ini -v 0
    true_cased=$(echo $1 | $moses_path/scripts/recaser/truecase.perl --model $corpus_path/truecase-model.tr)
    echo $true_cased | $moses_dec_path/bin/moses -f $binary_ini -v 0
}

#translate_file ~/moses/corpus/cografya_questions_all.txt
translate_file(){
    while read p; do
	translate "$p"
    done < $1
}
# test_mt $cografya_corpus/cografya_questions_all.txt $cografya_corpus/cografya_questions_all_translated.en $cografya_corpus/cografya_questions_all.en.txt
function test_mt {
    translate_file $1 > $2 2> $log_dir/translation.out
    $moses_path/scripts/generic/multi-bleu.perl \
	-lc $3 < $2
}
cografya_corpus="/home/hazircevap/moses/corpus/cografya"

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
echo 'binarise_models'
echo ''
echo 'test_mt'

#move_lines $1 $2 $3
#traverse $1

#head -n 6 /home/cagil/Datasets/snap/splited-07//tweets2009-07-splitedag > from.txt
#tail -n 5 /home/cagil/Datasets/snap/splited-07//tweets2009-07-splitedaf > to.txt
#move_lines from.txt to.txt 3
