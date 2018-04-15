# python3 /home/pi/Documents/EscapeRoom/testing/test25_smooth_camera_motion.py 
import sys
import sys
sys.path.insert(1,'/home/pi/pi3d') # to use local 'develop' branch version
import pi3d
import numpy as np
import math
import random
import time

random.seed(0) #desire predicable results so it's possible to reproduce any visual anomalies seen

MODEL_PATH = 'models/'
RINGS_PER_SECOND=2.0 #how many rings per second the player passes through
DISTANCE_BETWEEN_RINGS=20.0 #Pi3D units of distance between rings
#POD_DISTANCE_PER_SECOND=DISTANCE_BETWEEN_RINGS*RINGS_PER_SECOND
RING_ROTATION_DEGREES_PER_SECOND=30

MAX_POD_DISPLACEMENT=3.7 #2.8 #maximum distance the pod can be from the center of the playfield
POD_DISTANCE_PER_SECOND=10.0 #rate of pod movement per second

#playfield
display = pi3d.Display.create(background=(0.0, 0.0, 0.0, 0.0))
camera = pi3d.Camera()
shader = pi3d.Shader('uv_light')
light=pi3d.Light(lightpos=(10,-10,-7),lightcol=(0.75,0.75,0.45), lightamb=(0.1,0.1,0.42),is_point=False)
keys = pi3d.Keyboard()

#models
# rings
ring_list=[]
ring_template = pi3d.Model(file_string=MODEL_PATH+'straight_ring_1.obj')
ring_template.set_shader(shader)
ring_template.set_fog((0.0, 0.0, 0.0, 0.0), 130.8)
# is there a way to getHeight (z dimension) of a Shape in Pi3D...?

# pod
pod = pi3d.Model(file_string=MODEL_PATH+'pod_2.obj', z=0.0)
pod_scale=0.33
pod.scale(pod_scale,pod_scale,pod_scale)
laser_base = pi3d.Model(file_string=MODEL_PATH+'laser_base_2.obj', y=3.15)
laser_gun = pi3d.Model(file_string=MODEL_PATH+'laser_gun_2.obj', y=0.4, z=-0.4)
laser_base.add_child(laser_gun)
pod.add_child(laser_base)
pod.set_shader(shader) # all use uv_light shader
pod_x=0
pod_y=0

# asteroid
asteroid_scale=0.55
asteroid_template = pi3d.Model(file_string=MODEL_PATH+'asteroid_large_1.obj',sx=asteroid_scale,sy=asteroid_scale,sz=asteroid_scale)
asteroid_template.set_shader(shader)
#asteroid_template.set_fog((0.0, 0.0, 0.0, 0.0), 300.6)

# debug sphere
sphere=pi3d.Sphere(radius=3.0)
sphere.position(0,0,100)

#input:
#start_time of segment in seconds (passed directly to output and not otherwise used)
#duration of segment in seconds (passed directly to output and not otherwise used)
#start_position is the u=0 position in the segment (passed directly to
# output and not otherwise used)
#start_rotation_matrix is the rotation matrix of the segment at u=0 (passed
# directly to output and not otherwise used)
#distance is arc length in Pi3d distance units
#curvature is number of degrees of arc: 0 degrees is a straight line (TODO: fix div zero error),
# 90 degrees turns the input motion into perpendicular motion
#orientation is the z-axis rotation: 0 degrees is right, 90 degrees is up, 180 to the left, 270 down
#output:
# coeffients for a parameterized segment of the form:
# position(u)=[cos(u*2*np.pi)*x_coeff,cos(u*2*np.pi)*y_coeff,sin(u*2*np.pi)*z_coeff]
# where u is valid from 0 (start of arc) to 1 (end of arc)
def getSegmentParameters(start_time,duration,start_position,start_rotation_matrix,distance,curvature_degrees,orientation_degrees):
	arc_length=2*np.pi*curvature_degrees/360 #compute an initial estimate of arc length
	unit_scale=distance/arc_length #scale the initial curve computation to be the specified length
	orientation_radians=orientation_degrees*np.pi/180
	curvature_radians=curvature_degrees*np.pi/180
	x_coeff=np.cos(-orientation_radians)*unit_scale
	y_coeff=-np.sin(-orientation_radians)*unit_scale
	z_coeff=-unit_scale
	x_norm=math.sin(orientation_radians)#axis representing a vector normal to the axis of curvature rotation
	y_norm=-math.cos(orientation_radians)
	z_norm=0
	output={"start_time":start_time,
		    "duration":duration,
		    "start_rotation_matrix":start_rotation_matrix,
		    "start_position":start_position,
		    "distance":distance,
		    "curvature_degrees":curvature_degrees,
		    "curvature_radians":curvature_radians,
		    "orientation_degrees":orientation_degrees,
		    "orientation_radians":orientation_radians,
		    "x_coeff":x_coeff,
		    "y_coeff":y_coeff,
		    "z_coeff":z_coeff,
		    "x_norm":x_norm,
		    "y_norm":y_norm,
		    "z_norm":z_norm}
	return output
	
#at a given ratio u between 0 and 1, extract the position and rotation of
# a target point
#output: x,y,z postion in pi3d distance units
# X,Y,Z: Z-X-Y Euler rotation angles in degrees
def getOrientationAtTime(segment,u):
	x_coeff=segment["x_coeff"]
	y_coeff=segment["y_coeff"]
	z_coeff=segment["z_coeff"]
	curvature_degrees=segment["curvature_degrees"]
	curvature_radians=segment["curvature_radians"]
	orientation_radians=segment["orientation_radians"]
	theta=segment["curvature_radians"]*u
	u=u*curvature_degrees/360
	x_2d=-np.cos(u*2*np.pi)+1
	x_pos=x_2d*x_coeff
	y_pos=x_2d*y_coeff
	z_pos=-np.sin(u*2*np.pi)*z_coeff
	#testing
	r_hat=np.array([segment["x_norm"],segment["y_norm"],segment["z_norm"]])
	rotation_matrix=getRotationMatrixAboutVector(r_hat,theta)
	euler=camera.euler_angles(rotation_matrix) #degrees
	x_rot=euler[0]
	y_rot=euler[1]
	z_rot=euler[2]
	output={"x_pos":x_pos,
			"y_pos":y_pos,
			"z_pos":z_pos,
			"x_rot":x_rot,
			"y_rot":y_rot,
			"z_rot":z_rot,
			"rotation_matrix":rotation_matrix}
	return output
	
#given an elapsed time since level start, extract the position, rotation
# and rotation matrix for a node at the given point along the relevant segment
#output x,y,z_pos in pi3d distance units
# x,y,z_rot in degrees
# rotation_matrix as 3x3 numpy
def getOrientationAtElapsedTime(elapsed_time_seconds):
	for segment_id in range(len(segment_list)):
		segment=segment_list[segment_id]
		duration=segment["duration"]
		u=elapsed_time_seconds/duration
		elapsed_time_seconds-=duration
		if( (segment_id>=(len(segment_list)-1)) or (u<=1) ):
			orientation=getOrientationAtTime(segment,u)
			vector=np.array([orientation["x_pos"],orientation["y_pos"],orientation["z_pos"]])
			start_position=segment["start_position"] #defined in global coord frame
			start_rotation=segment["start_rotation_matrix"]
			this_position=np.array([orientation["x_pos"],orientation["y_pos"],orientation["z_pos"]])
			this_rotation=orientation["rotation_matrix"]
			#pre-mult first operation, then post-mult for second operation
			cumulative_rotation=this_rotation.dot(start_rotation)
			#print("this_position: "+str(this_position))
			#print("start_rotation: "+str(start_rotation))
			#print("this_position*start_rotation: "+str(this_position.dot(start_rotation)))
			#raise AssertionError("stop")
			cumulative_position=this_position.dot(start_rotation)+start_position
			euler=camera.euler_angles(cumulative_rotation) #degrees
			x_rot=euler[0]
			y_rot=euler[1]
			z_rot=euler[2]
			#print("u: "+str(cumulative_position))
			output={"x_pos":cumulative_position[0],
					"y_pos":cumulative_position[1],
					"z_pos":cumulative_position[2],
					"x_rot":x_rot,
					"y_rot":y_rot,
					"z_rot":z_rot,
					"rotation_matrix":cumulative_rotation}
			return output
			
#repurposed pi3d.Camera.euler_angles for multiple input vectors (direction
# and apriori y-axis)
def euler_angles(vector,u,segment,elapsed_time):
	z_vector=vector/np.linalg.norm(vector)
	#y_vector_pre=getOrientationAtTime(segment,u)["rotation_matrix"][1,:]
	y_vector_pre=getOrientationAtElapsedTime(elapsed_time)["rotation_matrix"][1,:]
	x_vector=np.cross(y_vector_pre,z_vector)
	x_vector/=np.linalg.norm(x_vector)
	y_vector=np.cross(z_vector,x_vector)
	y_vector/=np.linalg.norm(y_vector)
	rot_matrix=np.array([x_vector,y_vector,z_vector]).T
	#rot_matrix=getOrientationAtTime(segment,u)["rotation_matrix"].T #verified workable
	
	#rot_matrix=camera.matrix_from_two_vectors(np.array([0,0,1.0]),vector)
	#r_hat=np.array([segment["x_norm"],segment["y_norm"],segment["z_norm"]])
	#theta=segment["curvature_radians"]*u
	#rot_matrix=getRotationMatrixAboutVector(r_hat,theta)
	euler=camera.euler_angles(rot_matrix)
	#X=math.acos(rot_matrix[1,1])
	#Y=math.acos(rot_matrix[0,0])
	#Z=0
	#print("camera: "+str([euler[0],euler[1],euler[2]]))
	return [euler[0],euler[1],euler[2],rot_matrix]
	#return [X,Y,Z]
	
#equation from section 9.2 from: http://ksuweb.kennesaw.edu/~plaval/math4490/rotgen.pdf
#as camera/pod/etc position is moved around segment, ensure the rotation 
# reference frame is also rotated in the same way
def getRotationMatrixAboutVector(r_hat,theta_radians):
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
	
#variables
segment_list=[]
ring_list=[]

frame_id=0	
previous_time=time.time()
time_elapsed=0
	
#first segment definition
segment_ring_count=10
segment=getSegmentParameters(0,segment_ring_count/RINGS_PER_SECOND,
	np.array([0,0,0]),np.identity(3),segment_ring_count*DISTANCE_BETWEEN_RINGS,270,60)
segment_list.append(segment)
segment_out=getOrientationAtTime(segment,1)

pos=np.array([segment_out["x_pos"],segment_out["y_pos"],segment_out["z_pos"]])
sphere.position(pos[0],pos[1],pos[2])

#second segement definition
segment_ring_count2=10
segment2=getSegmentParameters(segment["duration"],segment_ring_count2/RINGS_PER_SECOND,
	np.array([segment_out["x_pos"],segment_out["y_pos"],segment_out["z_pos"]]),
	segment_out["rotation_matrix"],segment_ring_count2*DISTANCE_BETWEEN_RINGS,
	180,300)
segment_list.append(segment2)

#populate segment 1 rings
for step in range(segment_ring_count):
	u=step/segment_ring_count
	ring=ring_template.shallow_clone()
	orientation=getOrientationAtTime(segment,u)
	ring.position(orientation["x_pos"],orientation["y_pos"],orientation["z_pos"])
	ring.rotateToX(orientation["x_rot"])
	ring.rotateToY(orientation["y_rot"])
	ring.rotateToZ(orientation["z_rot"])
	ring_list.append(ring)
	print("segemnt1 ring pos: "+str([orientation["x_pos"],orientation["y_pos"],orientation["z_pos"]]))
	#print("ring rot: "+str([orientation["x_rot"],orientation["y_rot"],orientation["z_rot"]]))

#populate segment 2 rings
for step in range(segment_ring_count2):
	u=step/segment_ring_count
	ring=ring_template.shallow_clone()
	ring_elapsed_time=u*segment2["duration"]+segment2["start_time"]
	orientation=getOrientationAtElapsedTime(ring_elapsed_time)
	ring.position(orientation["x_pos"],orientation["y_pos"],orientation["z_pos"])
	ring.rotateToX(orientation["x_rot"])
	ring.rotateToY(orientation["y_rot"])
	ring.rotateToZ(orientation["z_rot"])
	ring_list.append(ring)
	print("segment2 ring pos: "+str([orientation["x_pos"],orientation["y_pos"],orientation["z_pos"]]))
	
#debug init
pod.position(0,0,10)

#raise AssertionError("stop")

while display.loop_running():
	#housekeeping
	frame_id+=1
	#restart motion at end of segments
	if(time_elapsed>(segment_list[-1]["start_time"]+segment_list[-1]["duration"])):
		time_elapsed=0
		previous_time=time.time()
		previous_time=time.time()
	this_timestamp=time.time()
	delta_time=this_timestamp-previous_time
	time_elapsed+=delta_time
	previous_time=this_timestamp
	
	#user input
	buttons=[]
	k=0
	while k>=0:
		k = keys.read()
		buttons.append(k)
	k=max(buttons)
	
	#camera, lights
	u_camera=time_elapsed/segment["duration"]
	u_target=(time_elapsed+0.4)/segment["duration"]
	#orientation_camera=getOrientationAtTime(segment,u_camera)
	#orientation_target=getOrientationAtTime(segment,u_target)
	orientation_camera=getOrientationAtElapsedTime(time_elapsed)
	orientation_target=getOrientationAtElapsedTime(time_elapsed+0.4)
	x_axis=orientation_camera["rotation_matrix"][0,:]
	y_axis=orientation_camera["rotation_matrix"][1,:]
	z_axis=orientation_camera["rotation_matrix"][1,:]
	position_camera=np.array([orientation_camera["x_pos"],orientation_camera["y_pos"],orientation_camera["z_pos"]])
	position_target=np.array([orientation_target["x_pos"],orientation_target["y_pos"],orientation_target["z_pos"]])
	camera_movement_scale=0.4
	position_camera+=x_axis*pod_x*camera_movement_scale
	position_camera+=y_axis*pod_y*camera_movement_scale
	position_target+=x_axis*pod_x
	position_target+=y_axis*pod_y
	xyz_degrees=euler_angles(position_target-position_camera,u_camera,segment,time_elapsed)
	#light_vect=np.array([10,-10,-7])
	#light_vect=np.array([0,0,-10])
	#light_vect=light_vect.dot(xyz_degrees[3])
	light_vect=(position_target+x_axis*15-y_axis*15)-position_camera #have light point somewhere down-right of target
	light_vect[2]=-light_vect[2]
	#light_vect=light_vect.dot(orientation_camera["rotation_matrix"].T)
	if(True):#frame_id % 8 <4):
		pass
		light.position((light_vect[0],light_vect[1],light_vect[2]))
		#light.color((1.0,0.0,0.0))
		#pi3d.Light(lightpos=(light_vect[0],light_vect[1],light_vect[2]),lightcol=(0.75,0.75,0.45), lightamb=(0.1,0.1,0.42),is_point=False)
		#print("light 1")
	else:
		light.position((-10,10,-7))
		#light.color((10.0,10.0,10.0))
		#pi3d.Light(lightpos=(-10,10,-7),lightcol=(0.75,0.75,0.45), lightamb=(0.1,0.1,0.42),is_point=False)
		#print("light 2")
	if(time_elapsed<2):
		#print(segment)
		pass
	#print(camera_position)
	camera.reset()
	camera.position(position_camera)
	camera.rotate(xyz_degrees[0],xyz_degrees[1],xyz_degrees[2])
	#camera.rotate(orientation_camera["x_rot"],orientation_camera["y_rot"],orientation_camera["z_rot"])
	
	pod.position(position_target[0],position_target[1],position_target[2])
	pod.rotateToX(orientation_target["x_rot"])
	pod.rotateToY(orientation_target["y_rot"])
	pod.rotateToZ(orientation_target["z_rot"])
	pod.set_light(light)
	pod.draw()
	
	for ring in ring_list:
		ring.set_light(light)
		ring.draw()
		
	#sphere.draw()
	
	#pod position update
	pod_target=np.array([0,0])
	is_x=False
	is_y=False
	if(k==ord('a')):
		pod_target[0]=-1
		is_x=True
	if(k==ord('d')):
		pod_target[0]=1
		is_x=True
	if(k==ord('w')):
		pod_target[1]=1
		is_y=True
	if(k==ord('s')):
		pod_target[1]=-1
		is_y=True
	delta_pod=pod_target*POD_DISTANCE_PER_SECOND*delta_time*(0.707 if (is_x and is_y) else 1.0)
	pod_pos=np.array([pod_x,pod_y])+delta_pod
	scale=np.linalg.norm(pod_pos)
	if(scale>MAX_POD_DISPLACEMENT):
		pod_pos=pod_pos*MAX_POD_DISPLACEMENT/scale
	pod_x=pod_pos[0]
	pod_y=pod_pos[1]
	
	#escape exit
	if k==27:
		keys.close()
		display.destroy()
		break

#print("ring_list len: "+str(len(ring_list)))
#for ring in ring_list:
#	print("ring: "+str([ring.x(),ring.y(),ring.z()]))
#print("x_coeff",segment["x_coeff"])
#print("y_coeff",segment["y_coeff"])
#print("z_coeff",segment["z_coeff"])
