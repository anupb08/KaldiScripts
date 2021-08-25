import logging
import subprocess
import tornado
import os
import util
from util.jobdb import getFilename
import json
import sox
import time
from util.jobdb import createJobIdFileInfo
from datetime import datetime
from run_speech2text_script import speech2Text
from tornado.options import options
from handlers2 import BaseHandler
from werkzeug import secure_filename


class StartFileTranscriptionHandler(BaseHandler):
	@tornado.web.asynchronous
	def post(self, *args, **kwargs):
		self.run_background(self._post, ())

	def _post(self):
		try:
			#model = self.request.arguments['model'][0].decode()
			#if model is None:
			request_id = self.request.arguments['request_id'][0].decode()
			audio_file_path = self.request.arguments['file_path'][0].decode()
			model = self.request.arguments['model'][0].decode().lower()
			models = model.split(',')
			if len(models) > 1:
				model = 'both'
			if model is None or len(model)== 0:
				model = options.configurations.get('model_name')
			timestamp = self.request.arguments['is_timestamp'][0].decode()
			if timestamp is None or len(timestamp) == 0:
				timestamp = options.configurations.get('is_timestamp')
			print(model, audio_file_path, timestamp)
			if not os.path.exists(audio_file_path):
				return json.dumps(util.Response(status=False, message="Requested audio/video file does not exist", data={}).__dict__,
                              cls=util.CustomJSONEncoder)
			if audio_file_path.endswith('.mp3') or audio_file_path.endswith('.mp4'):
				cmd = 'ffmpeg -i ' + audio_file_path + ' -ar 16000 -ac 1 -loglevel 0 -y ' + audio_file_path[:-4]+'.wav'
				print(cmd)
				os.system(cmd)
				audio_file_path = audio_file_path[:-4] + '.wav'

			if not os.path.exists(audio_file_path):
				return json.dumps(util.Response(status=False, message="Requested audio/video file does not exist", data={}).__dict__,
                              cls=util.CustomJSONEncoder)
			length = sox.file_info.duration(audio_file_path)
			duration = time.strftime('%H:%M:%S', time.gmtime(length))
			try:
				createJobIdFileInfo(request_id, audio_file_path, duration)
			except Exception as ex:
				logging.error(ex)
				return json.dumps(util.Response(status=False, message="Request not success due to DB insert error:" + str(ex), data={'filelength': duration}).__dict__,
                              cls=util.CustomJSONEncoder)

			main_file_path = os.path.join(os.getcwd(), "main.py")
			command = "python3 " + main_file_path	
			print(model, audio_file_path, timestamp, command)
			command = command + ' ' + str(audio_file_path) + ' ' + model + ' ' + timestamp + '  ' + str(request_id)
			print(command)

			#srt_path = options.configurations.get('processed_file_path')
			#command2 = "python3 SpeechToText.py " +   str(audio_file_path) + " " + srt_path 

			#out = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read()
			out = speech2Text(audio_file_path, model, timestamp, request_id)
			print(out)
			if out == -1:
				return json.dumps(util.Response(status=False, message="Request fail. Fail to start speech trancription process", data={'filelength': duration}).__dict__,
                              cls=util.CustomJSONEncoder)	

			return json.dumps(util.Response(status=True, message="Request successful. Transcription process intiated", data={'filelength': duration}).__dict__,
                              cls=util.CustomJSONEncoder)
		except Exception as ex:
			#logging.error(traceback.print_exc())
			logging.error(ex)
			return json.dumps(util.Response(status=False, message=str(ex), data={}).__dict__,
                              cls=util.CustomJSONEncoder)

