import os
import sys

args = sys.argv[1:]
dirname = args[0]
out_dir = args[1]
wavscp = open(os.path.join(out_dir,'wav.scp'), 'w')
spkfile = open(os.path.join(out_dir,'utt2spk'), 'w')
for root, directory, files in os.walk(dirname):
	for filename in files:
		if filename.endswith('.wav'):
			pathfile = os.path.join(root, filename)
			file, _ = os.path.splitext(filename)
			wavscp.write(file + ' ' + pathfile + '\n')
			spk = file.split('-')[0]
			spkfile.write(file + ' ' + spk + '\n')

