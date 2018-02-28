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
Class to serve as either a server or client to external actors
messages from send() are sent outbound from this PC immediately
inbound messages are queued in the ConnectionManager FIFO and are
accessible via peek() and pop() in that class

Usage:

"""

from enum import Enum
import threading
import util.Chpater

class NODE_DIRECTION(Enum):
	CLIENT=0
	SERVER=1

class NODE_TYPE(Enum):
	PROCTOR={"port":7070}
	WALL={"port":6060}
	HELM={"port":5050}

class NodeManager(threading.Thread)):
	#command_manager is where is_alive is polled from, and where queue is
	# maintained (server and client inputs are merged into a single queue)
	#node_type defines what port to present if acting as a server
	#node_direction specifies whether this node is a server or client
	def __init__(self,command_manager=None,node_type=NODE_TYPE.PROCTOR,is_server=True):
		threading.Thread.__init__(self)
		self._is_alive=True
		self.is_server=is_server
			
	#infinite loop looking for input from socket, enquing all that is found
	def run(self):
		while(self.is_alive):
			pass
			
	#call to close out open threads
	def dispose(self):
		self.is_alive=False
		
		
	#when input is received, add it to the queue
	def __enqueue(self,message):
		self.command_manager.enqueue(self,message)
		
	#given a message bound for a target, send it outbound out of this PC
	def send(self,message):
		pass

	@property
	def is_alive(self): return self._is_alive

	@is_alive.setter
	def is_alive(self, value):
		if(not value):
			self._is_alive = False
		else:
			#only allow external actors to set is_alive to False to
			#avoid conflicting access/revival in multi-threaded environment
			raise ValueError("Cannot configure is_alive to: "+str(value))
