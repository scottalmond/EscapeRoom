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
This method listens for commands from the Proctor or Wall computers on
the TCP port and then updates the Book accordingly

Usage:

"""

class ConnectionManager:
	def __init__(self,this_book):
		pass

	def clean(self):
		pass
		
	def dispose(self):
		pass

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
