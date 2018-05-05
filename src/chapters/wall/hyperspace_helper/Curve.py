
class Curve:
	def __init__(self,start_position,start_rotation_matrix,
		distance,curvature_degrees,orientation_degrees):
		if(abs(curvature_degrees)<0.0001): curvature_degrees=0.0001 #lower limit to approx stright line (easier than making special case for a line)
		self.start_position=start_position
		self.start_rotation_matrix=start_rotation_matrix
		self.distance=distance
		self.curvature_degrees=curvature_degrees
		self.orientation_degrees=orientation_degrees
		state=self.__getPath(start_position,start_rotation_matrix,
			distance,curvature_degrees,orientation_degrees)
		self.curvature_radians=state["curvature_radians"]
		self.orientation_radians=state["orientation_radians"]
		self.coeff=state["coeff"]
		self.normal=state["normal"]
		self.is_valid=True #is it possible for a pod to travel down this path
		# that is, the player has not directed the pod down another path
	
	#METHODS
	
	def getOrientationAlongCurve(self,u):
		relative_orientation=self.__getOrientationAlongCurve(self,u)
		this_rotation=relative_orientation["rotation_matrix"]
		this_position=relative_orientation["position"]
		cumulative_rotation=this_rotation.dot(self.start_rotation_matrix)
		cumulative_position=this_position.dot(self.start_rotation_matrix)+self.start_position
		euler=Curve.euler_angles(cumulative_rotation)
		output={"position":cumulative_position, #X, Y, Z
				"rotation_euler":euler, #X, Y, Z, degrees
				"rotation_matrix":cumulative_rotation}
		return output
	
	
	#HELPER METHODS
	
	#get the coeffs used to define a circular arc
	#input:
	# start_position is the u=0 position in the Path (passed directly to
	#  output and not otherwise used)
	# start_rotation_matrix is the rotation matrix of the Path at u=0 (passed
	#  directly to output and not otherwise used)
	# distance is arc length in Pi3d distance units
	# curvature_degrees is number of degrees of arc: 0 degrees is a straight line (TODO: fix div zero error),
	#  90 degrees turns the input motion into perpendicular motion
	# orientation_degrees is the z-axis rotation: 0 degrees is right, 90 degrees is up, 180 to the left, 270 down
	#output:
	# coeffients (3 element np.array) for a parameterized segment of the form:
	#  position(u)=[cos(u*2*np.pi)*x_coeff,cos(u*2*np.pi)*y_coeff,sin(u*2*np.pi)*z_coeff]
	#  where u is valid from 0 (start of arc) to 1 (end of arc)
	# normal (3 element np.array): an x,y,z vector representing the axis of rotation of the Path from start to finish
	@staticmethod
	def __getPath(start_position,start_rotation_matrix,
				distance,curvature_degrees,orientation_degrees):
		import numpy as np
		arc_length=2*np.pi*curvature_degrees/360 #compute an initial estimate of arc length
		unit_scale=distance/arc_length #scale the initial curve computation to be the specified length
		orientation_radians=orientation_degrees*np.pi/180
		curvature_radians=curvature_degrees*np.pi/180
		x_coeff=np.cos(-orientation_radians)*unit_scale
		y_coeff=-np.sin(-orientation_radians)*unit_scale
		z_coeff=-unit_scale
		coeff=np.array([x_coeff,y_coeff,z_coeff])
		x_norm=np.sin(orientation_radians)#axis representing a vector normal to the axis of curvature rotation
		y_norm=-np.cos(orientation_radians)
		z_norm=0
		normal=np.array([x_norm,y_norm,z_norm])
		output={"start_rotation_matrix":start_rotation_matrix,
				"start_position":start_position,
				"distance":distance,
				"curvature_degrees":curvature_degrees,
				"curvature_radians":curvature_radians,
				"orientation_degrees":orientation_degrees,
				"orientation_radians":orientation_radians,
				"coeff":coeff,
				"normal":normal
			   }
		return output
		
	#at a given ratio u between 0 and 1, extract the position and rotation of
	# a target point
	#output: x,y,z postion in pi3d distance units
	# X,Y,Z: Z-X-Y Euler rotation angles in degrees
	@staticmethod
	def __getOrientationAlongCurve(curve,u):
		import numpy as np
		#angles
		curvature_degrees=curve.curvature_degrees
		curvature_radians=curve.curvature_radians
		orientation_radians=curve.orientation_radians
		#position
		x_coeff=curve.coeff[0]
		y_coeff=curve.coeff[1]
		z_coeff=curve.coeff[2]
		v=u*curvature_degrees/360 #scale to fraction of full circle
		x_2d=-np.cos(v*2*np.pi)+1
		x_pos=x_2d*x_coeff
		y_pos=x_2d*y_coeff
		z_pos=-np.sin(v*2*np.pi)*z_coeff
		position=np.array([x_pos,y_pos,z_pos])
		#rotation
		theta=curvature_radians*u
		r_hat=curve.normal
		rotation_matrix=Curve.__getRotationMatrixAboutVector(r_hat,theta)
		euler=Curve.euler_angles(rotation_matrix) #degrees
		output={"position":position, #X, Y, Z
				"rotation_euler":euler, #X, Y, Z, degrees
				"rotation_matrix":rotation_matrix}
		return output

	#copy-paste from pi3d.Camera to make a static endpoint
	@staticmethod
	def euler_angles(matrix):
		import math
		m = matrix # alias for clarity
		rx = math.asin(m[1,2])
		cx = math.cos(rx)
		if cx != 0.0:
			ry = math.atan2(-m[0,2], m[2,2])
		else:
			ry = math.pi / 2.0
		rz = math.atan2(-m[1,0], m[1,1])
		return math.degrees(rx), math.degrees(ry), math.degrees(rz)
		
	#use one vector to define first axis, and second vector as an apriori estaimte at the second axis
	#axis_type and axis_type_apriori are single character Strings: 'x', 'y' or 'z'
	#vector_axis and vector_apriori are np.array(1x3)
	#output will be a dict with the following:
	# Euler angles in degrees as np.array(1x3)
	# rotation_matrix per pi3d usage
	#precon: axis_type =/= axis_type_apriori
	#precon: vector_axis =/= vector_apriori
	#precon: vector_axis =/= -vector_apriori
	#TODO: generalize
	@staticmethod
	def euler_angles_from_vectors(vector_axis,axis_type,vector_apriori,axis_type_apriori):
		import numpy as np
		z_vector=vector_axis/np.linalg.norm(vector_axis)
		y_vector_pre=vector_apriori
		x_vector=np.cross(y_vector_pre,z_vector)
		x_vector/=np.linalg.norm(x_vector)
		y_vector=np.cross(z_vector,x_vector)
		y_vector/=np.linalg.norm(y_vector)
		rot_matrix=np.array([x_vector,y_vector,z_vector]).T
		euler=Curve.euler_angles(rot_matrix)
		return {"rotation_euler":euler,"rotation_matrix":rot_matrix}
		
		

	#equation from section 9.2 from: http://ksuweb.kennesaw.edu/~plaval/math4490/rotgen.pdf
	#as camera/pod/etc position is moved around segment, ensure the rotation 
	# reference frame is also rotated in the same way
	@staticmethod
	def __getRotationMatrixAboutVector(r_hat,theta_radians):
		import numpy as np
		import math
		ux=r_hat[0]
		uy=r_hat[1]
		uz=r_hat[2]
		C=math.cos(theta_radians)
		S=math.sin(theta_radians)
		t=1-C
		T=[[t*ux*ux+C,t*ux*uy-S*uz,t*ux*uz+S*uy],
		   [t*ux*uy+S*uz,t*uy*uy+C,t*uy*uz-S*ux],
		   [t*ux*uz-S*uy,t*uy*uz+S*ux,t*uz*uz+C]]
		return np.array(T)
		
