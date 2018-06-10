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
			note: sprite is one of the following strings: start, end, corner, branch, dead, jump2, land3
				where jump2 and land3 can have any numeric after them
				where default 
			note: is_two_way is a boolean: 'TRUE' or 'FALSE'
				used as a flag to allow/deny the player from going back down
				a path in the backward direction.  If false, then only the forward
				direction (as listed in teh config file) is permitted/accessible
	segment_definition
		segment_id, type, curvature_degrees,  orientation_degrees,
		ring_model, ring_angle_degrees, ring_angle_degrees_per_second, 
		debris_name, debris_angle_degrees, debris_angle_degrees_per_second
			note: type can be one of the following strings: straight, dead, end
			note: ring_model is an int index per AssetLibrary.ring_filename
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
			note: debris_model is an int index from AssetLibrary.asteroid_filename
			note: scale will shrink/expand the CAD model
				by the stated ratio (1.0 default), leave blank to use default
			note: radius is a distance measurement in pi3d units to help with
				rendering the cross hairs on an asteroid that can be destroyed
			note: rows with a negative radius are ignored by the targeting algorithm
				(cannot eb targeted)
			note: radius is updated (scaled) automatically in RingAssembly.addDebris
				if xyz_scale are non-unity
			note: x, y, and z are offset in pi3d distance units from the center of the ring
				x is left/right, y is up/down, z is forward/back (direction of travel)
			note: all positions/velocities are made to be True precisely
				when the pod passes through them.  Forward/backward propagation is
				used to compute the state before/after an encounter with the player
			precon: first row must have a name in the 'debris_name' field

"""

from enum import Enum
import copy #deepcopy

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
		self.__verify_linear_and_branch_consistency()
		self.__verify_segment_definition()
		self.__verify_debris_definition()
		self.__merge_debris_into_segment_definition()
		
	#ensure that every ring pair in linear_definition is mated up with at least one branch in branch_definition and vice versa
	def __verify_linear_and_branch_consistency(self):
		#TODO: sanity check to make sure no definitions are missing...
		#  ex: nodes used in linear_definition/brach_definition, but not used elsewhere, same with segments
		#  TODO: update segment_definition to directly reference debris_definition row contents... "ring_list" --> debris_list=[debris_name[], debris_name[] ... ]
		unique_node_id=[]
		for is_check in [False,True]: #check that all nodes are in agreement between linear_definition and branch_definition
			for definition in [self.linear_definition,self.branch_definition]:
				for row in definition:
					if(definition is self.linear_definition):
						node_list=[row["node_id_prev"],row["node_id_next"]]
						definition_string="linear_definition"
					else:
						node_list=[row["node_id_prev"],row["node_id_curr"],row["node_id_next"]]
						definition_string="branch_definition"
					for node_id in node_list:
						if(is_check):
							if(node_id>=0 and not node_id in unique_node_id):
								#raise ValueError("Maze.__verify_linear_and_branch_consistency: node_id: ",node_prev," not defined in ",definition_string," config file")
								print("Maze.__verify_linear_and_branch_consistency: node_id: ",node_prev," not defined in ",definition_string," config file")
						else:
							if(not node_id in unique_node_id): unique_node_id.append(node_id)
		return True
	
	#ensure every segment defined in linear_definition has a concrete definition in segment_definition
	def __verify_segment_definition(self):
		#check that all segments in linear_definition are defined
		for linear_row in self.linear_definition:
			for linear_segment_id in linear_row["segment_list"]:
				is_found=False
				for segment_definition in self.segment_definition:
					if(segment_definition["segment_id"]==linear_segment_id):
						is_found=True
						break
				if(not is_found):
					print("Maze.__verify_segment_definition: segment_id "+str(linear_segment_id)+" not defined in linear_definition config file")
					#raise ValueError("Maze.__verify_segment_definition: segment_id "+str(linear_segment_id)+" not defined in linear_definition config file")
		
	#ensure that for every string debris_name called in segment_definition that there is a corresponding debris_definition
	def __verify_debris_definition(self):
		for segment_row in self.segment_definition:
			for ring_row in segment_row["ring_list"]:
				if(self.__get_debris_definition_by_name(ring_row["debris_name"]) is None):
					#raise ValueError("Maze.__verify_debris_definition: debris_name "+str(segment_row["debris_name"])+" not defined in debris_definition config file")
					print("Maze.__verify_debris_definition: debris_name "+str(ring_row["debris_name"])+" not defined in debris_definition config file")
		
	#merge debris_definition into segment_definition to simplify later code lookups
	def __merge_debris_into_segment_definition(self):
		for segment_row in self.segment_definition:
			for ring_row in segment_row["ring_list"]:
				ring_row["debris_list"]=self.__get_debris_definition_by_name(ring_row["debris_name"])
		
	def __get_debris_definition_by_name(self,debris_name):
		if(debris_name in ["","None","NONE","Null","NULL"]):
			return []
		if(not debris_name in self.debris_definition):
			return None
		return self.debris_definition[debris_name]
		
	#load csv file
	#linear_definition = [ [prev,next], [prev,next], ... ]
	#branch_definition = [ [prev,curr,next], [prev,curr,next], ... ]
	#segment_definition = [ [id,[ring_assy, ring_assy, ...], [id,[ring_assy, ring_assy, ...], ...]
	#debris_definition = { name:[debris, debris, ...], name:[debris, debris, ...], ... }
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
				segment_list=file_row["segment_list"].split()
				file_row["segment_list"]=[]
				for segment in segment_list: file_row["segment_list"].append(int(segment))
				color_list=file_row["colors"].split()
				file_row["colors"]=[]
				for color_str in color_list:
					this_color=color_str.split('_')
					if(len(this_color) != 3):
						raise NotImplementedError('Maze.__load: unknown color format specified in LINEAR_DEFINITION: ',this_color)
					for idx in range(3):
						this_color[idx]=int(this_color[idx])
					file_row["colors"].append(this_color)
				output.append(file_row)
			elif(maze_config==MAZE_CONFIG.BRANCH_DEFINITION):
				file_row["node_id_prev"]=int(file_row["node_id_prev"])
				file_row["node_id_curr"]=int(file_row["node_id_curr"])
				file_row["node_id_next"]=int(file_row["node_id_next"])
				is_two_way=False
				if(file_row["is_two_way"]==1 or file_row["is_two_way"]=='True' or
				   file_row["is_two_way"]=='TRUE'):
					is_two_way=True
				file_row["is_two_way"]=is_two_way
				
				#TODO, handle jump/land sprite case
				
				output.append(file_row)
			elif(maze_config==MAZE_CONFIG.SEGMENT_DEFINITION):
				file_row["segment_id"]=int(file_row["segment_id"])
				for prev_row in output: #ease-of-use imeplementation: copy-paste first row contents into subsequent rows with same id number
					if(prev_row["segment_id"]==file_row["segment_id"]):
						file_row["type"]=prev_row["type"]
						file_row["curvature_degrees"]=str(prev_row["curvature_degrees"])
						file_row["orientation_degrees"]=str(prev_row["orientation_degrees"])
						break
				file_row["type"]=file_row["type"].strip()
				if(not file_row["type"] in ["straight","dead","end","branch"]): 
					raise NotImplementedError('Maze.__load: unknown segment type in SEGMENT_DEFINITION: ',file_row["type"])
				for deg in ["curvature","orientation","ring_angle","debris_angle"]:
					file_row[deg+"_degrees"]=file_row[deg+"_degrees"].strip()
					if(len(file_row[deg+"_degrees"])<=0): #if no string present, then populate default
						file_row[deg+"_degrees"]=0.0
					else:
						file_row[deg+"_degrees"]=float(file_row[deg+"_degrees"])
				if(len(file_row["ring_angle_degrees_per_second"].strip())<=0):
					file_row["ring_angle_degrees_per_second"]=RingAssembly.RING_ROTATION_DEGREES_PER_SECOND
				else:
					file_row["ring_angle_degrees_per_second"]=float(file_row["ring_angle_degrees_per_second"])
				if(len(file_row["debris_angle_degrees_per_second"].strip())<=0):
					file_row["debris_angle_degrees_per_second"]=RingAssembly.DEBRIS_ROTATION_DEGREES_PER_SECOND
				else:
					file_row["debris_angle_degrees_per_second"]=float(file_row["debris_angle_degrees_per_second"])
				segment_row={"segment_id":file_row["segment_id"],"type":file_row["type"],
				    "curvature_degrees":file_row["curvature_degrees"],
				    "orientation_degrees":file_row["orientation_degrees"],"ring_list":[]}
				is_new_segment=True
				for row in output:#find first row in output where this segment_id has laready been defined
					if(row["segment_id"]==file_row["segment_id"]):
						segment_row=row
						is_new_segment=False
						break
				ring_row={}
				ring_parameters=["ring_model","debris_name",
								 "ring_angle_degrees","ring_angle_degrees_per_second",
								 "debris_angle_degrees","debris_angle_degrees_per_second"]
				for parameter in ring_parameters:
					if(parameter=="debris_name"):
						ring_row[parameter]=file_row[parameter]
					elif(parameter=="ring_model"):
						ring_row[parameter]=int(file_row[parameter])
					else:
						ring_row[parameter]=float(file_row[parameter])
				segment_row["ring_list"].append(ring_row)
				if(is_new_segment):
					output.append(segment_row)
			elif(maze_config==MAZE_CONFIG.DEBRIS_DEFINITION):
				file_row["debris_name"]=file_row["debris_name"].strip()
				this_row_name=file_row["debris_name"]
				if(len(file_row["debris_name"])<=0):
					this_row_name=previous_row_name
				file_row["radius"]=int(file_row["radius"])
				for var in ["","_scale","_degrees","_degrees_per_second"]:
					for dim in ["x","y","z"]:
						file_row[dim+var]=file_row[dim+var].strip()
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
			
	#return Segment with RingAssemblies assembled/installed/added
	#  TODO: only use/load RingAssemblies if in Hyperspace.py ...
	#can't remember, is padding (space between rings) put BEFORE ring
	#  CAD model, or after ...? TODO
	#  It's after:  u=idx/len - so u goes from [0,1)
	def getPopulatedSegment(self,segment_id,is_forward,is_branch,asset_library,
		start_position,start_rotation_matrix,start_time_seconds):
		segment_definition=self.__getSegmentDefinition(segment_id)
		if(segment_definition is None):
			raise IndexError("Maze.getSegment: cannot find segment_definition for segment_id: ",segment_id)
		is_branch=segment_definition["sprite"]=="branch"
		curvature_degrees=segment_definition["curvature_degrees"]
		orientation_degrees=segment_definition["orientation_degrees"]
		ring_count=len(segment_definition["ring_list"])
		segment=Segment(asset_library,is_branch,start_position,start_rotation_matrix,
			start_time_seconds,curvature_degrees,orientation_degrees,ring_count,segment_id)
		ring_list=segment_definition["ring_list"]
		if(not is_forward): ring_list=list(reversed(ring_list))
		for ring_index in range(len(ring_list)):
			ring_definition=ring_list[ring_index]
			u=ring_index/len(ring_list)
			ring_index=ring_definition["ring_model"]
			ring_rotation_degrees=ring_definition["ring_angle_degrees"]
			ring_rotation_rate=ring_definition["ring_angle_degrees_per_second"]
			debris_rotation_degrees=ring_definition["debris_angle_degrees"]
			debris_rotation_rate=ring_definition["debris_angle_degrees_per_second"]
			ring_assembly=segment.addRingAssembly(self,asset_library,u,ring_index,
				ring_rotation_degrees,ring_rotation_rate,
				debris_rotation_degrees,debris_rotation_rate)
			debris_list=ring_definition["debris_list"]
			for debris_definition in debris_list:
				debris_model_index=debris_definition["debris_model"]
				location=[debris_definition["x"],debris_definition["y"],debris_definition["z"]]
				angle=[debris_definition["x_degrees"],debris_definition["y_degrees"],debris_definition["z_degrees"]]
				angular_velocity=[debris_definition["x_degrees_per_second"],
								  debris_definition["y_degrees_per_second"],
								  debris_definition["z_degrees_per_second"]]
				scale=[debris_definition["x_scale"],debris_definition["y_scale"],debris_definition["z_scale"]]
				radius=debris_definition["radius"]
				this_debris=ring_assembly.addDebris(debris_model_index,location,angle,angular_velocity,scale,radius)
		return segment
		
	#search through file for definition (curvature, orientation, etc)
	def __getSegmentDefinition(self,segment_id):
		for row in self.segment_definition:
			if(row["segment_id"]==segment_id):#match
				return copy.deepcopy(row) #should no longer need deepcopy since debris is now copied into segment_definition at start ratehr than after this method call
		return None

	#TODO
	#curr_segment_id
	#prev_segment_id
	#return list of dictionaries:
	#[{"segment_id":X,"is_forward":True},{"segment_id":Y,"is_forward":False}]
	def getSegmentIdAfter_legacy(self,curr_segment_id,prev_segment_id):
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
			return [{"segment_id":node_node_relationship["segment_list"][0],"is_forward":True}]
		else:
			#first find the node-node relationship where this segment came from
			#then determine either 1) the neighboring segment from the segment_list
			#or the neighboring node-node relationship and the segment from *that* segment_list
			curr_node=self.getSegment2Node(curr_segment_id)
			prev_node=self.getSegment2Node(prev_segment_id)
			if(curr_node is None):
				ValueError("Maze.getSegmentIdAfter: Unable to fetch the node-node relationship for segment: ",curr_segment_id)
			if(prev_node is None): #should only occur if prev_segment_id is invalid, ie when traversing from the first to the second segment in the maze
				return [{"segment_id":self.linear_definition[0]["segment_list"][1],"is_forward":True}]
			#now get segment(s) after prev and curr node
			
	#returns list of segment_id that come after the curr_segment, prev_segment sequence
	#returns {"segment_id":X,"is_forward":bool}
	def getSegmentIdAfter(self,prev_segment_id,curr_segment_id):
		#consider five cases:
		#  prev_nodes==curr_nodes
		#    is between two nodes
		#    then next segment lies either 1) between these nodes, 2) at the start/end of the next nodes
		#  else prev_nodes!=curr_nodes
		#    if curr_nodes is branch, 3) return two followers coming from prev_nodes direction
		#    
		lin_def_pair=self.getOrderedLinearDefinition(curr_segment_id,prev_segment_id)
		prev_lin_def=lin_def_pair["prev"]
		curr_lin_def=lin_def_pair["curr"]
		#print("Maze.next_node_list: prev_lin_def[node_id_prev]: ",prev_lin_def["node_id_prev"])
		#print("Maze.next_node_list: curr_lin_def[node_id_prev]: ",curr_lin_def["node_id_prev"])
		#print("Maze.next_node_list: curr_lin_def[node_id_next]: ",curr_lin_def["node_id_next"])
		next_node_list=self.getNodeIdAfter(prev_lin_def["node_id_prev"],curr_lin_def["node_id_prev"],curr_lin_def["node_id_next"])
		out_list=[]
		#print("Maze.next_node_list: next_node_list: ",next_node_list)
		#if(prev_lin_def["node_id_prev"]==curr_lin_def["node_id_prev"] and
		#   prev_lin_def["node_id_next"]==curr_lin_def["node_id_next"]): #then operating in the same node-node region
		if(curr_lin_def["segment_id_index"]==(curr_lin_def["segment_list_len"]-1)):#then at end of this node-node region
			for next_node_id in next_node_list: #get the first segment_id from the next node-node region
				segment_list=self.getSegmentsBetweenNodes(curr_lin_def["node_id_next"],next_node_id)
				#print("Maze.getSegmentIdAfter: segment_list: ",segment_list)
				out_list.append({"is_forward":segment_list["is_forward"],"segment_id":segment_list["segment_list"][0]}) #precon: len(segment_list)>0
		else:#fetch next from current node-node region
			segment_list=curr_lin_def["segment_list"]
			curr_segment_index=curr_lin_def["segment_id_index"]
			#print("Maze.getSegmentIdAfter: curr_segment_index",curr_segment_index)
			#print("Maze.getSegmentIdAfter: curr_segment_index",curr_segment_index)
			out_list.append({"is_forward":curr_lin_def["is_forward"],"segment_id":segment_list[curr_segment_index+1]}) #get segment_id after curr_segment_id in this node-node region
		#else:#prev_ and curr_segment_id straddle a node-node relationship
		#	if(curr_lin_def["segment_id_index"]==(curr_lin_def["segment_list_len"]-1)):
		return out_list
	
	#reutrn a list of next_node_id (may include branches)
	#curr_node_id_from aka prev_node_id_to
	def getNodeIdAfter(self,prev_node_id_from,curr_node_id_from,curr_node_id_to):
		prev_node_id=curr_node_id_from
		if(curr_node_id_from==curr_node_id_to):#if in branch, use previous node as anchor point to determine next node
			prev_node_id=prev_node_id_from
		curr_node_id=curr_node_id_to
		out_list=[]
		for row in self.branch_definition:
			#print("Maze.getNodeIdAfter: row: ",row)
			if(row["node_id_curr"]==curr_node_id):
				if(row["node_id_prev"]==prev_node_id): #forward relationship
					out_list.append(row["node_id_next"])
				elif(row["node_id_next"]==prev_node_id and row["is_two_way"]): #reverse relationship
					out_list.append(row["node_id_prev"])
		#make sure not get stuck in a loop - remove [curr_node_id_from,curr_node_id_to] relationship, if present
		#if(curr_node_id_from==curr_node_id_to):
		#	out_list=[row for row in out_list if not row==curr_node_id_to]
		if(len(out_list)>1): #if looking to branch out
			if(not curr_node_id_from==curr_node_id_to): #and not already in a branch
				out_list=[curr_node_id_to] #then specifically go to this upcoming branch
		return out_list
		
	#get the linear_definition for curr_ and prev_segment_id, but ordered (is_forward) for the partiular input sequence
	#returns {"prev":{"prev_id_node":X,"next_id_node":Y,"is_forward":bool,"segment_id":Z},
	#		  "curr":{"prev_id_node":X,"next_id_node":Y,"is_forward":bool,"segment_id":Z}}
	#put from_ and to_ nodes in order, and include the index of the segment in the segment_list
	def getOrderedLinearDefinition(self,curr_segment_id,prev_segment_id):
		prev_lin_def=self.getLinearDefinitionOfSegment(prev_segment_id)
		curr_lin_def=self.getLinearDefinitionOfSegment(curr_segment_id)
		if(curr_lin_def["node_id_prev"]==prev_lin_def["node_id_prev"] and
		   curr_lin_def["node_id_next"]==prev_lin_def["node_id_next"]): #then both segments within same node-node range
			if(prev_node_id["segment_id_index"]>curr_node_id["segment_id_index"]): #need to flip because headed backwards
				prev_lin_def=self.__reverseLinearDefinition(prev_lin_def)
				curr_lin_def=self.__reverseLinearDefinition(curr_lin_def)
		else:
			#else, stradelling some form of node-node boundary, and may need to reverse one or both segment linear_definition rows
			is_reverse_prev=True
			is_reverse_curr=True
			if(prev_lin_def["node_id_prev"]==prev_lin_def["node_id_next"]):
				is_reverse_prev=False #prev is branch
			if(curr_lin_def["node_id_prev"]==curr_lin_def["node_id_next"]):
				is_reverse_curr=False #curr is branch
			if(prev_lin_def["node_id_next"] in [curr_lin_def["node_id_prev"],curr_lin_def["node_id_next"]]):
				is_reverse_prev=False #prev in correct order
			if(curr_lin_def["node_id_prev"] in [prev_lin_def["node_id_prev"],prev_lin_def["node_id_next"]]):
				is_reverse_curr=False #curr in correct order
			if(is_reverse_prev): prev_lin_def=self.__reverseLinearDefinition(prev_lin_def)
			if(is_reverse_curr): curr_lin_def=self.__reverseLinearDefinition(curr_lin_def)
		#assert prev_lin_def["node_id_next"]==curr_lin_def["node_id_prev"]
		return {"prev":prev_lin_def,"curr":curr_lin_def}
		
	def __reverseLinearDefinition(self,row):
		row["is_forward"]=False
		was_node_id_prev=row["node_id_prev"]
		was_node_id_next=row["node_id_next"]
		row["node_id_next"]=was_node_id_prev#flip order of nodes so that _from_ is always first, before _to_
		row["node_id_prev"]=was_node_id_next
		row["segment_id_index"]=row["segment_list_len"]-row["segment_id_index"]-1 #flip orientation of list_index
		row["segment_list"]=list(reversed(row["segment_list"]))
		return row
		
	#given a segment_id, find the two nodes around it
	#always returns is_forward=True order
	def getLinearDefinitionOfSegment(self,segment_id):
		for row in self.linear_definition:
			if(segment_id in row["segment_list"]):
				return {
				"node_id_prev":row["node_id_prev"],
				"node_id_next":row["node_id_next"],
				"is_forward":True,
				"segment_id_index":row["segment_list"].index(segment_id),
				"segment_id":segment_id,
				"segment_list":row["segment_list"],
				"segment_list_len":len(row["segment_list"])}
		return None

	#given two (precon: sequential) nodes (OR same node to find branch segment(s)), find the segment list
	#segment list will always be in order from prev_node to curr_node
	#returns {"is_forward":True/False,"segment_list":[segment_id,segment_id,segment_id]}
	#note: method will blindly return segments even if they are not accessible in the stated order (ex. branch_definition is_two_way=False)
	def getSegmentsBetweenNodes(self,prev_node,next_node):
		for row in self.linear_definition:
			this_prev=row["node_id_prev"]
			this_next=row["node_id_next"]
			this_segments=row["segment_list"]
			hit=False
			is_forward=True
			if(this_prev==prev_node and this_next == next_node):
				hit=True
			elif(this_next==prev_node and this_prev==next_node):
				hit=True
				is_forward=False
				this_segments=list(reversed(this_segments))
			if(hit):
				return {"is_forward":is_forward,"node_id_prev":this_prev,"node_id_next":this_next,"segment_list":this_segments}
		return None

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
	#print(maze.linear_definition)
	#print(maze.branch_definition)
	#print(maze.segment_definition)
	#print(maze.debris_definition)
	print(maze.getSegmentIdAfter(2,3))
