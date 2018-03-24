"""
   Copyright 2018 Scott Almond

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

Purpose:
A helper class for ConnectionManager to serve as either a server
or client to external actors
messages from send() are sent outbound from this PC immediately
inbound messages are queued in the ConnectionManager FIFO and are
accessible via peek() and pop() in that class
Note: A client instance will automatically seek servers until one is found
 and will reestablish the connection if lost

Usage:

TO DO:
really need a thread lock on the server_socket connection to force
sequential operation in sections.  Ex. Connecting to a server and
sending the client identification
message may be interrupted by an extenral thread sending a packet, which confuses server
since the server is expecting an ID packet but gets live data instead
also needed to ensure socket does not revert to None randly during execition
refer to AttributionErrors throughout code

future version should use 'payload' rather than 'package' jargon

note: interrupted socket connection can lead to malformed json packet
whick throws json.decoder.JSONDecodeError

"""


import threading
import queue
import json
import socket
import subprocess
import time
import re #regular expressions
from enum import Enum

class NODE_DIRECTION(Enum):
	CLIENT=0
	SERVER=1

#needs to match Chapter setup to satisfy isSocketFor()
class NODE_TYPE(Enum):
	PROCTOR={"port":7070}
	WALL={"port":6060}
	#HELM={"port":5050}

class NodeManager(threading.Thread):
	MAX_CONNECTIONS=10 #max clients that can connect to this server
	CONNECTION_TIMEOUT_SECONDS=0.01 #how long to listen for new connections before doing something else
	MAX_PACKET_SIZE_BYTES=1024 #presumed maximum size of a packet from an external PC
	
	#source_node_type is a String (representing name of Book running on this PC)
	#target_node_types is a String - append additional clients with appendClient()
	#is_server is a Boolean - indicates whehter the Book running on this PC is acting
	# as a server or a client in this NM relationship
	def __init__(self,connection_manager,source_node_title,target_node_title,is_server,is_enabled=True,is_debug=False):
		threading.Thread.__init__(self)
		self._is_alive=True
		self._is_enabled=is_enabled
		self.is_debug=is_debug
		self.connection_manager=connection_manager
		self.is_server=is_server
		self.nodes=[]
		self.appendTarget(target_node_title)
		self.source_node_title=source_node_title
		if(self.is_server):
			port=self.__getPortForServer(source_node_title)
			self.server={"pointer":None,"port":port,"is_error":False}
		
	#helper method for constructor - allow clients to be added
	def appendTarget(self,target_node_title):
		#target name, target pointer, is_error
		self.nodes.append({"target_node_title":target_node_title,"target_pointer":None,"is_error":False})
			
	def __isPrintEnabled(self):
		return self.is_debug and self._is_enabled
			
	#infinite loop looking for input from sockets, enqueuing to
	# ConnectionManager all that is found
	def run(self):
		if(self.__isPrintEnabled()): print("NodeManager.run: enter")
		while(self._is_alive):
			#time.sleep(1)
			#print("NM -- "+str(time.time()))
#			print("NodeManager.run: wait for input: "+str(time.time()))
			if(not self._is_enabled):
				time.sleep(0.1)
			else:
				for node_index in range(len(self.nodes)):
					node=self.nodes[node_index]
					conn=node["target_pointer"] #get socket
					if(self.__nodeReady(node)):
						#listen for input from existing clients, if not closed
						#note: may be operating on None type for node["target_pointer"]
						# due to multi-threaded access to dictionary
						try:
							data=conn.recv(self.MAX_PACKET_SIZE_BYTES)
							self.receive(data.decode())
						except socket.timeout:
							pass #if no input received, then move on to next task
						except AttributeError:
							pass #type changed to None during execution
						except ConnectionResetError:
							node["is_error"]=True
						#there may be errors related to sending data over a closed connection... --> no action upon is_error
						#BrokenPipeError --> set is_error=True
						# if is_server, then server["is_error"]=True
		self.__disposeNode() #when done with thread, close connections
				
	#Establish or re-establish connections with external PCs
	# an external thread in ConnectionManger regularly calls this method
	def connect(self):
		if(self.__isPrintEnabled()): print("NodeManager.connect: enter")
		if(not self._is_enabled):
			return #skip TCP tasks if NodeManager is acting as a dummy class
		is_action_needed=not self.isReady()
		if(is_action_needed): #skip resource-intensive tasks if no action is needed
			if(self.is_server): #this PC is server, has many clients
				if(self.server["is_error"]):
					self.__disposeNode()
				if(self.server["pointer"] is None):
					self.server["pointer"]=self.__createServer(self.server["port"])
					self.server["is_error"]=False
				server_socket=self.server["pointer"]
				#listen for new clients
				try:
					conn, addr=server_socket.accept()
					if(self.__isPrintEnabled()): print("NodeManager.connect: New client joined: "+str(conn)+", "+str(addr))
					identity_packet=conn.recv(self.MAX_PACKET_SIZE_BYTES).decode()
					if(self.__isPrintEnabled()): print("NodeManager.connect: identity packet: "+str(identity_packet))
					self.receive(identity_packet,conn)
					conn.settimeout(self.CONNECTION_TIMEOUT_SECONDS)
					
					#raise NotImplementedError("NodeManager.connect: need to identify new client and add to the node list in the correct location")
					
				except socket.timeout:
					pass #looking for new clients, if none found, move on
				except AttributeError:
					pass #server_socket is None
			else: #this PC is a client, connected to one server
				#seek servers for uninitiated connection
				ip_list=self.getAllAddresses() #called once here instead of in __connectToServer
				# to conserve execution time (takes several seconds to run)
				for node_index in range(len(self.nodes)):
					node=self.nodes[node_index] #for node in self.nodes - makes a deep copy of node, but using indexing does not - unexpected behavior in python
					if(not self.__nodeReady(node)):
						#close existing connections if malformed
						if(not node["target_pointer"] is None):
							self.__disposeNode(node)
							node["target_pointer"]=None
							node["is_error"]=False
						port=self.__getPortForServer(node["target_node_title"])
						#connect to discoverd servers
						this_server=self.__connectToServer(port,ip_list)
						node["target_pointer"]=this_server #may be None if unable to establish connection
						#immediately after connecting to the server, send 
						# a client identification package so the server can respond to queries
						if(not this_server is None):
							identity_packet=self.__getClientConnectionMessage()
							self.send(identity_packet)
						
	#call to close out open threads
	def dispose(self):
		if(self.__isPrintEnabled()): print("NodeManager.dispose: enter")
		self._is_alive=False
		
	#when input is received from an external PC, add it to the internal queue
	#message is a json encoded binary
	def receive(self,message,socket=None):
		message_decoded=json.loads(message)
		if(len(message)>0):
			if(self.__isPrintEnabled()): print("NodeManager.receive: message: "+str(message_decoded))
			if(message_decoded["target_scope"]=="NodeManager"):#if target is NodeManager, parse here, else flow upward
				self.receiveCommand(message_decoded,socket)
			else:
				self.connection_manager.receive(message_decoded)
		
	#received a command from an external PC destined for this NodeManager
	#packet is a dictionary
	def receiveCommand(self,packet,socket=None):
		command=packet["command"]
		package=packet["package"] #WALL (when being sent to PROCTOR)
		if(command=="client_identification"):
			if(self.is_server):
				if(self.__isPrintEnabled()): print("NodeManager.receiveCommand: client_identification")
				#look through nodes for matching connection
				# and assign this socket in that list
				for node_index in range(len(self.nodes)):
					node=self.nodes[node_index] #pointer to node rather than (shallow?) copy
					if(package==node["target_node_title"]):
						node["target_pointer"]=socket
		
	#determine if this is the socket relationship for a given book relationship
	#inputs are strings
	def isSocketFor(self,source_book_title,target_book_title):
		return False
		
	#given a message (json.dumps binary) bound for a target, send it
	# outbound out of this PC
	def send(self,message):
		#identify the socket to send the packet out over...
		message_decoded=json.loads(message)
		if(self.__isPrintEnabled()): print("NodeManager.send: message: "+str(message_decoded))
		if(self.__isPrintEnabled()): print("NodeManager.send: iterating over number of nodes: "+str(len(self.nodes)))
		for node in self.nodes:
			target_node_title=node["target_node_title"]
			target_message_title=message_decoded["target_book_title"]
			socket=node["target_pointer"]
			if(target_node_title==target_message_title):
				if(self.__nodeReady(node)):
					try:
						if(self.__isPrintEnabled()): print("NodeManager.send: sending...")
						if(self._is_enabled): socket.send(message.encode())
						return True
					except BrokenPipeError:
						node["is_error"]=True
						return False
					except AttributeError: #socket is None - will be fixed by connect() in another thread
						return False
				break
		return False
		#note: may be operating on None type for node["target_pointer"]
		# due to multi-threaded access to dictionary
		#BrokenPipeError
		
	#set up a server on this PC, return the socket if node is successfully created
	def __createServer(self,port,host=None,max_connections=None):
		if(max_connections is None): max_connections=self.MAX_CONNECTIONS
		if(host is None): host=self.getOwnAddress()
		skt=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		skt.settimeout(self.CONNECTION_TIMEOUT_SECONDS)
		try:
			skt.bind((host,port))
			skt.listen(max_connections)
			if(self.__isPrintEnabled()): print("NodeManager.createServer: Opened server as: "+str(host)+", port: "+str(port))
			return skt
		except socket.error as msg:
			pass
		return None
		
	#look through list of ip addresses for a server to connect to
	# return the socket if a connection can be formed, else return None
	def __connectToServer(self,port,ip_list=[]):
		for host in ip_list:
			skt=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			skt.settimeout(self.CONNECTION_TIMEOUT_SECONDS)
			try:
				skt.connect((host,port))
				if(self.__isPrintEnabled()): print("Connected to server: "+str(host)+", port: "+str(port))
				return skt
			except socket.error as msg:
				pass #silence connection errors
		return None
		
	#GET/SET
		
	#get the packet that is sent by the client on this computer when first
	# connecting to a remote server to identify this PC
	def __getClientConnectionMessage(self):
		packet=self.connection_manager.getPacketFor(
			source_book_title=self.source_node_title,
			source_chapter_title=None,
			target_book_title=self.nodes[0]["target_node_title"],
			target_scope="NodeManager",
			command="client_identification",
			package=self.source_node_title
			)
		return packet
		
	def getStatus(self):
		output=""
		output+="NodeManager "+("Server" if self.is_server else "Client")+"\n"
		if(self.is_server):
			output+="  --\n"
			output+="  Source: "+self.source_node_title+"\n"
			output+="  Server: "+("None" if self.server["pointer"] is None else "Exists")+"\n"
			output+="  Health: "+("Error" if self.server["is_error"] else "Good")+"\n"
		for node in self.nodes:
			output+="  --\n"
			output+="  Source: "+self.source_node_title+"\n"
			output+="  Target: "+node["target_node_title"]+"\n"
			output+="  Socket: "+("None" if node["target_pointer"] is None else "Exists")+"\n"
			if(not node["target_pointer"] is None):
				output+="  DEBUG: "+str(node["target_pointer"].fileno())+"\n"
			output+="  Health: "+("Error" if node["is_error"] else "Good")+"\n"
		return output
		
	#given the String title of a server, return the Int port number
	def __getPortForServer(self,server_title):
		return NODE_TYPE[server_title].value["port"]
		
	#returns IP address String
	def getOwnAddress(self):
		ip_addr_hr=subprocess.check_output(['hostname', '--all-ip-addresses'])
		regex=re.compile(r"""[0-9]+(?:\.[0-9]+){3}""")
		return regex.findall( str(ip_addr_hr) )[0]
		
	#fetch the ip addresses of all PCs in local network and return as a list of Strings
	def getAllAddresses(self):
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

	def isReady(self):
		is_ready=True
		for node in self.nodes:
			if(not self.__nodeReady(node)): is_ready=False
		return is_ready
		
	def __nodeReady(self,node):
		#if socket is closed, set is_error=True
		
		return not node["target_pointer"] is None and not node["is_error"]
		
	#disconnect socket cleanly - use None to close all sockets
	def __disposeNode(self,node=None):
		for node in self.nodes:
			socket=node["target_pointer"]
			if(not socket is None): socket.close()
		if(self.is_server):
			socket=self.server["pointer"]
			if(not socket is None): socket.close() #may still throw some errors due to thread concurrency
			

	#@property
	#def is_alive(self): return self._is_alive

	#@is_alive.setter
	#def is_alive(self, value):
		#if(not value):
			#self._is_alive = False
		#else:
			##only allow external actors to set is_alive to False to
			##avoid conflicting access/revival in multi-threaded environment
			#raise ValueError("Cannot configure is_alive to: "+str(value))
