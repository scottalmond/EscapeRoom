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
cd
python3 -m util.ConnectionManager WALL

in another terminal:
cd
python3 -m util.ConnectionManager PROCTOR

two nodes should automatically connect and exchange messages

"""

import threading
import queue
import json
import socket
import subprocess
from enum import Enum
import time

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
		
	SECONDS_BETWEEN_DEBUG_PRINT=4 #minimum number of seconds between debug printing in the run method
	RATE_LIMIT_SECONDS=0.1 #limit how often activity is queried over TCP connection
	
	#if is_enabled is False, then this class acts as a placeholder, returning empty responses
	# if is_enabled is True, then this class performs intended duties
	# to connect computers
	def __init__(self,this_book_title,is_enabled=True,is_debug=False):
		threading.Thread.__init__(self)
		self._is_alive=True
		self._is_enabled=is_enabled
		self.is_debug=is_debug
		self.book_title=this_book_title
		self.nodes=[]
		self.inbound_queue=queue.Queue()
		server_nm=None
		self.last_run_print_seconds=0 #time of last print
		#create NodeManagers to represent the connections this PC has with
		# external actors
		for relationship in self.BOOK_MASTER_RELATIONSHIP:
			if(relationship[0]==self.book_title):
				if(server_nm is None):
					server_nm=NodeManager(self,relationship[0],relationship[1],True,is_enabled,is_debug)
					self.nodes.append(server_nm)
				else:
					server_nm.appendTarget(relationship[1])
			elif(relationship[1]==self.book_title):
				client_nm=NodeManager(self,relationship[1],relationship[0],False,is_enabled,is_debug)
				self.nodes.append(client_nm)
		if(self.__isPrintEnabled()): print("ConnectionManager.init: number of NMs: "+str(len(self.nodes)))
		for node in self.nodes:
			node.start() #kick off threads that will seek connections and listen to input
		
	def __isPrintEnabled(self):
		return self.is_debug and self._is_enabled
		
	def clean(self):
		pass
		
	def dispose(self):
		if(self.__isPrintEnabled()): print("ConnectionManager.dispose()")
		self._is_alive=False #it appears threads also have an is_alive bool and there is a conflict, so set _is_alive directly
		for node in self.nodes:
			node.dispose()
			node.join()
		
	def run(self):
		if(self.__isPrintEnabled()): print("ConnectionManager.run: enter method")
		while(self._is_alive):
			if(self.RATE_LIMIT_SECONDS>0): time.sleep(self.RATE_LIMIT_SECONDS)
			run_print_enabled=time.time()-self.SECONDS_BETWEEN_DEBUG_PRINT>self.last_run_print_seconds
			if(run_print_enabled):
				self.last_run_print_seconds=time.time()
			if(not self._is_enabled):
				time.sleep(0.1)
			else:
				if(run_print_enabled and self.__isPrintEnabled()): print("CM -- "+str(time.time()))
				if(run_print_enabled and self.__isPrintEnabled()): print(self.getStatus())
				if(not self.isReady()):
					if(run_print_enabled and self.__isPrintEnabled()): print("ConnectionManager.run: Attempt to (re-)connect nodes...")
				for node in self.nodes:
					node.connect()
					#call in an infinite loop to reestablish any dropped connections
	
	#external PC sends package to this PC
	#package is a dictinary
	def receive(self,package):
		if(self.__isPrintEnabled()): print("ConnectionManager.receive: "+str(package))
		self.inbound_queue.put(package)
		
	#scope is a string like "Book" or "Chapter" (class name)
	# or even "NodeManager", but these packets are wiped away before
	# getting up to this level
	# case sensitive
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
	#packet is a json.dumps String
	def send(self,packet):
		#TODO: attempt to send to all node managers, only relevant node manager will comply
		for node in self.nodes:
			is_success=node.send(packet)
			if(is_success): return True
		return False
		
	#query whether the link to a particular book has been established
	# assumes each PC has a unique name and only exists once as either a server or client, not both
	#if target_book_title is None, then check the status of all books together
	# etiehr they are all ready (True) or one or more is not (False)
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

if __name__ == "__main__":
	print("START")
	import sys
	import time
	args=sys.argv
	is_debug=False
	if("DEBUG" in args):
		is_debug=True
	cm=ConnectionManager(str(args[1]),is_enabled=True,is_debug=is_debug)
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
	
	
