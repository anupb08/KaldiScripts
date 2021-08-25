import json
import sys
import os

args = sys.argv[1:]
file_name = args[0]

out_json = args[1] #os.path.join('JSON',file_name + '.json')
#words_timestamp_file = '/home/user/kaldi/egs/nptel/s5/exp/dnn8f_BN_pretrain-dbn_dnn_smbr/decode_' +file_name+ '_it4_rescore/score_16/' + file_name + '.ctm'
words_timestamp_file = args[2]#'/home/user/kaldi/egs/nptel/s5/exp/dnn8f_BN_pretrain-dbn_dnn_smbr/decode_' +file_name+ '_it4/score_16/' + file_name + '.ctm'
if not os.path.isfile(words_timestamp_file):
	print('Could not process file')
words_timestamp = open(words_timestamp_file).readlines()
words = list()
punct = list()
speakers = [{"@id": "S0","gender": "F"}, {"@id": "S1","gender": "F"}]
segments = list()
index = 0
last_line = None
offset = 0.0
i = 0
for line in words_timestamp:
	line = line.strip()
	list_entity = line.split()
	start = float(list_entity[2])
	if index > 0 and float(last_line.split()[2]) > start:
		segment = dict()
		segment["@type"] = "Segment"
		segment["start"] = offset
		segment_end = (int(last_line.split()[0].split('-')[2])*30)/1000
		segment["duration"] = segment_end - offset
		offset = segment_end
		segment["bandwidth"] = "S"
		segment["speaker"] = {"@id": "S"+str(i),"gender": "id"}
		segments.append(segment)
		i = i+1
	dur = float(list_entity[3])
	end = start + dur
	last_line = line
	word = list_entity[4]
	punct.append(word)
	words.append({"start":offset+ start, "confidence": 0.9, "end": offset +end, "word": word, "punct": word, "index": index})
	index = index + 1

segment = dict()
segment["start"] = offset
segment_end = (int(last_line.split()[0].split('-')[2])*30)/1000
segment["duration"] = segment_end - offset
offset = segment_end
segment["@type"] = "Segment"
segment["bandwidth"] = "S"
segment["speaker"] = {"@id": "S"+str(i),"gender": "id"}
segments.append(segment)

texts = ' '.join(punct)

#timestamp_transcript = open(srt_file).readlines()
def con_float(t):
	h = int(t.split(':')[0])
	m = int(t.split(':')[1])
	s = int(t.split(':')[2])
	return h*3600+m*60+s
'''
for line in timestamp_transcript:
	if len(line.split('-->')) < 2:
		continue
	line = line.strip()
	segment = dict()
	start = con_float(line.split('-->')[0])
	end = con_float(line.split('-->')[1])
	dur = end - start
	segment["@type"] = "Segment"
	segment["start"] = start
	segment["duration"] = dur
	segment["bandwidth"] = "S"
	segment["speaker"] = speakers[0]
	segments.append(segment)
'''
with open(out_json, 'w') as json_timestamp:
	timestamp = dict()
	timestamp["action"] =  "audio-transcribe"
	timestamp["retval"] = None
	timestamp["elapsed"] = 0.091
	timestamp["servertime"] = "20181102111317.9727"
	retval = dict()
	retval["status"] = True
	retval["wonid"] = "octo:2692ea33-d595-41d8-bfd5-aa7f2d2f89ee"
	retval["punct"] = texts
	retval["words"] = words
	retval["segmentation"] = dict()
	retval["segmentation"]["metadata"] = {"version": "0.0.10"}
	retval["segmentation"]["@type"] = "AudioFile"
	retval["segmentation"]["speakers"] = speakers
	retval["segmentation"]["segments"] = segments
	timestamp["retval"] = retval
	json.dump(timestamp, json_timestamp, indent=2)

