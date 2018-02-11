#show that:
#master-slave server-client conenctions can be daisy-chained
#the network can be interrupted and restarted automatically
#ip address can be acquired dynamically

#notes on architecture, children automatically connect with parents
# parents are in control of server - once setup, they wait for children
# to join

#note: two inputs: data from programmer, data from client (if WALL or PROCTOR)
# to stop SELF: send command 'q'

PROCTOR_PORT=7070
WALL_PORT=6060
CLIENT_PORT=5050

from enum import Enum
import socket
import subprocess
import re
import sys
import threading
import time

#would prefer automatic detection of IP addresses rather than hard-coding
# and needing to troubleshoot connection issues months/years later
#however, this package appears limited to RPi platforms and not
# portable to other linux distros (Unix, Linaro)
#import nmap #pip3 install python-nmap
#rather, using nmap call directly through terminal is more mobile
# if needing to use other PCs as Proctor

class NODE(Enum):
	PROCTOR={"port":7070}
	WALL={"port":6060}
	HELM={"port":5050}
	
MAX_CONNECTIONS=10
CONNECTION_TIMEOUT_SECONDS=0.01

#fetch the ip addresses of all PCs in network and return as a list of Strings
def getAllAddresses():
	use_arp=False
	ip_list=[]
	if(use_arp): #have found that arp command tends to return stale or incomplete ip address listing, also not mobile across linux platforms (Unix, Linaro)
		ip_raw = subprocess.Popen(['arp','-a'], stdout=subprocess.PIPE)
		ip_hr=ip_raw.communicate()[0]#human readable ip address listing
		ip_hr_list=str(ip_hr).split('\\n')
		#regular expression: get last text between brackets()
		#https://stackoverflow.com/questions/10459455/regex-for-getting-text-between-the-last-brackets
		for ip_hr_str in ip_hr_list:
			#no idea why regex needs to be so involved within Python
			#used the following to get an output from match:
			#https://stackoverflow.com/questions/5319571/python-regex-doesnt-work-as-expected
			regex=re.compile(r"""\(([^)]*)\)[^(]*$""")
			this_ip=regex.findall(ip_hr_str)
			if(not this_ip is None and len(this_ip)>0):
				ip_list.append(this_ip[-1])
		ip_list.append(getOwnAddress()) #for testing, allow server to connect to SELF
	else:#use nmap
		ip_raw = subprocess.check_output(["nmap", "-sP", "192.168.1.0/24"])
		ip_raw=str(ip_raw)
		regex=re.compile(r"""\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}""")
		ip_list=regex.findall(ip_raw)
	return ip_list

#create and open a server.  Return None if unable to, else return socket
def createServer(host,port,max_connections=MAX_CONNECTIONS):
	skt=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	skt.settimeout(CONNECTION_TIMEOUT_SECONDS)
	try:
		skt.bind((host,port))
		skt.listen(max_connections)
		print("Opened server as: "+str(host)+", port: "+str(port))
		return skt
	except socket.error as msg:
		pass
	return None
		
#as a client, connect to a target server if possible
# return socket if one can be formed, else return None
def connectToServer(host,port):
	skt=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
	skt.settimeout(CONNECTION_TIMEOUT_SECONDS)
	try:
		skt.connect((host,port))
		print("Connected to server: "+str(host)+", port: "+str(port))
		return skt
	except socket.error as msg:
		pass #silence connection errors
	return None
	
#given a type (WALL, PROCTOR, HELM), connect to it
#return open socket connection
#if unable to find an IP address that is open under the local network 
# with the target port open, then return None
def connectToNode(target):
	if(not type(target) is type(NODE.WALL)):
		raise ValueError("Invalid node target type specified: "+str(target))
	ip_list=getAllAddresses()
	target_port=target.value["port"]
	for this_ip_addr in ip_list:
		print("try to connect: "+str(this_ip_addr))
		skt=connectToServer(this_ip_addr,target_port)
		if(not skt is None):
			return skt
	return None
	
#return the IP address of SELF as a String
def getOwnAddress():
	ip_addr_hr=subprocess.check_output(['hostname', '--all-ip-addresses'])
	regex=re.compile(r"""[0-9]+(?:\.[0-9]+){3}""")
	return regex.findall( str(ip_addr_hr) )[0]

#print('START')
#print(socket.gethostname())
#print(socket.gethostbyname('linaro-alip'))


#nmap = subprocess.Popen('nmap', stdout=subprocess.PIPE)
#ipout = nmap.communicate()[0]
#print(ipout)


#nmap = subprocess.Popen('arp', stdout=subprocess.PIPE)
#ipout = nmap.communicate()[0]
#print(ipout)

#this_ip_list=getAllAddresses()
#for this_host in this_ip_list:
#	print("candidate host: "+str(this_host))
	
#print('DONE')
	
#WALL
#accept input from PROCTOR (via client_socket)
#accept input from programmer
#print input
#send input to clients (via server_socket) pre-pended with "WALL: "
#stop if input is 'q'
	
#allow input from both the programmer, and if supplied, any clients
#when data is supplied by clients, respond with a capitalized version of the String
#when data is supplied by the programmer, terminate if 'q', else
# send to clients

#2/9/18 architecture decision:
#packets are queued
#chapter pushes packet to queue

#to deal with Python *bug* where programmers cannot peek at elements in
#queues, use separate queues for each target within the client
#ie, the ConnectionManager pulls packets from the input and pipes either 
#to a book FIFO or a chapter FIFO...

#BrokenPipeError
class NodeThread(threading.Thread):
	def __init__(self,my_name,client_socket=None,server_socket=None):
		threading.Thread.__init__(self)
		self.my_server_socket=server_socket
		self.my_client_socket=client_socket
		self.clients=[]
		self.is_alive=True
		self.my_name=my_name
		print("NodeThread.__init__")
	
	def run(self):
		while(self.is_alive):
			if(not self.my_server_socket is None): #connection from self to children
				try:
					conn, addr=self.my_server_socket.accept()
					print("New client joined: "+str(conn)+", "+str(addr))
					conn.settimeout(CONNECTION_TIMEOUT_SECONDS)
					self.clients.append(conn)
				except socket.timeout:
					pass#looking for new clients, if none found, move on
				for conn in self.clients:
					try:
						data=conn.recv(1024).decode() #locking... when a client is present... --> put in a timeout for the conn, fixed issue
						self.acknowledge(data) #this is input from the children sent back up the chain to the server
						#data=data.upper()
						#conn.send(data.encode())
					except socket.timeout:
						pass#looking for new info from existing clients, if none found, move on
			if(not self.my_client_socket is None): #connection from self to parent
				try:
					data=self.my_client_socket.recv(1024).decode()
					self.ext_input(data)
				except socket.timeout:
					pass
				
	#have found about 3 ms latency one-way for packets with ~100 characters
	def ext_input(self,in_str):
		in_str=str(in_str)
		if(in_str=='q'):
			self.is_alive=False
			return
		in_str=self.my_name+": "+in_str+" "+str(time.time())
		print("input received: "+in_str)
		ack_str=in_str+" ACK"
		if(not self.my_client_socket is None): self.my_client_socket.send(ack_str.encode()) #BrokenPipeError
		print("num clients: "+str(len(self.clients)))
		for conn in self.clients:
			conn.send(in_str.encode())
		
	#input from children sent in response to input
	def acknowledge(self,in_str):
		print("ACK received: "+str(in_str))

if __name__ == "__main__":
	print('START')
	args=sys.argv
	parent_node=None
	node_type=None
	if("PROCTOR" in args):
		node_type=NODE.PROCTOR
		args.remove("PROCTOR")
	elif("WALL" in args):
		parent_node=NODE.PROCTOR
		node_type=NODE.WALL
		args.remove("WALL")
	elif("HELM" in args):
		parent_node=NODE.WALL
		node_type=NODE.HELM
		args.remove("HELM")
	server_socket=None
	client_socket=None
	#create own server if acting as a parent/server
	if(node_type in [NODE.WALL,NODE.PROCTOR]):
		print("Create server...")
		server_socket=createServer(getOwnAddress(),node_type.value["port"])
		if(not server_socket is None): print("Created server")
		else: print("Failed to create server")
	#if there is a parent/server to connect to, do so as a child/client
	if(not parent_node is None):
		print("connect as client...")
		client_socket=connectToNode(parent_node)
		if(not client_socket is None): print("Connected as client: "+str(client_socket.getpeername()))
		else: print("Failed to connect to server")
		
	nt=NodeThread(str(node_type.name),client_socket,server_socket)
	nt.start()
	time.sleep(0.01)
	
	message=""
	while(nt.is_alive):
		message=input(' INPUT: ')
		nt.ext_input(message)
		
	#close client connection
	
	#close sockets
	if(not client_socket is None): client_socket.close()
	if(not server_socket is None): server_socket.close()
	print('DONE')
