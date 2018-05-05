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
At the start of te Hyperspace Chapter, the Wall seriealizes the map, send it
to the SLAVE Helm console.  The Wall then updates the state of the map and forwards
these updates to the Helm

python3 -m chapters.wall.hyperspace_helper.Maze

"""

#supporting libraries
from enum import Enum
import json #for serializable objects

#util
from util.ResourceManager import ResourceManager

class MAZE_FILE_TYPE(Enum):
	MAP_CONNECTIONS="map_connections" #how the PC represents the nodes - as a series of prev-current-next relationships
	NODE_TYPE="node_type" #dead-end, branch, elbow, etc
	NODE_RELATIONSHIP="node_relationship" #how nodes are drawn on screen repective to each other

class Maze:
	#note, it is uncler which way the screen will be installed
	#allow for post-installation rotation as a parameter
	IS_SCREEN_ROTATED_180=False
	#also, screen resolution is 1680x1050, 60Hz
	
	#generic JSON keys
	SERIAL_TYPE_KEY="serial_type"
	SERIAL_PACKAGE_KEY="package"
	
	#file locations
	#details how to travel through branches: where two file rows have equal _in_ and _node_ values, but different _out_
	#dead ends are nodes that have no subsequent connections
	#elbows are nodes that only have one _in_ and one _out_ for a _node_
	#columns:
	#In - the node that the player is traveling from
	#Node - the node the player is traveling through, such as where a decision to right or left is made
	#Out - one node the player can chose to go toward (if traveling over a branch)
	#Two-way - if FALSE, then this sequence of nodes is only accessible in the direction stated
	#  if TRUE, then the player can also travel down a Out-Node-In path
	MAP_CONNECTIONS_FILE_PATH='./chapters/wall/assets/hyperspace/configuration_map_connections.csv'
	#file column titles (and constants used throughout execution)
	MAP_CONN_IN_KEY="In"
	MAP_CONN_NODE_KEY="Node"
	MAP_CONN_OUT_KEY="Out"
	MAP_CONN_TWO_WAY="Two-way"
	
	#details how nodes are positioned relative to one another
	#all connections will be illustrated with a line draw on-screen
	#suppy a X and Y position to override the relative position 
	# ex. to position islands not connected to the rest of the map
	#X and Y define center of node
	#where X and Y are measured from the top-left of the screen
	NODE_TYPE_FILE_PATH='./chapters/wall/assets/configuration_map_node_type.csv'
	
	NODE_TYPE_START_KEY="This Node"
	NODE_TYPE_END_KEY="Next Node"
	NODE_TYPE_DIRECTION_KEY="Direction"
	NODE_TYPE_DISTANCE_PX="Distance (pixels)"
	NODE_TYPE_X_PX="Node X (pixels)"
	NODE_TYPE_Y_PX="Node Y (pixels)"
	
	#columns:
	NODE_RELATIONSHIP_FILE_PATH='./chapters/wall/assets/configuration_map_node_relationship.csv'
	
	def __init__(self):
		#self.player_position_map=(0,0,0) #... X path, Y ratio through it
		#self.player_position_screen=(0,0,0) #position on screen
		#self.player_attitude=(0,0,0) #angle...?
		
		#self.camera_position=(0,0,0)
		#self.camera_attitude=(0,0,0)
		
		#each varialbe is a list of dictionaries
		#supplied by MASTER through file_load or deserialize()
		self.map_connections=None
		self.node_type=None
		self.node_relationship=None
		
	"""
	fetch contents of a csv file, expresses as dictionary and returns
	"""
	def file_load(self,serial_type,filename):
		struct={}
		struct[self.SERIAL_TYPE_KEY]=serial_type.value
		file_contents=ResourceManager.loadCSV(filename)
		#print(file_contents)
		if(serial_type==MAZE_FILE_TYPE.MAP_CONNECTIONS):
			map_connections=[]
			for row in file_contents:
				new_row={self.MAP_CONN_IN_KEY:row[self.MAP_CONN_IN_KEY],
						 self.MAP_CONN_NODE_KEY:row[self.MAP_CONN_NODE_KEY],
						 self.MAP_CONN_OUT_KEY:row[self.MAP_CONN_OUT_KEY]}
				map_connections.append(new_row)
				if(row[self.MAP_CONN_TWO_WAY]=="TRUE"):
					reverse_row={self.MAP_CONN_IN_KEY:row[self.MAP_CONN_OUT_KEY],
								 self.MAP_CONN_NODE_KEY:row[self.MAP_CONN_NODE_KEY],
								 self.MAP_CONN_OUT_KEY:row[self.MAP_CONN_IN_KEY]}
					map_connections.append(reverse_row)
			struct[self.SERIAL_PACKAGE_KEY]=map_connections
			#print(len(map_connections))
		elif(serial_type==MAZE_FILE_TYPE.NODE_TYPE):
			for row in file_contents:
				pass
		elif(serial_type==MAZE_FILE_TYPE.NODE_RELATIONSHIP):
			for row in file_contents:
				print(row)
		return struct#json.dumps(struct)
	
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
	def deserialize(self,json_string):
		json_dict=json.loads(json_string)
		if(not SERIAL_TYPE_KEY in json_dict):
			raise ValueError("Key not found in de-serial data stream '"+str(SERIAL_TYPE_KEY)+"': "+str(json_string))
		serial_type=str(json_dict[SERIAL_TYPE_KEY])
		package=None
		if(SERIAL_PACKAGE_KEY in json_dict):
			package=json_dict[SERIAL_PACKAGE_KEY]
		if(serial_type==HYPERSPACE_SERIAL_TYPE.MAP_CONNECTIONS.value):
			#check if package exists, and that it is formatted correctly
			#if good, save to live state
			if(package is None or not type(package)==type([])): raise ValueError("Invalid package specified in de-serialization packet of type "+str(serial_type)+": "+str(json_string))
			for row in package:
				if(not all(x in row for x in [self.MAP_CONN_IN_KEY,self.MAP_CONN_NODE_KEY,self.MAP_CONN_OUT_KEY])):
					raise ValueError("Missing de-serialization parameters from package of type "+str(serial_type)+": "+str(row))
			self.map_connections=package
		elif(serial_type==HYPERSPACE_SERIAL_TYPE.NODE_TYPE.value):
			if(package is None or not type(package)==type([])): raise ValueError("Invalid package specified in de-serialization packet of type "+str(serial_type)+": "+str(json_string))
			
		elif(serial_type==HYPERSPACE_SERIAL_TYPE.NODE_RELATIONSHIP.value):
			if(package is None or not type(package)==type([])): raise ValueError("Invalid package specified in de-serialization packet of type "+str(serial_type)+": "+str(json_string))
		else:
			raise ValueError("Invalid de-serialization type sepcified: "+str(json_dict[SERIAL_TYPE_KEY])+", from: "+str(json_string))

	#evaluate whether maze state has been loaded from disk or over TCP
	def isLoaded(self):
		return (not self.map_connections is None and
			    not self.node_type is None and 
			    not self.node_relationship is None)

	#draw Helm contents of maze state object
	def drawBackground(self,rm):
		#for every node in 
		if(not self.isLoaded()): return False #skip drawing if no content available
		
		

#cd /Documents/EscapeRoom/src/
#python3 -m chapters.wall.hyperspace_helper.HyperspaceState
if __name__ == "__main__":
	hs=Maze()
	out=hs.file_load(MAZE_FILE_TYPE.MAP_CONNECTIONS,Maze.MAP_CONNECTIONS_FILE_PATH)
	print(out)
	
