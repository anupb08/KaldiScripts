import os
import sys
import json
import datetime
import srt

max_length = 5.0
args = sys.argv[1:]
json_file = args[0]

subs = []

with open(json_file) as jfile:
    json_dict =  json.load(jfile)
    words = json_dict['retval']['words']
    start = words[0]['start']
    text = ''
    for word in words:
        end = word['end'] 
        text = text +' '+ word['word']
        if end -start > max_length:
           s = datetime.timedelta(seconds=start) 
           e = datetime.timedelta(seconds=end)
           subs.append(srt.Subtitle(index=1, start=s, end=e, content=text.strip())) 
           text = ''
           start = word['start']
    t = srt.compose(subs)
    print(t)
