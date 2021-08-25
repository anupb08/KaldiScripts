#!/bin/bash

. ./path.sh || exit 1
. ./cmd.sh || exit 1
nj=20 # number of parallel jobs - 1 is perfect for such a small data set
decode_nj=2
threads=20
lm_order=3
stage=13

. utils/parse_options.sh || exit 1
[[ $# -ge 1 ]] && { echo "Wrong arguments!"; exit 1; }

if [ $stage -le 0 ]; then
	# Making spk2utt files
	utils/utt2spk_to_spk2utt.pl data/train/utt2spk > data/train/spk2utt
	utils/utt2spk_to_spk2utt.pl data/test/utt2spk > data/test/spk2utt
fi

echo
echo "===== FEATURES EXTRACTION ====="
echo
# Making feats.scp files

if [ $stage -le 1 ]; then
	mfccdir=mfcc
	# Uncomment and modify arguments in scripts below if you have any problems with data sorting
	# utils/validate_data_dir.sh data/train # script for checking prepared data - here: for data/train directory
	# utils/fix_data_dir.sh data/train # tool for data proper sorting ifneeded - here: for data/train directory

	steps/make_mfcc.sh --nj $nj --cmd "$train_cmd" data/train exp/make_mfcc/train $mfccdir
	steps/make_mfcc.sh --nj $nj --cmd "$train_cmd" data/test exp/make_mfcc/test $mfccdir

	# Making cmvn.scp files
	steps/compute_cmvn_stats.sh data/train exp/make_mfcc/train $mfccdir
	steps/compute_cmvn_stats.sh data/test exp/make_mfcc/test $mfccdir
fi

echo
echo "===== PREPARING LANGUAGE DATA ====="
echo

if [ $stage -le 2 ]; then
	# Preparing language data
	utils/prepare_lang.sh data/local/dict "<UNK>" data/local/lang data/lang
fi
echo
echo "===== LANGUAGE MODEL CREATION ====="
echo "===== MAKING lm.arpa ====="
echo

if [ $stage -le 3 ]; then
	local=data/local
	mkdir $local/tmp
	ngram-count -order $lm_order -write-vocab $local/tmp/vocab-full.txt -wbdiscount -text $local/corpus.txt -lm $local/tmp/lm.arpa
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
echo "===== MONO TRAINING ====="
echo
if [ $stage -le 5 ]; then
	steps/train_mono.sh --nj $nj --cmd "$train_cmd" data/train data/lang exp/mono || exit 1
	echo
	echo "===== MONO DECODING ====="
	echo
	utils/mkgraph.sh --mono data/lang exp/mono exp/mono/graph || exit 1 
	steps/decode.sh --config conf/decode.config --nj 2 --cmd "$decode_cmd" \
	--num-threads 20 exp/mono/graph data/test exp/mono/decode 
fi

echo
echo "===== TRI1 (first triphone pass) TRAINING ====="
echo
if [ $stage -le 6 ]; then
	steps/align_si.sh --nj $nj --cmd "$train_cmd" data/train data/lang exp/mono \
	exp/mono_ali || exit 1

	steps/train_deltas.sh --cmd "$train_cmd" 2000 20000 data/train data/lang \
	exp/mono_ali exp/tri1 || exit 1
	echo
	echo "===== TRI1 (first triphone pass) DECODING ====="
	echo
	utils/mkgraph.sh data/lang exp/tri1 exp/tri1/graph || exit 1
	steps/decode.sh --config conf/decode.config --nj 2 --cmd "$decode_cmd" \
	--num-threads 20 exp/tri1/graph data/test exp/tri1/decode
fi

if [ $stage -le 7 ]; then
  steps/align_si.sh --nj $nj --cmd "$train_cmd" \
    data/train data/lang exp/tri1 exp/tri1_ali || exit 1

  steps/train_lda_mllt.sh --cmd "$train_cmd" \
    4000 50000 data/train data/lang exp/tri1_ali exp/tri2 || exit 1

  utils/mkgraph.sh data/lang exp/tri2 exp/tri2/graph || exit 1

  steps/decode.sh --nj $decode_nj --cmd "$decode_cmd" \
    --num-threads $threads \
    exp/tri2/graph data/test exp/tri2/decode || exit 1
fi

if [ $stage -le 8 ]; then
  steps/align_si.sh --nj $nj --cmd "$train_cmd" \
    data/train data/lang exp/tri2 exp/tri2_ali || exit 1

  steps/train_sat.sh --cmd "$train_cmd" \
    5000 100000 data/train data/lang exp/tri2_ali exp/tri3 || exit 1

  utils/mkgraph.sh data/lang exp/tri3 exp/tri3/graph || exit 1

  steps/decode_fmllr.sh --nj $decode_nj --cmd "$decode_cmd" \
    --num-threads $threads \
    exp/tri3/graph data/test exp/tri3/decode || exit 1
fi

if [ $stage -le 9 ]; then
  steps/align_fmllr.sh --nj $nj --cmd "$train_cmd" \
    data/train data/lang exp/tri3 exp/tri3_ali || exit 1

  steps/make_denlats.sh --transform-dir exp/tri3_ali --nj $nj --cmd "$decode_cmd" \
    data/train data/lang exp/tri3 exp/tri3_denlats || exit 1

  steps/train_mmi.sh --cmd "$train_cmd" --boost 0.1 \
    data/train data/lang exp/tri3_ali exp/tri3_denlats \
    exp/tri3_mmi_b0.1 || exit 1

  for iter in 4; do
  steps/decode.sh --transform-dir exp/tri3/decode --nj $decode_nj --cmd "$decode_cmd" --iter $iter \
    --num-threads $threads \
    exp/tri3/graph data/test exp/tri3_mmi_b0.1/decode_test_it$iter || exit 1
  done
fi

if [ $stage -le 10 ]; then
  # Run the DNN recipe on fMLLR feats:
  local/nnet/run_dnn.sh || exit 1
fi

if [ $stage -le 11 ]; then
  # DNN recipe with bottle-neck features
  local/nnet/run_dnn_bn.sh || exit 1;
fi

if [ $stage -le 12 ]; then
# Run the nnet2 multisplice recipe
 local/online/run_nnet2_ms.sh || exit 1;
fi

if [ $stage -le 13 ]; then
 # local/nnet3/run_tdnn.sh  # better absolute results
  local/nnet3/run_tdnn_lstm.sh || exit 1;
fi

if [ $stage -le 14 ]; then
  local/nnet3/run_lstm.sh  || exit 1;
fi

if [ $stage -le 15 ]; then
  local/run_nnet2.sh || exit 1;
fi
