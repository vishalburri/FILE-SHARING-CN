import socket
import os
import random
from datetime import datetime
import hashlib
import time
import threading
import json
from stat import *
import signal
clientsocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port = input("PORT:")

try:
	if os.access('destfolder',os.W_OK) and os.path.exists('destfolder'):
 		os.chdir('destfolder')
except:	
	if not os.path.exists('destfolder'):
		print "No destination folder please create it"
	elif not os.access('destfolder',os.W_OK):
		print "Destination folder has no permisssions"
	exit(0)

try:
 	clientsocket.connect((host,port))
except:
 	clientsocket.close()
 	print "No server found with above address"
 	exit(0)

print "--------Connection Established to server-------"

logfile=open("client.log","a+")

ctime = datetime.now().strftime("%I:%M%p %B %d, %Y")
logfile.write(" Connected to " + host + " at " + ctime + " -------\nCommands Sent:\n")	

index=0	

def indexget(args):
	#sends args to server
	clientsocket.send(args)
	while True:
#receives response data from server
		response=clientsocket.recv(1024)
		if response=="finish":
			break
		if response=="syntaxerror":
			print "syntax error \n Format is : Index shortlist Y1-M1-D1 Y2-M2-D2"
			break
		clientsocket.send("received")
		if response!='finish':
			print response
	return	

def hashget(args):
	clientsocket.send(args)
	response=clientsocket.recv(1024)
	if response!='finish':
		print response
	return 

def filedownload(args):
	clientsocket.send(args)
	inputs=args.split()
	response = clientsocket.recv(1024)
	if len(inputs)!=3:
		print 'Syntax error\n Format: Download TCP/UDP filename'
		return
	if response!='received':
		print response
		return
	if inputs[1]=='TCP':
		file = open(inputs[2],'wb+')
		while True:
			response = clientsocket.recv(1024)
			if response=="finish":
				break
			file.write(response)
			clientsocket.send('received')
		file.close()
	elif inputs[1]=='UDP':
		udpport=int(clientsocket.recv(1024))
		udpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		socketaddr = (host,udpport)
		udpsocket.sendto("received",socketaddr)
		file=open(inputs[2],"wb+")
		while True:
			response,address = udpsocket.recvfrom(1024)
			if response=="finish":
				break
			file.write(response)
			udpsocket.sendto("received",address)
		file.close()
		udpsocket.close()

	hash2=hashlib.md5(open(inputs[2],'rb').read()).hexdigest()
	hash1=clientsocket.recv(1024)
	if hash1!=hash2:
		print 'File sent Failed'
	else:
		clientsocket.send("senddata")
		response=clientsocket.recv(1024)
		if response!='finish':
			print response
		print "File has been Downloaded successfully"
		clientsocket.send('perm')
		response=clientsocket.recv(1024)
		os.chmod(inputs[2],int(response))

def automate(args):
	clientsocket.send(args)

	response = clientsocket.recv(1024)
	clientsocket.send("ok")
	if response!='received':
		return
	sharedfolderfiles=[]
	sharedfolderhash=[]
	sharedfoldermodify=[]
	files=os.listdir('.')
	
	while True:
		response=clientsocket.recv(1024)
		if response=="finish":
			break
		clientsocket.send('received')
		#sharedfolderfiles.append(json.loads(response))
		dictionary=json.loads(response)
		sharedfolderfiles.append(dictionary['Filename'])
		sharedfolderhash.append(dictionary['filehash'])
		sharedfoldermodify.append(dictionary['filemodify'])

	count=0
	count1=0
	l=len(sharedfolderfiles)
	for i in range(0,l):

		for file in files:
			count1+=1
			st=os.stat(file)
			if sharedfolderfiles[i]==file and sharedfolderhash[i]!=hashlib.md5(open(file,'rb').read()).hexdigest() and datetime.strptime(sharedfoldermodify[i],"%a %b %d %H:%M:%S %Y") > datetime.strptime(str(time.asctime(time.localtime(st[ST_MTIME]))),"%a %b %d %H:%M:%S %Y"):
				filedownload('Download TCP '+sharedfolderfiles[i])
			elif sharedfolderfiles[i]!=file:
				count+=1
		if count==count1:
			filedownload('Download TCP '+sharedfolderfiles[i])
	return						

	
exit=0	#threading.Timer(1, automate(args)).start()
def signal_handler(signal,frame):
	global exit
	print('Automation stopped')
	exit=1


while True:
 	index=index+1
 	cli=""
 	cli=raw_input("Prompt>>")
 	inputs = cli.split()
 	logfile.write(str(index) + "." + cli+"\n")
 	
 	if cli=="":
 		index-=1
 		continue
 	elif len(inputs)==0:
 		clientsocket.send(cli)
 		print "---------Connection closed to server ---------"
 		ctime1 = datetime.now().strftime("%I:%M%p %B %d, %Y")
 		clientsocket.close()
 		logfile.write("---------Connection closed to server at "+ctime1+"-----------\n")
 		logfile.close()
 		exit(0)	
 	elif inputs[0]=="exit":
 		clientsocket.send(cli)
 		print "---------Connection closed to server ---------"
 		ctime1 = datetime.now().strftime("%I:%M%p %B %d, %Y")
 		clientsocket.close()
 		logfile.write("---------Connection closed to server at "+ctime1+"-----------\n")
 		logfile.close()
 		exit(0)
 		
 	elif inputs[0]=="Index":
 		indexget(cli)
 	elif inputs[0]=="Hash" and inputs[1]=="verify":
 		hashget(cli)
 	elif inputs[0]=="Hash" and inputs[1]=="checkall":
 		indexget(cli)

 	elif inputs[0]=="Download":
 		filedownload(cli)
 	elif inputs[0]=="Automate":
 		while True:
 			automate(cli)
 			signal.signal(signal.SIGTSTP,signal_handler)
 			time.sleep(3)
 			if exit:
 				exit=0
 				break
 			
 	else:
 		print "Invalid Command"

clientsocket.close()


		





		




 		
 		




 	



 	
 	

 	


	



