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
This class contains the information about the hyperspace map.  This includes:
- Position of nodes
- Node type
- How nodes are connected
- How asteroids, rings, and obstacles are located throughout the map, including their current orietation with time
- Player position

Usage:
The Wall console contains a MASTER copy of this object.
At the start of te Hyperspace Chapter, the Wall seriealizes the map, sends it
to the SLAVE Helm console.  The Wall then updates the state of the map and forwards
these updates to the Helm

"""

#supporting libraries
from enum import Enum
import json

class HYPERSPACE_SERIAL_TYPE(Enum):
	MAP_CONNECTIONS=1
	NODE_TYPE=2
	NODE_RELATIONSHIP=3
	

class HyperspaceState:
	#JSON keys
	SERIAL_TYPE_KEY='serial_type'
	
	#file loctions
	
	def __init__(self):
		self.player_position_map=(0,0,0) #... X path, Y ratio through it
		self.player_position_screen=(0,0,0) #position on screen
		self.player_attitude=(0,0,0) #angle...?
		
		self.camera_position=(0,0,0)
		self.camera_attitude=(0,0,0)
		
	"""
	fetch contents of a csv file, expresses as json and returns
	"""
	def file_load(self,serial_type,filename):
		struct={}
		struct[self.SERIAL_TYPE_KEY]=serial_type.value
		if(serial_type==HYPERSPACE_SERIAL_TYPE.MAP_CONNECTIONS):
			pass
		elif():
			pass
		return json.dumps(struct)
	
	"""
	produce a string that can be sent between the wall and the helm computers
	representing the map and player state
	json...
	"""
	def serialize(self,serial_type):
		pass

	"""
	given a data stream, deseialize contents into the current object.
	To probe the contents of the data stream only,
	initialize a new class instance and deserialize into that, then
	use accessor methods
	"""
	def deserialize(self,data_stream):
		pass
