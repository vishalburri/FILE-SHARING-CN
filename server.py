import socket
import os
import random
from datetime import datetime
import hashlib
import time
import re
from stat import * 
import json
#input port and bind to the socket
port = input("PORT:")
serversocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
serversocket.bind((host, port))
serversocket.listen(5)
#change to the shared folder dir if it has permissions
try:
	if os.access('sharedfolder',os.R_OK) and os.path.exists('sharedfolder'):
 		os.chdir('sharedfolder')
except:	
	if not os.path.exists('sharedfolder'):
		print "No shared folder please create it"
	if not os.access('sharedfolder',os.R_OK):
		print "Shared folder has no permisssions"
	exit(0)
#open log file server.log
logfile=open("server.log","a+")

print "Server Listening...."

stime = datetime.now().strftime("%I:%M%p %B %d, %Y")
logfile.write("!!!!!!!!!!!!!!!!!Server started at "+ stime + "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!\n\n")
filelist=[]

def longlist(clientsocket):
	files=os.listdir('.')
	if len(files)==0:
		clientsocket.send('No files found')
		return
	for file in files:
		st = os.stat(file)
		fileName,fileExtension = os.path.splitext(file)
		if os.path.isfile(file):
			fileExtension='file'
		elif os.path.isdir(file):
			fileExtension='directory'	
		dictionary={}
		dictionary['Filename']=file
		dictionary['filemodify']=str(time.asctime(time.localtime(st[ST_MTIME])))
		dictionary['filehash']=hashlib.md5(open(file,'rb').read()).hexdigest()
		dictionary['filetype']=str(fileExtension)
		dictionary['filesize']=str(st[ST_SIZE])
		data=json.dumps(dictionary)	
		result ="File name:"+str(file)+"\nfile size:"+ str(st[ST_SIZE])+"\nfile modified:"+str(time.asctime(time.localtime(st[ST_MTIME])))+"\nfile type:"+str(fileExtension)+"\n"
		clientsocket.send(result)
		if clientsocket.recv(1024)!="received":
			break
		
	clientsocket.send("finish")		
	return 
	
def llist(clientsocket,args):
	clientsocket.send("received")
	response=clientsocket.recv(1024)
	files=os.listdir('.')
	i=0	
	for file in files:
		if os.path.isfile(file):
			st=os.stat(file)
			dictionary={}
			dictionary['Filename']=file
			dictionary['filemodify']=str(time.asctime(time.localtime(st[ST_MTIME])))
			dictionary['filehash']=hashlib.md5(open(file,'rb').read()).hexdigest()
			data=json.dumps(dictionary)
			clientsocket.send(data)	
			response=clientsocket.recv(1024)	
			if response!='received':
				break
	clientsocket.send("finish")		
	return 	


def shortlist(clientsocket,args):
	inputs=cli.split()
	if len(inputs)!=4:
		clientsocket.send('syntaxerror')
		#clientsocket.send('syntax error \n Format is : Index shortlist Y1-M1-D1 Y2-M2-D2')
		return
	else:
		newdate1=datetime.strptime(inputs[2],"%Y-%m-%d")
		newdate2=datetime.strptime(inputs[3],"%Y-%m-%d")
		files = os.listdir('.')
		for file in files:
			st = os.stat(file)
			origdate=datetime.strptime(time.strftime('%Y-%m-%d', time.gmtime(os.path.getmtime(file))),"%Y-%m-%d")
			fileName,fileExtension = os.path.splitext(file)
			if os.path.isfile(file):
				fileExtension='file'
			elif os.path.isdir(file):
				fileExtension='directory'	

			result ="File name:"+str(file)+"\nfile size:"+ str(st[ST_SIZE])+"\nfile modified:"+str(time.asctime(time.localtime(st[ST_MTIME])))+"\nfile type:"+str(fileExtension)+"\n"
			if newdate1 <= origdate and origdate<=newdate2:
				clientsocket.send(result)
				if clientsocket.recv(1024)!="received":
					break
		clientsocket.send("finish")
	return		
def regex(clientsocket,args):
	inputs=cli.split()
	files=os.listdir('.')
	for file in files:
		st = os.stat(file)
		fileName,fileExtension = os.path.splitext(file)
		result ="File name:"+str(fileName)+"\nfile size:"+ str(st[ST_SIZE])+"\nfile modified:"+str(time.asctime(time.localtime(st[ST_MTIME])))+"\nfile type:"+str(fileExtension)+"\n"
		if re.search(inputs[2], file):
		 	clientsocket.send(result)
		 	if clientsocket.recv(1024)!="received":
				break
	clientsocket.send('finish')
	return				

def verify(clientsocket,args):
	inputs=cli.split()
	files=os.listdir('.')
	flag=0
	for file in files:
		if file==inputs[2]:
			flag=1
	if flag==0:
		clientsocket.send('No file found')
		return
	else:
		st=os.stat(inputs[2])
		clientsocket.send("check sum:"+hashlib.md5(open(inputs[2],'rb').read()).hexdigest()+"\nTimestamp:"+str(time.asctime(time.localtime(st[ST_MTIME]))))
		return 

def checkall(clientsocket,args):
	inputs=cli.split()
	files=os.listdir('.')
	for file in files:
		st=os.stat(file)
		clientsocket.send("filename:"+file+"\ncheck sum:"+hashlib.md5(open(file,'rb').read()).hexdigest()+"\nTimestamp:"+str(time.asctime(time.localtime(st[ST_MTIME])))+"\n\n")

		if clientsocket.recv(1024)!="received":
			break
	clientsocket.send("finish")
	return		

def downloadtcp(clientsocket,args):
	inputs=args.split()
	if not os.path.exists(inputs[2]):
		clientsocket.send("No such file exists")
		return
	clientsocket.send('received')
	if inputs[1]=='TCP':
		file = open(inputs[2],'rb')
		c = file.read(1024)
		while c:
			clientsocket.send(c)
			if clientsocket.recv(1024)!="received":
				break
			c= file.read(1024)
		clientsocket.send('finish')
	hash1=hashlib.md5(open(inputs[2],'rb').read()).hexdigest()
	clientsocket.send(hash1)
	if clientsocket.recv(1024)=='senddata':
		st=os.stat(inputs[2])
		fileName,fileExtension = os.path.splitext(inputs[2])
		result ="File name:"+inputs[2]+"\nfile size:"+ str(st[ST_SIZE])+"\nfile modified:"+str(time.asctime(time.localtime(st[ST_MTIME])))+"\nMD5 hash:"+hash1
		clientsocket.send(result)
	if clientsocket.recv(1024)=='perm':
		result=str(os.stat(inputs[2]).st_mode & 0777)
		clientsocket.send(result)	


def downloadudp(clientsocket,args):
	inputs=args.split()
	if not os.path.exists(inputs[2]):
		clientsocket.send("No such file exists")
		return
	clientsocket.send('received')
	udpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	udpport=random.randint(1000,9999)
	udpsocket.bind((host,udpport))
	clientsocket.send(str(udpport))
	response,addr=udpsocket.recvfrom(1024)
	if response=="received":
		file=open(inputs[2],"rb")
		c= file.read(1024)
		while c:
			udpsocket.sendto(c,addr)
			response,addr = udpsocket.recvfrom(1024)
			if response!="received":
				break
			c=file.read(1024)
		udpsocket.sendto("finish",addr)

	hash1=hashlib.md5(open(inputs[2],'rb').read()).hexdigest()
	clientsocket.send(hash1)
	if clientsocket.recv(1024)=='senddata':
		st=os.stat(inputs[2])
		fileName,fileExtension = os.path.splitext(inputs[2])
		result ="File name:"+str(inputs[2])+"\nfile size:"+ str(st[ST_SIZE])+"\nfile modified:"+str(time.asctime(time.localtime(st[ST_MTIME])))+"\nMD5 hash:"+hash1+'\n'
		clientsocket.send(result)	

	




#Multiple times clients can get connected to this server while it is running 
while True:
	clientsocket,addr = serversocket.accept()
	print("------Got a connection from client with addr: %s------" % str(addr))
	stime1 = datetime.now().strftime("%I:%M%p %B %d, %Y")
	logfile.write("----------Got a connection from client with addr"+ str(addr) + "at"+stime1+"------\n")
	logfile.write("Requested Commands:\n")
	index=0
	#receives commands from client and execute them individually
	while True:

		index+=1
		cli = clientsocket.recv(1024)
		logfile.write(str(index)+"."+cli+"\n")
		inputs = cli.split()

 		if  len(inputs)==0 or inputs[0]=='exit':
			print "Connection closed to client"
 			stime2 = datetime.now().strftime("%I:%M%p %B %d, %Y")
 			clientsocket.close()
 			logfile.write("Connection closed to client at "+stime2+"\n")
 			
 			break	
 			
 		elif inputs[0]=="Index":
 			if inputs[1]=="longlist":
 				longlist(clientsocket)
 			elif inputs[1]=="shortlist" :
 				shortlist(clientsocket,cli)
 			elif inputs[1]=='regex':
 				regex(clientsocket,cli)
 		elif inputs[0]=="Hash":
 			if inputs[1]=="verify":
 				verify(clientsocket,cli)
 			elif inputs[1]=="checkall":
 				checkall(clientsocket,cli)
 		elif inputs[0]=="Download":
 			print str(inputs)
			if inputs[1]=="TCP":
				downloadtcp(clientsocket,cli)
			elif inputs[1]=="UDP":
				downloadudp(clientsocket,cli)
		elif inputs[0]=="Automate":
			llist(clientsocket,cli)		

 			
 	clientsocket.close()



 	








	

