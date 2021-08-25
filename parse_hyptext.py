import time
import os
import sys

args = sys.argv[1:]
hyp_file = args[1]
srt_file = os.path.splitext(hyp_file)[0] + '.srt'
hyp = open(hyp_file).readlines()
last_time='0'
isTimestamp = int(args[0])
if isTimestamp is None:
	isTimestamp = 0
with open(srt_file, 'w') as srt:
	for l in hyp:
		filename = l.split()[0]
		frame = filename.split('-')[2]
		timestamp = time.strftime('%H:%M:%S', time.gmtime(int(frame)*30/1000))
		if isTimestamp == 1:
			#print(last_time + ' --> ' + timestamp)
			#print(' '.join(l.split()[1:]))
			srt.write(last_time + ' --> ' + timestamp)
			srt.write('\n')
			srt.write(' '.join(l.split()[1:]))
			srt.write('\n')
		else:
			#print(' '.join(l.split()[1:]), end='')
			#print(' ', end='')
			srt.write(' '.join(l.split()[1:]), end='')
			srt.write('\n')
			srt.write(' ', end='')
			srt.write('\n')
		last_time = timestamp
	
