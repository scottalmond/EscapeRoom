#consists of the following tree structure:
#  global axis  <-- fixed location & rotation in space
#    ring <-- rotates at one rate in z-dimension
#    debris axis <-- rotates at another rate in the z-dimension
#        asteroid 1
#        asteroid 2
#        asteroid 3
#    art asteroid <-- any debris outside the playing field for aesthetics

from enum import Enum

class DEBRIS_TYPE(Enum):
	ASTEROID_LARGE=0
	ASTEROID_MEDIUM=1

class RingAssembly:
	PRE_RENDER_SECONDS=5 #render objects that are defined between now and X seconds into the future
	POST_RENDER_SECONDS=1
	
	RING_ROTATION_DEGREES_PER_SECOND=-40
	DEBRIS_ROTATION_DEGREES_PER_SECOND=10
	
	#asset_library is an instance of the AssetLibrary with the template 3D models
	#position is the np.array of x,y,z coords in the global reference frame for hte center of the ring
	#rotation_euler is the Z-X-Y euler rotation angles in degrees, and
	#rotation_matrix is the pi3d rotation matrix for the Shape
	#definition_time is the time at which this RingAssembly is defined
	# all rotation rates are movtions are computed as a linear propagation
	# forward or backward from this timestamp in seconds
	#ring_index is the 3D model to use: None for none, 0 or more for straight or branched as defined in AssetLibrary.rings
	#ring_rotation_degrees is the rotation of the ring at the time definition_time
	#ring_rotation_rate is degrees per second rotation about the Z axis for the ring
	#debris_rotation_rate is degrees per second rotation of the cumulative debris about the Z axis
	def __init__(self,asset_library,position,rotation_euler,rotation_matrix,definition_time,
		ring_index,ring_rotation_degrees,ring_rotation_rate,debris_rotation_rate):
		#variables
		self.rotation_euler=rotation_euler
		self.rotation_matrix=rotation_matrix
		self.definition_time=definition_time
		self.ring_rotation_degrees=ring_rotation_degrees
		self.ring_rotation_rate=ring_rotation_rate
		self.debris_rotation_rate=debris_rotation_rate
		self.is_visible=False
		self.asset_library=asset_library
		
		#global axis
		self.global_axis=asset_library.invisible.shallow_clone()
		self.global_axis.children=[]
		self.global_axis.position(position[0],position[1],position[2])
		self.global_axis.rotateToX(rotation_euler[0])
		self.global_axis.rotateToY(rotation_euler[1])
		self.global_axis.rotateToZ(rotation_euler[2])
		
		#ring
		self.ring=asset_library.rings[ring_index].shallow_clone()
		self.ring.children=[]
		self.global_axis.add_child(self.ring)
		
		#debris axis
		self.debris_axis=None
		
		#debris objects
		self.debris_list=[]
		
	#add a piece of debris to this debris_axis
	#location is an [x,y,z] numpy.array of the debris at definition_time
	#angle is the numpy.array [x,y,z] rotation at definition_time measures in degrees
	#angular_velocity is degrees per second
	def addDebris(self,debris_type,location,angle,angular_velocity):
		if(self.debris_axis is None):
			#debris axis, declare only on first usage
			self.debris_axis=self.asset_library.invisible.shallow_clone()
			self.debris_axis.children=[]
			self.global_axis.add_child(self.debris_axis)
		model=None
		if(debris_type==DEBRIS_TYPE.ASTEROID_LARGE):
			model=self.asset_library.asteroid_large.shallow_clone()
		elif(debris_type==DEBRIS_TYPE.ASTEROID_MEDIUM):
			model=self.asset_library.asteroid_medium.shallow_clone()
		model.children=[]
		model.position(location[0],location[1],location[2])
		self.debris_list.append({"model":model,
								 "debris_type":debris_type,
								 "location":location,
								 "angle":angle,
								 "angular_velocity":angular_velocity})
		self.debris_axis.add_child(model)

	def update(self,life_elapsed_time_seconds,light):
		min_time=self.definition_time - self.PRE_RENDER_SECONDS
		max_time=self.definition_time + self.POST_RENDER_SECONDS
		self.is_visible= min_time <= life_elapsed_time_seconds <= max_time
		#if(self.is_visible):
		seconds_offset=(life_elapsed_time_seconds-self.definition_time)
		self.ring.rotateToZ(self.ring_rotation_rate*seconds_offset+self.ring_rotation_degrees)
		if(not self.debris_axis is None):
			self.debris_axis.rotateToZ(self.debris_rotation_rate*seconds_offset)
		self.ring.set_light(light)
		for debris in self.debris_list:
			rot=debris["angle"]
			rot_rate=debris["angular_velocity"]
			model=debris["model"]
			model.rotateToX(rot_rate[0]*seconds_offset+rot[0])
			model.rotateToY(rot_rate[1]*seconds_offset+rot[1])
			model.rotateToZ(rot_rate[2]*seconds_offset+rot[2])
			model.set_light(light)

	def draw(self):
		#TODO: checks if ring is visible, otherwise does not render
		if(self.is_visible):
			self.global_axis.draw()

	#return list of x,y,z and radius for each phyisical (non-art) asteroid
	def getAsteroidPositions(self):
		pass
