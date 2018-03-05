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
This class as a kind of virtual mail sorter.  Messages from other PCs, 
 both servers and clients, come into this class through TCP connections.
 The messages are queued for when the CM/Book/Chapter is ready to read them.
 Conversely, when this PC's CM/Book/Chapter is ready to send, messages
 are routed to the appropriate PC based on the contents of the packet

Assumptions:


Usage:
python3 -m util.ConnectionManager WALL

"""

import threading
import queue
import json
import socket
import subprocess
from enum import Enum

import util.Book
from util.Book import BOOK_TYPE
import util.Chapter
from util.NodeManager import NodeManager

#needs to match Chapter setup to satisfy isSocketFor()
#precon: ports are uniquely assigned to each PC to aid in automatic
# establishment of conenctions using nmap
class NODE_TYPE(Enum):
	PROCTOR={"port":7070}
	WALL={"port":6060}
	HELM={"port":5050}

class ConnectionManager(threading.Thread):
	#precon: master(server)-slave(client) relationship is unique
	BOOK_MASTER_RELATIONSHIP=[ #[master,slave]...
		[BOOK_TYPE.PROCTOR.name,BOOK_TYPE.WALL.name],
		[BOOK_TYPE.WALL.name,BOOK_TYPE.HELM.name]
		]
	
	def __init__(self,this_book_title,is_debug=False):
		threading.Thread.__init__(self)
		self._is_alive=True
		self.is_debug=is_debug
		self.book_title=this_book_title
		self.nodes=[]
		self.inbound_queue=queue.Queue()
		server_nm=None
		#create NodeManagers to represent the connections this PC has with
		# external actors
		for relationship in self.BOOK_MASTER_RELATIONSHIP:
			if(relationship[0]==self.book_title):
				if(server_nm is None):
					server_nm=NodeManager(self,relationship[0],relationship[1],True,is_debug)
					self.nodes.append(server_nm)
				else:
					server_nm.appendTarget(relationship[1])
			elif(relationship[1]==self.book_title):
				client_nm=NodeManager(self,relationship[1],relationship[0],False,is_debug)
				self.nodes.append(client_nm)
		if(self.is_debug): print("ConnectionManager.init: number of NMs: "+str(len(self.nodes)))
		for node in self.nodes:
			node.start() #kick off threads that will seek connections and listen to input
		
	def clean(self):
		pass
		
	def dispose(self):
		if(self.is_debug): print("ConnectionManager.dispose()")
		self._is_alive=False #it appears threads also have an is_alive bool and there is a conflict, so set _is_alive directly
		for node in self.nodes:
			node.dispose()
		
	def run(self):
		if(self.is_debug): print("ConnectionManager.run: enter method")
		while(self._is_alive):
			#time.sleep(1)
			if(self.is_debug): print("CM -- "+str(time.time()))
			if(self.is_debug): print(self.getStatus())
			if(not self.isReady()):
				if(self.is_debug): print("ConnectionManager.run: Attempt to (re-)connect nodes...")
			for node in self.nodes:
				node.connect()
				#call in an infinite loop to reestablish any dropped connections
	
	#external PC sends package to this PC
	#package is a dictinary
	def receive(self,package):
		if(self.is_debug): print("ConnectionManager.receive: "+str(package))
		self.inbound_queue.put(package)
		
	#scope is a string like "Book" or "Chapter"
	#returns the packet on the top of the queue
	# if none is thre, returns None
	def pop(self,scope):
		if(self.inbound_queue.empty()):
			return None
		peek=self.inbound_queue.queue[0]
		if(peek["target_scope"]==scope):
			try:
				return self.inbound_queue.get(block=False)
			except queue.Empty:
				pass
		return None
		
	#this PC sending a package out bound to another PC
	#packet is json.dumps encoded
	def send(self,packet):
		#TODO: attempt to send to all node managers, only relevant node manager will comply
		for node in self.nodes:
			is_success=node.send(packet)
			if(is_success): return True
		return False
		
	#query whether the link to a particular book has been established
	# assumes each PC has a unique name and only exists once as either a server or client, not both
	#if target_book_title is None, then check the status of all books together
	def isReady(self,target_book_title=None):
		if(target_book_title is None):
			for nm in self.nodes:
				if(not nm.isReady()): return False
			return True
		else:
			raise NotImplementedError("ConnectionManager.isReady: Still need to implement check for specific PCs existing in network")
		
	#def connectToServer(target,target_port):
		#ip_list=getAllAddresses()
		#for this_ip_addr in ip_list:
			#print("ConnectionManager.connectToServer: try to connect: "+str(this_ip_addr))
			#skt=connectToServer(this_ip_addr,target_port)
			#if(not skt is None):
				#return skt
		#return None
		
	def getTitle(self):
		return self.book_title
		
	def getStatus(self):
		output="ConnectionManager for "+self.getTitle()+"\n"
		for node in self.nodes:
			output+="--\n"
			output+=node.getStatus()
		return output
		
	@staticmethod
	def getPacketFor(source_book_title,source_chapter_title,target_book_title,target_scope,command,package):
		import json
		source_book_title=str(source_book_title) #Book.getTitle()
		source_chapter_title=str(source_chapter_title) #Chapter.getTitle() or None
		target_book_title=str(target_book_title)
		target_scope=str(target_scope) #NodeManager, Book, Chapter - String
		command=str(command)
		json_dict={"source_book_title":source_book_title,
				   "source_chapter_title":source_chapter_title,
				   "target_book_title":target_book_title,
				   "target_scope":target_scope,
				   "command":command,
				   "package":package}
		json_packet=json.dumps(json_dict)
		return json_packet
		
	#@property
	#def is_alive(self): return self._is_alive

	#@is_alive.setter
	#def is_alive(self, value):
		#if(not value): self._is_alive = False
		#else: raise ValueError("Cannot configure is_alive to: "+str(value))

##can't use priority queue which requires the peek() method to return the same 
## output as pop() (when called sequentially), which is only guaranteed in a strict FIFO
## Would need some kind of locking mechanism on the queue to ensure peek()/pop() operate
## harmonously if a PriorityQueue is needed
#import queue
#import json
#from enum import Enum

#import util.Book
#import util.Chapter
#import util.NodeManager

#class ConnectionManager:
	##document how books are mapped between each other
	##[[MASTER,SLAVE],[MASTER,SLAVE]]
	#BOOK_MASTER_RELATIONSHIP=[
		#[Book.BOOK_TYPE.PROCTOR,Book.BOOK_TYPE.WALL],
		#[Book.BOOK_TYPE.WALL,Book.BOOK_TYPE.HELM]
		#]
	
	#def __init__(self,this_book_title):
		#self.incoming_queue=queue.Queue()
		##use BOOK_MASTER_RELATIONSHIP to configure Nodes
		#self.sockets=[]
		#client_list=[]
		#for relationship in BOOK_MASTER_RELATIONSHIP:
			#if(relationship[0].name==this_book_title): client_list.append(relationship[1].name)
		#if(len(client_list)>0):
			#self.sockets.append(NodeManager(self,

	#def clean(self):
		#pass
		
	#def dispose(self):
		#pass
		
	##called when nodes receive external input
	## used to store incoming messages until ready to be used by super()
	#def enqueue(self,message):
		##sanitize, ensure message is json format, has a source, target
		#try:
			#json_dict=json.loads(message)
		#except JSONDecodeError:
			#print("ConnectionManager.enqueue: External message received at socket could not be parsed as JSON: "+str(message))
		#key="None"
		#try:
			#for key in ["source_book_title","source_chapter_title","target_scope","target_title","command","package"]:
				#value=json_dict[key] #attempt to fetch value for a key, and if key is not present, throw an error
		#except KeyError:
			#raise ValueError("ConnectionManager.enqueue: Unable to find key '"+str(key)+"' in incoming JSON packet: "+str(json_dict))
		
	##call this method to send a message outbound from this PC
	## to either the master or slave sockets
	##source_book_title - ex "PROCTOR" String
	##source_chapter_title - ex None if command comes from Book, or "Hyperspace" String
	##target_book_title - ex "HELM" String
	##target_scope - ex "Book" or "Chapter" String
	##target_title - ex "Map"
	##command - ex "set_player_position" String
	##packet - ex dictionary {"branch":[10,20],"fractional":0.2}
	#def send(self,source_book_title,source_chapter_title,target_book_title,target_scope,target_title,command,package):
		#source_book_title=str(source_book_title) #Book.getTitle()
		#source_chapter_title=str(source_chapter_title) #Chapter.getTitle() or None
		#target_book_title=str(target_book_title)
		#target_scope=str(target_scope)
		#target_name=str(target_name)
		#command=str(command)
		#json_dict={"source_book_title":source_book_title,
				   #"source_chapter_title":source_chapter_title,
				   #"target_book_title":target_book_title,
				   #"target_scope":target_scope,
				   #"target_name":target_name,
				   #"command":command,
				   #"package":package}
		#json_packet=json.dumps(json_dict)
		#node_manager=self.getNodeFor(source_book_title,target_book_title)
		#if(node_manager is None):
			#raise ValueError("ConnectionManager.send: Attempted to send packet to non-existant NodeManager for books source: "+source_book_title+", target: "+target_book_title+", packet: "+str(json_dict))
		#return node_manager.send(json_packet)
	
	##evaluate whether a connection exists and is ready to exchange packets
	#def isReady(self,source_book_title,target_book_title):
		#node_manager=self.getNodeManagerFor(source_book_title,target_book_title)
		#if(node_manager is None): return False
		#return node_manager.isReady(source_book_title,target_book_title)
	
	##returns the NodeManager for a given book relationship
	## if no NM exists, reteurn None
	##note that for server NMs, the client may or may not exist
	## the client status needs to be independently checked with isReady()
	#def getNodeManagerFor(self,source_book_title,target_book_title):
		#is_to_master=self.is_to_master(source_book_title,target_book_title)
		#for node_manager in self.sockets:
			#if(source_book_title==node_manager.getSourceBookTitle()
				#and (node_manager.is_server or target_book_title=node_manager.getTargetBookTitle())):
				#return node_manager
		#return None
	
	##evaluate whether one book is the master to another
	#def is_to_master(self,source_book_title,target_book_title):
		#for relationship in ConnectionManager.BOOK_MASTER_RELATIONSHIP:
			#master_book=relationship[0].name
			#slave_book=relationship[1].name
			#if(master_book==source_book_title and slave_book==target_book_title):
				#return True
			#if(slave_book==source_book_title and master_book==target_book_title):
				#return False
		#raise ValueError("ConnectionManager.__is_to_master: Unable to determine relationship of source to target books: "+str(source_book_title)+", "+str(target_book_title))
		
	##inspect the latest message in the queue for the given taget (Book or Chapter)
	#def peek(self,target):
		#if(not self.is_alive): return None #if closed, return no object
		#peek=incoming_queue.queue[0]
		#if(isinstance(target,Book)):
			#pass
		#elif(isinstance(target,Chapter)):
			#pass
		#else:
			#raise ValueError("Invalid target specified to fetch queued messages for (type: "+str(type(target))+"): "+str(target))
		
	##pull the latest message off the top of the queue
	#def poll(self,target):
		#outbound=peek(target)
		#if(not outbound is None):
			#pass

if __name__ == "__main__":
	print("START")
	import sys
	import time
	is_debug=False
	args=sys.argv
	cm=ConnectionManager(str(args[1]),is_debug)
	cm.start()
	#if(str(args[1])=="HELM"):
	#	time.sleep(10)
	#	cm.dispose()
	if(str(args[1])=="PROCTOR"):
		while(True):
			time.sleep(1)
			packet=cm.getPacketFor(
				source_book_title="PROCTOR",
				source_chapter_title=None,
				target_book_title="WALL",
				target_scope="Book",
				command="time",
				package=str(time.time()))
			print("CM.__main__: send packet: "+str(packet))
			cm.send(packet)
	if(str(args[1])=="WALL"):
		while(True):
			time.sleep(5)
			while(True):
				inbound_packet=cm.pop("Book")
				if(inbound_packet is None): break
				print("CM.__main__: received command: "+str(inbound_packet["command"])+", package: "+str(inbound_packet["package"]))
	print("DONE")
	
	
