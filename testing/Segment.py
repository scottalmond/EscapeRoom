from Curve import Curve
from RingAssembly import RingAssembly

class Segment:
	DISTANCE_BETWEEN_RINGS=20.0 #Pi3D units of distance between rings
	RINGS_PER_SECOND=1.2 #how many rings per second the player passes through
	
	def __init__(self,asset_library,is_branch,start_position,start_rotation_matrix,
		start_time_seconds,curvature_degrees,orientation_degrees,ring_count):
		self.start_time_seconds=start_time_seconds
		self.is_branch=is_branch
		self.curves=[] #math representation
		self.ring_assembly_list=[] #CAD models
		if(self.is_branch):
			self.curves.append(Curve(start_position,start_rotation_matrix,
				3*self.DISTANCE_BETWEEN_RINGS,0,0)) #ring branch (non-transversable)
			self.curves.append(Curve(start_position,start_rotation_matrix,
				3*self.DISTANCE_BETWEEN_RINGS,25,180)) #left branch
			self.curves.append(Curve(start_position,start_rotation_matrix,
				3*self.DISTANCE_BETWEEN_RINGS,25,0)) #right branch
			self.addRingAssembly(asset_library,u=0.0,curve_id=0,ring_index=1)
			self.addRingAssembly(asset_library,u=0.33,curve_id=0,ring_index=1)
			self.addRingAssembly(asset_library,u=0.66,curve_id=0,ring_index=0)
			self.curves[0].is_valid=False
		else:
			self.curves.append(Curve(start_position,start_rotation_matrix,
				ring_count*self.DISTANCE_BETWEEN_RINGS,curvature_degrees,orientation_degrees))

	#if the pod position is <0, then go left, if life_elapsed_time_seconds is 
	#within the purview of this segment
	#is_left=True means the pod wants to go left (right branch will become invalid
	def decideBranch(life_elapsed_time_seconds,is_left):
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
			curve_out={"curve_id":curve_id,
					   "is_valid":curve.is_valid,
					   "position":start_position,
					   "rotation_matrix":start_rotation_matrix,
					   "timestamp_seconds":start_time_seconds
					  }
			output.append(curve_out)
		return output
	
	#determine if the input timestamp in seconds lies within the
	# time domain of this segment
	def isValidTime(self,elapsed_time):
		curve=self.__getValidCurve()
		duration_seconds=curve.distance/(self.DISTANCE_BETWEEN_RINGS*self.RINGS_PER_SECOND)
		max_time_seconds=self.start_time_seconds+duration_seconds
		return self.start_time_seconds <= elapsed_time <= max_time_seconds
	
	def getOrientationAtTime(self,elapsed_time):
		curve=self.__getValidCurve()
		duration_seconds=curve.distance/(self.DISTANCE_BETWEEN_RINGS*self.RINGS_PER_SECOND)
		u=(elapsed_time-self.start_time_seconds)/duration_seconds
		return curve.getOrientationAlongCurve(u)
	
	def addRingAssembly(self,asset_library,u,curve_id=0,
		ring_index=1,ring_rotation_degrees=0,ring_rotation_rate=0,debris_rotation_rate=0):
		curve=self.curves[curve_id]
		definition_time=self.start_time_seconds+u*curve.distance/(self.DISTANCE_BETWEEN_RINGS*self.RINGS_PER_SECOND)
		ring_orientation=curve.getOrientationAlongCurve(u)
		ring_assembly=RingAssembly(asset_library,ring_orientation["position"],
			ring_orientation["rotation_euler"],ring_orientation["rotation_matrix"],
			definition_time,ring_index,ring_rotation_degrees,
			ring_rotation_rate,debris_rotation_rate)
		self.ring_assembly_list.append(ring_assembly)
		if(ring_index==0):
			print("curve_id: "+str(curve_id))
			print("definition_time: "+str(definition_time))
			print("definition_time: "+str(self.start_time_seconds))
		return ring_assembly
		
	def update(self,life_elapsed_time_seconds,light):
		for ring_assembly in self.ring_assembly_list:
			ring_assembly.update(life_elapsed_time_seconds,light)
		
	def draw(self):
		for ring_assembly in self.ring_assembly_list:
			ring_assembly.draw()
