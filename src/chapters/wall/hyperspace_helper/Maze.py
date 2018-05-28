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
This class manages the configuration file IO of the hyperspace map
and regular data access to this info.  This includes:
- Subway Map (2D)
- Hyperspace Map (3D)
Layers:
- LINEAR_DEFINITION, what you will encounter between where-you-were and where-you-are, and how that will be represented in 2D/3D
- BRANCH_DEFINITION, where-you-were, where-you-are, where-you're-going relationship, if this relationship is reversable, and what where-you-are looks like
- SEGMENT_DEFINITION, refinement of what the 3D visuals looks like
- DEBRIS_DEFINITION, refinement of what the 3D visuals looks like

Structure:
The 2D/3D maps are inter-related.  They share "nodes" where transitions occur.  Several node relationships exist:
- corner, where one linear sequence comes in and one linear sequence leaves
  The 2D map shows a 45 degree bend, typically, here with one line coming in and one leaving
  The 3D visuals does make any clear indiciation a bend has occurred
  This distinction is useful for clearly visualizing progress of the pod through hyperspace on the 2D map as opposed to have one node-node relationship consist of multiple bends in the config file
- branch, where one linear sequence comes in and two leave
  The 2D map shows a circle where thee sequences exit
  The 3D visuals show a branching structure that the pod travels through
- jump/land, where a hyperspace jump starts/ends
  The 2D map shows the pod stopping at the "jump" node, only proceeding
  once the pod has reached the "land" node.  The jump has a perpendicular line
  The land has a perpendicular line plus a triangle pointing in the direction of travel
  The 3D visuals use a different ring type to indicate a hyperspace jump
- start, where the start of the map is
  The 2D map shows a square where only one sequence exits
  The 3D visuals play an intro sequence before the first life.
  On subsequnet lives, the player pod starts here, blinking briefly to indicate a new life
- dead, a dead end
  On the 2D map, an 'X' is displayed
  On the 3D visuals, a black hole of soome kind is displayed
- end, the goal of traversing the map
  In the 2D map, this is the same as "start"
  In the 3D visuals, something analagous to an "dead" is displayed, but in a different color (white)
  
Between each pair of nodes, one or more segments exist
- The 2D map only tracks the total process made between two nodes
- Each segment consists of a singular 3D circular arcing path.  To make
  a "back-and-forth" motion requires multiple segments back-to-back.  Each
  segment consists of some number of rings, which in turn each contain debris
  
python3 -m chapters.wall.hyperspace_helper.Maze

File types:
  linear_definition
    defines how nodes are conceptually inter-related: branching, jumps, dead ends, start, finish
    is effectively the core of the maze definition
    defines how nodes are represented on a 2D screen (support for 2D graphic rendering)
  branch_definition
	defines how the straight segments defiend in linear_definition are inter-related
  segment_definition
    defines a list of ring-debris relationships for each segment (support for 3D grphi rendering)
  debris_definition
    defines one rings' worth of debris (quick-reference dictionary for segment_definition)

File columns:
	linear_definition
		node_id_prev, node_id_next, segments, colors
			note: segments is a space-separated list of numbers from segment_definition
			precon: each segment_id only appears once ever in the config file
			precon: the first node-node relationship in the file is the start of the maze
			precon: branches only contain one segment (otherwise state machine would lose sense of direction in maze)
			note: colors is a space-separated list of paranthetical underscore numerical RGB triplets: "0_255_0 0_0_255"
			    would draw a green and blue line next to each other on the subway map
	branch_definition
		node_id_prev, node_id_curr, node_id_next, is_two_way, sprite, x_pixels, y_pixels
			note: sprite is one of the following strings: default, jump2, land3, dead, start, end, corner
				where jump2 and land3 can have any numeric after them
				where default 
			note: is_two_way is a boolean: 'TRUE' or 'FALSE'
				used as a flag to allow/deny the player from going back down
				a path in the backward direction.  If false, then only the forward
				direction (as listed in teh config file) is permitted/accessible
	segment_definition
		segment_id, type, curvature_degrees,  orientation_degrees,
		ring_model, ring_angle_degrees, ring_angle_rate_degrees_per_second, 
		debris_name, debris_angle_degrees, debris_angle_rate_degrees_per_second
			note: type can be one of the following strings: straight, dead, end
			note: ring_model is a filename pointing to an obj file in the asset folder
			note: debris_name can be 'None' string or a string to 'debris_definition'
			note: ring_angle_rate_degrees_per_second and debris_... can be the 
				string 'DEFAULT' to use the built-in default constant
			note: all positions/velocities are made to be True precisely
				when the pod passes through them.  Forward/backward propagation is
				used to compute the state before/after an encounter with the player
			precon: the last ring in a branch should be a double-ring .obj model
			precon: if segment_id are used in 'linear_definition' where
				node_id_prev==node_id_next then segment_type must be type 'branch'
	debris_definition
		debris_name, debris_model, radius, x_scale, y_scale, z_scale,
		x, y, z, x_degrees, y_degrees, z_degrees,
		x_degrees_per_second, y_degrees_per_second, z_degrees_per_second
			note: debris_name is a unique string used to identify the debris construction
				if the debris_name is blank, this row is combined with the previous row
				to create a composite debris definition
			note: scale will shrink/expand the CAD model
				by the stated ratio (1.0 default), leave blank to use default
			note: radius is a distance measurement in pi3d units to help with
				rendering the cross hairs on an asteroid that can be destroyed
			note: rows with a negative radius are ignored by the targeting algorithm
				(cannot eb targeted)
			note: radius is independent from scale
			note: x, y, and z are offset in pi3d distance units from the center of the ring
				x is left/right, y is up/down, z is forward/back (direction of travel)
			note: all positions/velocities are made to be True precisely
				when the pod passes through them.  Forward/backward propagation is
				used to compute the state before/after an encounter with the player
			precon: first row must have a name in the 'debris_name' field

"""

from enum import Enum

class MAZE_CONFIG(Enum):
	LINEAR_DEFINITION={"filename":"linear_definition.csv"}
	BRANCH_DEFINITION={"filename":"branch_definition.csv"}
	SEGMENT_DEFINITION={"filename":"segment_definition.csv"}
	DEBRIS_DEFINITION={"filename":"debris_definition.csv"}

class Maze:
	#CONFIG_FILE_PATH='./chapters/wall/assets/hyperspace/configuration/'
	CONFIG_FILE_PATH='/home/pi/Documents/EscapeRoom/src/chapters/wall/assets/hyperspace/configuration/'
	
	def __init__(self):
		from RingAssembly import RingAssembly #to fetch constants for ring/debris rotation rate
		from ResourceManager import ResourceManager
		self.rm=ResourceManager
		self.ra=RingAssembly
		
	def clean(self):
		self.linear_definition=self.__load(MAZE_CONFIG.LINEAR_DEFINITION)
		self.branch_definition=self.__load(MAZE_CONFIG.BRANCH_DEFINITION)
		self.segment_definition=self.__load(MAZE_CONFIG.SEGMENT_DEFINITION)
		self.debris_definition=self.__load(MAZE_CONFIG.DEBRIS_DEFINITION)
		
	#returns a list of dictionaries
	# except for DEBRIS_DEFINITION which is a dictionary (by ring_assembly name)
	# of lists (of each debris group) of dictionaries (for each field
	# of a debris definition)
	def __load(self,maze_config):
		filename=maze_config.value["filename"]
		file_contents=self.rm.loadCSV(self.CONFIG_FILE_PATH+filename)
		if(maze_config==MAZE_CONFIG.DEBRIS_DEFINITION):
			output={}
		else:
			output=[]
		previous_row=[]
		previous_row_name=''
		for file_row_id in range(len(file_contents)):
			file_row=file_contents[file_row_id]
			if(maze_config==MAZE_CONFIG.LINEAR_DEFINITION):
				file_row["node_id_prev"]=int(file_row["node_id_prev"])
				file_row["node_id_next"]=int(file_row["node_id_next"])
				segment_list=file_row["segments"].split()
				file_row["segments"]=[]
				for segment in segment_list: file_row["segments"].append(int(segment))
				output.append(file_row)
				color_list=file_row["colors"].split()
				file_row["colors"]=[]
				for color_str in color_list:
					this_color=color_str.split('_')
					if(len(this_color) != 3):
						raise NotImplementedError('Maze.__load: unknown color format specified in LINEAR_DEFINITION: ',this_color)
					for idx in range(3):
						this_color[idx]=int(this_color[idx])
					file_row["colors"].append(this_color)
			elif(maze_config==MAZE_CONFIG.BRANCH_DEFINITION):
				file_row["node_id_prev"]=int(file_row["node_id_prev"])
				file_row["node_id_curr"]=int(file_row["node_id_curr"])
				file_row["node_id_next"]=int(file_row["node_id_next"])
				is_two_way=False
				if(file_row["is_two_way"]==1 or file_row["is_two_way"]=='True' or
				   file_row["is_two_way"]=='TRUE'):
					is_two_way=True
				file_row["is_two_way"]=is_two_way
			elif(maze_config==MAZE_CONFIG.SEGMENT_DEFINITION):
				file_row["segment_id"]=int(file_row["segment_id"])
				if(not file_row["type"] in ["straight","dead","end"]):
					raise NotImplementedError('Maze.__load: unknown segment type in SEGMENT_DEFINITION: ',file_row["type"])
				for deg in ["curvature","orientation","ring_angle","debris_angle"]:
					file_row[deg+"_degrees"]=file_row[deg+"_degrees"].trim()
					if(len(file_row[deg+"_degrees"])<=0):
						file_row[deg+"_degrees"]=0.0
					else:
						file_row[deg+"_degrees"]=float(file_row[deg+"_degrees"])
				if(len(file_row["ring_angle_degrees_per_second"].trim())<=0):
					file_row["ring_angle_degrees_per_second"]=RingAssembly.RING_ROTATION_DEGREES_PER_SECOND
				else:
					file_row["ring_angle_degrees_per_second"]=float(file_row["ring_angle_degrees_per_second"])
				if(len(file_row["debris_angle_degrees_per_second"].trim())<=0):
					file_row["debris_angle_degrees_per_second"]=RingAssembly.DEBRIS_ROTATION_DEGREES_PER_SECOND
				else:
					file_row["debris_angle_degrees_per_second"]=float(file_row["debris_angle_degrees_per_second"])
			elif(maze_config==MAZE_CONFIG.DEBRIS_DEFINITION):
				file_row["debris_name"]=file_row["debris_name"].strip()
				if(len(file_row["debris_name"])<=0):
					this_row_name=previous_row_name
				file_row["radius"]=int(file_row["radius"])
				for var in ["","_scale","_degrees","_degrees_per_second"]:
					for dim in ["x","y","z"]:
						file_row[dim+var]=file_row[dim+var].trim()
						if(len(file_row[dim+var])<=0): #defaults
							if(var==""): #0 pos
								file_row[dim+var]=0.0
							elif(var=="_scale"): #1x scale
								file_row[dim+var]=1.0
							elif(var=="_degrees"): #0 deg
								file_row[dim+var]=0.0
							elif(var=="_degrees_per_second"):
								file_row[dim+var]=0.0 #0 deg/sec
						else:
							file_row[dim+var]=float(file_row[dim+var])
				if(not this_row_name in output):
					output[this_row_name]=[]
				output[this_row_name].append(file_row)
				previous_row_name=this_row_name
			else:
				raise NotImplementedError('Maze.__load: Unable to load config file type: ',maze_config)
		return output
		
	#TODO
	#curr_segment_id
	#prev_segment_id
	#return list of dictionaries:
	#[{"segment_id":X,"is_forward":True},{"segment_id":Y,"is_forward":False}]
	def getSegmentIdAfter(self,curr_segment_id,prev_segment_id):
		#sudo-code:
		#if segment_id<0 (ie, get starting segment)
		#  get the first segment from linear_definition amd return that
		#look through linear_definition for current segment_id
		#if is_forward, find the segment_id after the current segment_id
		#  in this node-node relationship segment_list
		#if NOT is_forward, find the segment_id BEFORE the current segment_id
		#if segment_list from this node-node relationship has been exhausted
		#then fetch the next/previous node-node relationship and
		#return the first/last segment from there
		#if node_type is end/dead --> return [] since there is no follower
		if(curr_segment_id<0):
			#first segment
			node_node_relationship=self.linear_definition[0]
			return [{"segment_id":node_node_relationship["segments"][0],"is_forward":True}]
		else:
			#first find the node-node relationship where this segment came from
			#then determine either 1) the neighboring segment from the segment_list
			#or the neighboring node-node relationship and the segment from *that* segment_list
			curr_node=self.getSegment2Node(curr_segment_id)
			prev_node=self.getSegment2Node(prev_segment_id)
			if(curr_node is None):
				ValueError("Maze.getSegmentIdAfter: Unable to fetch the node-node relationship for segment: ",curr_segment_id)
			if(prev_node is None): #should only occur if prev_segment_id is invalid, ie when traversing from the first to the second segment in the maze
				return [{"segment_id":self.linear_definition[0]["segments"][1],"is_forward":True}]
			#now get segment(s) after prev and curr node
			
		
	#given two (precon: sequential) nodes (OR same node to find branch segment(s)), find the segment list
	#segment list will always be in order from prev_node to curr_node
	#returns {"is_forward":True/False,"segments":[segment_id,segment_id,segment_id]}
	#note: method will blindly return segments even if they are not accessible in the stated order (ex. branch_definition is_two_way=False)
	def getSegmentsBetweenNodes(self,prev_node,next_node):
		for row in self.linear_definition:
			this_prev=row["node_id_prev"]
			this_next=row["node_id_next"]
			this_segments=row["segments"]
			hit=False
			is_forward=True
			if(this_prev==prev_node and this_next == next_node):
				hit=True
			elif(this_next==prev_node and this_prev==next_node):
				hit=True
				is_forward=False
				this_segments=list(reversed(this_segments))
			if(hit):
				return {"is_forward":is_forward,"node_id_prev":this_prev,"node_id_next":this_next,"segments":this_segments}
		return None
			
	#return the populated Segment with RingAssemblies
	#  TODO: only use/load RingAssemblies if in Hyperspace.py ...
	def getSegment(self,segment_id,is_forward):
		pass

	#TODO: deletable...
	#get the node-node relationship, and the segment_list index, for a given segment_id
	#return dictionary {"node":linear_definition[X],"segment_list_index":Y}
	#return None if not found
	def getSegment2Node(self,segment_id):
		for node_node_iter in self.linear_definition:
			segment_list=node_node_iter["segments"]
			if(segment_id in segment_list):
				segment_index=segment_list.index(seg_id)
				return {"node":node_node_iter,"segment_list_index":segment_index}
		return None
		
if __name__ == "__main__":
	import sys
	sys.path.append('/home/pi/Documents/EscapeRoom/src/util')
	#from ResourceManager import *
	#csv=ResourceManager.loadCSV(Maze.CONFIG_FILE_PATH+MAZE_CONFIG.LINEAR_DEFINITION.value["filename"])
	#print(csv)
	maze=Maze()
	maze.clean()
	print(maze.getSegmentsBetweenNodes(100,91))
	print(maze.getSegmentsBetweenNodes(91,100))
	print(maze.getSegmentsBetweenNodes(91,91))
