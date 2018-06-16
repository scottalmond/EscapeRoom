

from chapters.wall.hyperspace_helper.Curve import Curve
from chapters.wall.hyperspace_helper.RingAssembly import RingAssembly

class Segment:
	DISTANCE_BETWEEN_RINGS=20.0 #Pi3D units of distance between rings
	RINGS_PER_SECOND=1.2 #how many rings per second the player passes through
	BRANCH_DISPLACEMENT_DISTANCE=2 #when selecting a branch path, there is
	# a lateral offset in the paths between the input and the 2 outputs
	# this is the distance between the input and one of the outputs in pi3d distance units
	# TODO: make diagram of branch mechanics for joint connections
	
	def __init__(self,asset_library,is_branch,start_position,start_rotation_matrix,
		start_time_seconds,curvature_degrees,orientation_degrees,ring_count,segment_id=0):#,
		#is_forward=True): #segments are naive to forward/backward notion, is managed by a super class instead
		self.start_time_seconds=start_time_seconds
		self.is_branch=is_branch
		self.curves=[] #math representation
		self.ring_assembly_list=[] #CAD models
		self.successor=[None,None,None] #pointer to next segment: center, left, right
		self.predecessor=None
		self.segment_id=segment_id
		#self.is_forward=is_forward
		if(self.is_branch):
			#center
			x_axis=start_rotation_matrix[0,:]
			self.curves.append(Curve(start_position,start_rotation_matrix,
				1.4*self.DISTANCE_BETWEEN_RINGS,0,0)) #ring branch (non-transversable)
				
			branch_dist=2.2
			branch_curvature=25
			#left branch
			start_left_pos=start_position-x_axis*self.BRANCH_DISPLACEMENT_DISTANCE
			self.curves.append(Curve(start_left_pos,start_rotation_matrix,
				branch_dist*self.DISTANCE_BETWEEN_RINGS,branch_curvature,180))
				
			#right branch
			start_right_pos=start_position+x_axis*self.BRANCH_DISPLACEMENT_DISTANCE
			self.curves.append(Curve(start_right_pos,start_rotation_matrix,
				branch_dist*self.DISTANCE_BETWEEN_RINGS,branch_curvature,0))
			self.addRingAssembly(asset_library,u=0.0,curve_id=0,ring_model_index=1)
			#self.addRingAssembly(asset_library,u=0.33,curve_id=0,ring_index=1)
			self.addRingAssembly(asset_library,u=1.0,curve_id=0,ring_model_index=0)
			self.curves[0].is_valid=False
		else:
			self.curves.append(Curve(start_position,start_rotation_matrix,
				ring_count*self.DISTANCE_BETWEEN_RINGS,curvature_degrees,orientation_degrees))
	
	#need a way to determine if a given segment should be extended
	# so recursively look for a predecessor segment that matches the current pod segment (target)
	# if the target pod segment is not in the tree, then the pod followed a different path
	def hasTraceabilityTo(self,target):
		if(self==target): return True
		if(self.__branches_alive()<=0 or self.predecessor is None): return False
		return self.predecessor.hasTraceabilityTo(target)
		
	def dispose(self):
		#if(self.is_branch):
		#	print('Segment.dispose: branch disposed')
		for curve in self.curves:
			curve.is_valid=False
	
	#if the pod position is <0, then go left, if life_elapsed_time_seconds is 
	#within the purview of this segment
	#is_left=True means the pod wants to go left (right branch will become invalid
	def decideBranch(self,life_elapsed_time_seconds,is_left):
		if(life_elapsed_time_seconds>self.start_time_seconds and self.is_branch and self.__branches_alive()>1):
			if(is_left):
				self.curves[2].is_valid=False
			else:
				self.curves[1].is_valid=False
	
	#count number of brnaches that are alive
	def __branches_alive(self):
		branch_count=0
		for curve in self.curves:
			if(curve.is_valid): branch_count+=1
		return branch_count
		
	def __getValidCurve(self):
		for curve in self.curves:
			if(curve.is_valid): return curve
		return None
		
	def getSuccessor(self):
		if(self.is_branch):
			if(self.isLeft()):
				return self.successor[1]
			#print('Segment.getSuccessor: '+str(self.isLeft()))
			return self.successor[2]
		else:
			return self.successor[0]
		
	#returns True is left branch has been select, Flase for right branch
	# and None for no selection yet, or not a branch
	def isLeft(self):
		if(self.is_branch):
			if(self.curves[1].is_valid and not self.curves[2].is_valid):
				return True
			if(self.curves[2].is_valid and not self.curves[1].is_valid):
				return False
		return None
		
	#get a list of dictionaries defining the end point of a path
	#first index is for left path, second is for right path (if is_branch)
	def getEndPoints(self):
		output=[]
		curve_id_list=[1,2] if self.is_branch else [0]
		for curve_id in curve_id_list:
			curve=self.curves[curve_id]
			orientation_end=curve.getOrientationAlongCurve(1.0)
			start_position=orientation_end["position"]
			start_rotation_matrix=orientation_end["rotation_matrix"]
			start_time_seconds=curve.distance/(self.DISTANCE_BETWEEN_RINGS*self.RINGS_PER_SECOND)+self.start_time_seconds
			curve_out={"id":curve_id,
					   "is_valid":curve.is_valid,
					   "position":start_position,
					   "rotation_matrix":start_rotation_matrix,
					   "timestamp_seconds":start_time_seconds
					  }
			output.append(curve_out)
		return output
	
	#seconds
	def durationSeconds(self):
		#curve=self.__getValidCurve()
		curve=self.curves[-1]
		duration_seconds=curve.distance/(self.DISTANCE_BETWEEN_RINGS*self.RINGS_PER_SECOND)
		return duration_seconds
	
	#determine if the input timestamp in seconds lies within the
	# time domain of this segment
	#DEPRECIATED: getRatio
	def isValidTime(self,elapsed_time):
		#curve=self.__getValidCurve()
		duration_seconds=self.durationSeconds()#curve.distance/(self.DISTANCE_BETWEEN_RINGS*self.RINGS_PER_SECOND)
		max_time_seconds=self.start_time_seconds+duration_seconds
		return self.start_time_seconds <= elapsed_time <= max_time_seconds
		#TODO: revise to return u --> only valid from u=[0,1], <0 is before, >1 is after
	
	#get u, may be <0 or >1, indicating out of range
	def getRatio(self,elapsed_time):
		#curve=self.__getValidCurve()
		duration_seconds=self.durationSeconds()#curve.distance/(self.DISTANCE_BETWEEN_RINGS*self.RINGS_PER_SECOND)
		max_time_seconds=self.start_time_seconds+duration_seconds
		return (elapsed_time-self.start_time_seconds)/(max_time_seconds-self.start_time_seconds)
		
	def getOrientationAtTime(self,elapsed_time):
		curve=self.__getValidCurve()
		duration_seconds=self.durationSeconds()#curve.distance/(self.DISTANCE_BETWEEN_RINGS*self.RINGS_PER_SECOND)
		u=self.getRatio(elapsed_time)#(elapsed_time-self.start_time_seconds)/duration_seconds
		output=curve.getOrientationAlongCurve(u)
		if(self.is_branch):
			position=output['position']
			rotation_matrix=output['rotation_matrix']
			x_axis=-rotation_matrix[0,:]
			delta_x=x_axis*self.BRANCH_DISPLACEMENT_DISTANCE*(1-u)
			if(self.isLeft()):
				position-=delta_x
			else:
				position+=delta_x
		return output
	
	#curve_id is the branch id number - for straight paths the value is 0 (default)
	#u is between 0 and 1
	def addRingAssembly(self,asset_library,u,curve_id=0,
		ring_model_index=1,ring_rotation_degrees=0,ring_rotation_rate=0,debris_rotation_degrees=0,debris_rotation_rate=0):
		curve=self.curves[curve_id]
		definition_time=self.start_time_seconds+u*curve.distance/(self.DISTANCE_BETWEEN_RINGS*self.RINGS_PER_SECOND)
		ring_orientation=curve.getOrientationAlongCurve(u)
		ring_assembly=RingAssembly(asset_library,ring_orientation["position"],
			ring_orientation["rotation_euler"],ring_orientation["rotation_matrix"],
			definition_time,ring_model_index,
			ring_rotation_degrees,ring_rotation_rate,
			debris_rotation_degrees,debris_rotation_rate)
		self.ring_assembly_list.append(ring_assembly)
		#if(ring_index==0):
		#	print("curve_id: "+str(curve_id))
		#	print("definition_time: "+str(definition_time))
		#	print("definition_time: "+str(self.start_time_seconds))
		return ring_assembly
		
	def update(self,life_elapsed_time_seconds,light):
		for ring_assembly in self.ring_assembly_list:
			ring_assembly.update(life_elapsed_time_seconds,light)
		
	def draw(self):
		for ring_assembly in self.ring_assembly_list:
			ring_assembly.draw()
