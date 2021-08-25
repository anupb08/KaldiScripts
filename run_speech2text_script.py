import os
import sys
import  subprocess
from subprocess import Popen, PIPE


def speech2Text(filename, model, timestamp, jobid):
	print(filename)
	print(timestamp)

	if model == 'model-1':
		model_type = '1'
	elif model == 'model-2':
		model_type = '2'
	elif model == 'both':
		model_type = '3'
	elif model == 'model-1,model-2':
		model_type = '3'
	else:
		model_type = '1'
	   
	
	#cmd = "pocketsphinx_continuous -hmm model_parameters/nptel.cd_cont_4000/ -lm " +lm + " -dict " + dictionary + " -logfn /dev/null -infile " + filename #+" > t"
	file_dir = os.path.splitext(filename.split('/')[-1])[0].replace('.', '-').replace(' ', '-')
	cmd = '/mnt/md0/SpeechRecognitionServer/runme ' + filename + ' ' + model_type + ' ' + timestamp + ' '+ str(jobid) + ' ' + str(jobid) + ' ' + '> logs/' +str(jobid)
	print(cmd)    
	#transcript = subprocess.Popen(cmd ,cwd='./', shell=True , stdout=PIPE).stdout.read().decode(sys.stdout.encoding)
	try:
		res = subprocess.Popen(cmd ,cwd='./', shell=True)
	except:
		print("Fail to start speech trancription process")
		return -1
	print(res)
	return 1


