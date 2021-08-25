#!/bin/bash
. ./path.sh || exit 1
. ./cmd.sh || exit 1
stage=0

if [ $stage -le 2 ]; then
    # Preparing language data
    rm -rf data/local/lang data/lang data/local/tmp data/local/dict/lexiconp.txt
    utils/prepare_lang.sh data/local/dict "<UNK>" data/local/lang data/lang
fi
echo
echo "===== LANGUAGE MODEL CREATION ====="
echo "===== MAKING lm.arpa ====="
echo

if [ $stage -le 3 ]; then
    local=data/local
    mkdir $local/tmp
    ngram-count -order 3 -write-vocab $local/tmp/vocab-full.txt -wbdiscount -text $local/corpus_large.txt -lm $local/tmp/lm.arpa
fi

echo
echo "===== MAKING G.fst ====="
echo
if [ $stage -le 4 ]; then
    lang=data/lang
    cat $local/tmp/lm.arpa | arpa2fst - | fstprint | utils/eps2disambig.pl | \
    utils/s2eps.pl | fstcompile --isymbols=$lang/words.txt \
    --osymbols=$lang/words.txt --keep_isymbols=false --keep_osymbols=false | \
    fstrmepsilon | fstarcsort --sort_type=ilabel > $lang/G.fst
fi

echo
echo "===== TRIE GRAPH  ====="
echo
gmm=exp/dnn8c_BN_fmllr-gmm_largLM
if [ $stage -le 5 ]; then
    utils/mkgraph.sh data/lang exp/tri3_largeLM exp/tri3_largeLM/graph
    #utils/mkgraph.sh data/lang $gmm $gmm/graph
fi

