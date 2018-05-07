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
This class manages the configuration file IO about the hyperspace map
and regular data access to this info.  This includes:
- Position of nodes
- Node type
- How nodes are connected
- How asteroids, rings, and obstacles are located throughout the map
- Player position
- debris definition
- ring definition

Usage:
The Wall console contains a MASTER copy of this object.
At the start of te Hyperspace Chapter, the Wall seriealizes the map, send it
to the SLAVE Helm console.  The Wall then updates the state of the map and forwards
these updates to the Helm

python3 -m chapters.wall.hyperspace_helper.Maze

File types:
  node_definition
    defines how nodes are conceptually inter-related: branching, jumps, dead ends, start, finish
    is effectively the core of the maze definition
  branch_definition
	defines how the straight segments defiend in node_definition are inter-related
  subway_definition
    defines how nodes are represented on a 2D screen (support for 2D graphic rendering)
  segment_definition
    defines a list of ring-debris relationships for each segment (support for 3D grphi rendering)
  debris_definition
    defines one rings' worth of debris (quick-reference dictionary for segment_definition)

File columns:
	node_definition
		node_id_prev, node_id_next, segments
			note: segments is a spare-separate list of numbers from segment_definition
			precon: each segment_id only appears once ever in the config file
			precon: the first node-node relationship in the file is the start of the maze
			precon: branches only have one segment (otherwise state machine would lose sense of direction in maze)
	branch_definition
		node_id_prev, node_id_curr, node_id_next, is_two_way
			note: is_two_way is a boolean: 'TRUE' or 'FALSE'
				used as a flag to allow/deny the player from going back down
				a path in the backward direction.  If false, then only the forward
				direction (as listed in teh config file) is permitted/accessible
	subway_definition
		node_id_curr, node_id_next, direction, distance_pixels, x_pixels, y_pixels, type
			note: direction is compass rose style string: NW, SE, N
			note: distance_pixels is used by default as measured in 'direction' from 'node_id_curr'
				however if x_pixels and y_pixels are specified, the node_id_curr
				is placed precisely at this location on the screen
			note: type is one of the following strings: default, jump2, land3, dead, start, end
				where jump2 and land3 can have any numeric after them
				where default 
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
			precon: if segment_id are used in 'node_definition' where
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

class MAZE_CONFIG(Enum):
	NODE_DEFINITION={"filename":"node_definition.csv"}
	BRANCH_DEFINITION={"filename":"branch_definition.csv"}
	SUBWAY_DEFINITION={"filename":"subway_definition.csv"}
	SEGMENT_DEFINITION={"filename":"segment_definition.csv"}
	DEBRIS_DEFINITION={"filename":"debris_definition.csv"}

class Maze:
	CONFIG_FILE_PATH='./chapters/wall/assets/hyperspace/configuration/'
	
	def __init__(self):
		from RingAssembly import * #to fetch constants for ring/debris rotation rate
		
	def clean(self):
		self.node_definition=self.__load(self.NODE_DEFINITION)
		self.branch_definition=self.__load(self.BRANCH_DEFINITION)
		self.subway_definition=self.__load(self.SUBWAY_DEFINITION)
		self.segment_definition=self.__load(self.SEGMENT_DEFINITION)
		self.debris_definition=self.__load(self.DEBRIS_DEFINITION)
		
	#returns a list of dictionaries
	# except for DEBRIS_DEFINITION which is a dictionary (by ring_assembly name)
	# of lists (of each debris group) of dictionaries (for each field
	# of a debris definition)
	def __load(self,maze_config):
		filename=maze_config.value["filename"]
		file_contents=ResourceManager.loadCSV(filename)
		if(maze_config==self.DEBRIS_DEFINITION):
			output={}
		else:
			output=[]
		previous_row=[]
		previous_row_name=''
		for file_row_id in range(len(file_contents)):
			file_row=file_contents[file_row_id]
			if(maze_config==self.NODE_DEFINITION):
				file_row["node_id_prev"]=int(file_row["node_id_prev"])
				file_row["node_id_next"]=int(file_row["node_id_next"])
				segment_list=file_row["segments"].split()
				file_row["segments"]=[]
				for segment in segment_list: file_row["segments"].append(int(segment))
			elif(maze_config==self.BRANCH_DEFINITION):
				file_row["node_id_prev"]=int(file_row["node_id_prev"])
				file_row["node_id_curr"]=int(file_row["node_id_curr"])
				file_row["node_id_next"]=int(file_row["node_id_next"])
				is_two_way=False
				if(file_row["is_two_way"]==1 or file_row["is_two_way"]=='True' or
				   file_row["is_two_way"]=='TRUE'):
					is_two_way=True
				file_row["is_two_way"]=is_two_way
			elif(maze_config==self.SUBWAY_DEFINITION):
				pass
			elif(maze_config==self.SEGMENT_DEFINITION):
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
			elif(maze_config==self.DEBRIS_DEFINITION):
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

	#curr_segment_id can be <0 in order to fetch first segment only
	#prev_segment_id is ignored when outside a branch...? (TODO?)
	#return list of dictionaries:
	#[{"segment_id":X,"is_forward":True},{"segment_id":Y,"is_forward":False}]
	def getSegmentIdAfter(self,curr_segment_id,prev_segment_id):
		#sudo-code:
		#if segment_id<0 (ie, get starting segment)
		#  get the first segment from node_definition amd return that
		#look through node_definition for current segment_id
		#if is_forward, find the segment_id after the current segment_id
		#  in this node-node relationship segment_list
		#if NOT is_forward, find the segment_id BEFORE the current segment_id
		#if segment_list from this node-node relationship has been exhausted
		#then fetch the next/previous node-node relationship and
		#return the first/last segment from there
		#if node_type is end/dead --> return [] since there is no follower
		if(curr_segment_id<0):
			#first segment
			node_node_relationship=self.node_definition[0]
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
				return [{"segment_id":self.node_definition[0]["segments"][1],"is_forward":True}]
			#now get segment(s) after prev and curr node
			
			
	#return the populated Segment with RingAssemblies
	def getSegment(self,segment_id,is_forward):
		pass

	#get the node-node relationship, and the segment_list index, for a given segment_id
	#return dictionary {"node":node_definition[X],"segment_list_index":Y}
	#return None if not found
	def getSegment2Node(self,segment_id):
		for node_node_iter in self.node_definition:
			segment_list=node_node_iter["segments"]
			if(segment_id in segment_list):
				segment_index=segment_list.index(seg_id)
				return {"node":node_node_iter,"segment_list_index":segment_index}
		return None
		
