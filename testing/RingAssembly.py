#consists of the following tree structure:
#  global axis  <-- fixed location & rotation in space
#    ring <-- rotates at one rate in z-dimension
#    debris axis <-- rotates at another rate in the z-dimension
#        asteroid 1
#        asteroid 2
#        asteroid 3
#    art asteroid <-- any debris outside the playing field for aesthetics

class RingAssembly:
	PRE_RENDER_SECONDS=5 #render objects that are defined between now and X seconds into the future
	POST_RENDER_SECONDS=1
	
	RING_ROTATION_DEGREES_PER_SECOND=30
	
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

	def update(self,life_elapsed_time_seconds,light):
		min_time=self.definition_time - self.PRE_RENDER_SECONDS
		max_time=self.definition_time + self.POST_RENDER_SECONDS
		self.is_visible= min_time <= life_elapsed_time_seconds <= max_time
		#if(self.is_visible):
		self.ring.rotateToZ(self.ring_rotation_rate*(life_elapsed_time_seconds-self.definition_time)+self.ring_rotation_degrees)
		self.ring.set_light(light)
		#TODO: set is-visible here

	def draw(self):
		#TODO: checks if ring is visible, otherwise does not render
		if(self.is_visible):
			self.global_axis.draw()

	#return list of x,y,z and radius for each phyisical (non-art) asteroid
	def getAsteroidPositions(self):
		pass
