perl utils/map_arpa_lm.pl data2/lang/words.txt < data2/local/tmp/lm.arpa > t.int
/home/user/kaldi/src/lmbin/arpa-to-const-arpa --bos-symbol=152501 --eos-symbol=152502 t.int data2/lang_rescore/G.carpa
