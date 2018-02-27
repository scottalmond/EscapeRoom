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
Class to sever as either a server or client to external actors
messages from send() are sent outbound immediately
messages inbound are queued in a FIFO and are accessible via peek() and pop()

Usage:

"""

from enum import Enum
import threading
import util.Chpater
import queue

class NODE_DIRECTION(Enum):
	CLIENT=0
	SERVER=1

class NODE_TYPE(Enum):
	PROCTOR={"port":7070}
	WALL={"port":6060}
	HELM={"port":5050}

class NodeManager(threading.Thread)):
	def __init__(self,node_direction,node_type):
		threading.Thread.__init__(self)
		if(node_direction==NODE_DIRECTION.CLIENT):
			self.is_server=True
		elif(node_direction==NODE_DIRECTION.SERVER):
			self.is_server=False
		else:
			raise ValueError("NodeManager: Invalid node direction specification: "+str(node_direction))
		self._is_alive=True
		self.queue=queue.Queue()
			
	#infinite loop looking for input from socket, enquing all that is found
	def run(self):
		while(self.is_alive):
			pass
			
	#call to close out open threads
	def dispose(self):
		self.is_alive=False
		
	#inspect the latest message in the queue for the given taget (Book or Chapter)
	def peek(self,target):
		if(not self.is_alive): return None #if closed, return no object
		if(isinstance(target,Book):
			pass
		elif(isinstance(target,Chapter):
			pass
		else:
			raise ValueError("Invalid target specified to fetch queued messages for (type: "+str(type(target))+"): "+str(target))
		
	#pull the latest message off the top of the queue
	def poll(self,target):
		outbound=peek(target)
		if(not outbound is None):
			pass
		
	#when input is received, add it to the queue
	def __enqueue(self,message):
		pass
		
	#given a message bound for a target, send it outbound out of this PC
	def send(self,message):
		pass

	@property
	def is_alive(self): return self._is_alive

	@is_alive.setter
	def is_alive(self, value):
		if(not value):
			self._is_alive = False
			#self.dispose() #need to allow natural shut down sequence order to run after life is terminated
		else:
			#only allow external actors to set is_alive to False to
			#avoid conflicting access/revival in multi-threaded environment
			raise ValueError("Cannot configure is_alive to: "+str(value))
