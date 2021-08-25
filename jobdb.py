import time
import os

cmd ='which python > /tmp/t'
os.system(cmd)

import mysql.connector

def getDBConnector():
	mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="mysql",
  database="jobdb"
	)
	return mydb


#mydb = getDBConnector()
#mycursor = mydb.cursor()
#mycursor.execute("DROP table jobrequest")
#mycursor.execute("CREATE TABLE jobrequest (id INT AUTO_INCREMENT PRIMARY KEY, jobid VARCHAR(255), filename VARCHAR(255), filelength VARCHAR(255), uploadeddate TIMESTAMP, jobstatus INT, transcriptfile VARCHAR(255), modeltype VARCHAR(255))")
#mycursor.execute("ALTER TABLE jobrequest ADD COLUMN date TIMESTAMP DEFAULT CURRENT_TIMESTAMP") 
#mycursor.execute("ALTER TABLE jobrequest ADD COLUMN transcriptfile VARCHAR(255)") 
#mycursor.execute("ALTER TABLE jobrequest ADD COLUMN modeltype VARCHAR(255)") 
#mycursor.execute("select * from jobrequest")

#for x in mycursor:
#  print(x)

def createJobIdFileInfo(jobId, filename, filelength, dateUploaded=None):
    mydb = getDBConnector()
    mycursor = mydb.cursor()
    datetime = time.strftime('%Y-%m-%d %H:%M:%S')
    print(datetime)
    sql = "INSERT INTO jobrequest (jobid, filename, filelength, uploadeddate, jobstatus) VALUES ('%s', '%s', '%s', '%s', %d)"
    val = (jobId, filename, filelength, datetime, 0)
    cmd = sql %(val)
    print(cmd)
    mycursor.execute(cmd)
    #mycursor.execute("INSERT INTO jobrequest (jobid, filename, filesize, uploadeddate, jobstatus) VALUES (12349, 'test.wav', 123, '2019-09-10 21:12:20', 0)")
    mydb.commit()
    mycursor.close()

def getFilename(jobid):
    mydb = getDBConnector()
    mycursor = mydb.cursor()
    sql = "select filename from jobrequest where jobid = '%s'" % str(jobid)
    print(sql)
    try:
        mycursor.execute(sql)
    except mysql.connector.Error as err:
        mycursor.close()
        print("Error on DB execution: {}".format(err))
        raise Exception("Error on DB execution")
    result = mycursor.fetchall()
    print(result[0][0])
    mycursor.close()
    return result[0][0]

def getTranscriptionStatus(jobid):
    mydb = getDBConnector()
    mycursor = mydb.cursor()
    sql = "select jobstatus from jobrequest where jobid = '%s'"% str(jobid)
    print(sql)
    try:	
        mycursor.execute(sql)
    except mysql.connector.Error as err:
        mycursor.close()
        print("Error on DB execution: {}".format(err))
        raise Exception("Error on DB execution")
    result = mycursor.fetchall()
    mycursor.close()
    mycursor = None
    print(result[0][0])
    if len(result)==0:
        raise Exception("Error on DB execution")
    return result[0][0]

def getTranscriptFilename(jobid):
    mydb = getDBConnector()
    mycursor = mydb.cursor()
    sql = "select transcriptfile from jobrequest where jobid = '%s'" % str(jobid)
    print(sql)
    mycursor.execute(sql)
    result = mycursor.fetchall()
    print(result)
    mycursor.close()
    return result[0][0]

#createJobIdFileInfo('1234567', '/home/hitesh/upload/PROF._AMIT_JAIN_INTRODUCTION_.wav', '00:04:13') 
#getFilename(12349)
'''
def test():
	try:
	   ret = getTranscriptionStatus(1234567)
	except Exception as ex:
	   print("error")
	print(ret)
	return ret
'''

