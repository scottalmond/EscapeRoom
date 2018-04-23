# python3 /home/pi/Documents/EscapeRoom/testing/test25_smooth_camera_motion.py 
import sys
import sys
sys.path.insert(1,'/home/pi/pi3d') # to use local 'develop' branch version
import pi3d
import numpy as np
import math
import random
import time

#definitions:
#NodeConnection is comprised of multiple sequential (and/or branching) Segments
#A Segment is either one Curve (normal) or three Curves (used to build a branch)
#A Curve consists of one Path and some number of rings and obstacles
#A Path is parameterized curve through 3-space

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
# triangle
node_template=pi3d.Triangle(corners=((0,0),(.001,.001),(-.001,.001)))

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

#variables
segment_list=[]
ring_list=[]
frame_id=0	
previous_time=time.time()
time_elapsed=0

#a segment normally consists of one curve, but for branches there are three
# one for the brnached ring location, and two for the path choices
def getNextPath(this_path_id,is_forward_path,
				start_time,start_position,start_rotation_matrix):
	is_branch=False
	if(this_path_id%5==2):
		is_branch=True
		
	curves=[]
	if(is_branch):
		
	else:
		#fetch parameters for curve here given the path_id and is_forward_path
		
		
		
	chosen_path=0 #chosen direction, either 1 for left or 2 for right
	output={"id":this_path_id,
			"is_branch":is_branch,
			"curves":curves,
			"chosen_path":chosen_path
			}
	return output

#define segments based on start node, end node
# curves have rings on them
#ring_definition is a list of rings to place on the curve
# may be None to signify no ring to exist, but leave space free along curve
def getCurveByID(this_curve_id,start_time,ring_definition):
	ring_count=len(ring_definition)
	distance=ring_count*DISTANCE_BETWEEN_RINGS
	ring_list=[]
	
#get the coeffs used to define a circular arc
#input:
# start_time_seconds of Path (passed directly to output and not otherwise used)
# start_position is the u=0 position in the Path (passed directly to
#  output and not otherwise used)
# start_rotation_matrix is the rotation matrix of the Path at u=0 (passed
#  directly to output and not otherwise used)
# duration_seconds of Path in seconds (passed directly to output and not otherwise used)
# distance is arc length in Pi3d distance units
# curvature_degrees is number of degrees of arc: 0 degrees is a straight line (TODO: fix div zero error),
#  90 degrees turns the input motion into perpendicular motion
# orientation_degrees is the z-axis rotation: 0 degrees is right, 90 degrees is up, 180 to the left, 270 down
#output:
# coeffients (3 element np.array) for a parameterized segment of the form:
#  position(u)=[cos(u*2*np.pi)*x_coeff,cos(u*2*np.pi)*y_coeff,sin(u*2*np.pi)*z_coeff]
#  where u is valid from 0 (start of arc) to 1 (end of arc)
# normal (3 element np.array): an x,y,z vector representing the axis of rotation of the Path from start to finish
def getPath(start_time_seconds,start_position,start_rotation_matrix,
			duration_seconds,distance,curvature_degrees,orientation_degrees):
	if(math.abs(curvature_degrees)<0.0001): curvature_degrees=0.0001 #lower limit to approx stright line (easier than making special case for a line)
	arc_length=2*np.pi*curvature_degrees/360 #compute an initial estimate of arc length
	unit_scale=distance/arc_length #scale the initial curve computation to be the specified length
	orientation_radians=orientation_degrees*np.pi/180
	curvature_radians=curvature_degrees*np.pi/180
	x_coeff=np.cos(-orientation_radians)*unit_scale
	y_coeff=-np.sin(-orientation_radians)*unit_scale
	z_coeff=-unit_scale
	coeff=np.array([x_coeff,y_coeff,z_coeff])
	x_norm=math.sin(orientation_radians)#axis representing a vector normal to the axis of curvature rotation
	y_norm=-math.cos(orientation_radians)
	z_norm=0
	normal=np.array([x_norm,y_norm,z_norm])
	output={"start_time_seconds":start_time_seconds,
		    "start_rotation_matrix":start_rotation_matrix,
		    "start_position":start_position,
		    "duration_seconds":duration_seconds,
		    "distance":distance,
		    "curvature_degrees":curvature_degrees,
		    "curvature_radians":curvature_radians,
		    "orientation_degrees":orientation_degrees,
		    "orientation_radians":orientation_radians,
		    "coeff":coeff,
		    "normal":normal
		   }
	return output

def getOrientationAlongCurve(curve,u):
	#angles
	curvature_degrees=segment["curvature_degrees"]
	curvature_radians=segment["curvature_radians"]
	orientation_radians=segment["orientation_radians"]
	#position
	x_coeff=curve["coeff"][0]
	y_coeff=curve["coeff"][1]
	z_coeff=curve["coeff"][2]
	v=u*curvature_degrees/360 #scale to fraction of full circle
	x_2d=-np.cos(v*2*np.pi)+1
	x_pos=x_2d*x_coeff
	y_pos=x_2d*y_coeff
	z_pos=-np.sin(v*2*np.pi)*z_coeff
	position=np.array([x_pos,y_pos,z_pos])
	#rotation
	theta=curvature_radians*u
	r_hat=segment["normal"]
	rotation_matrix=getRotationMatrixAboutVector(r_hat,theta)
	euler=camera.euler_angles(rotation_matrix) #degrees
	output={"position":position,
			"rotation_euler":euler, #X, Y, Z, degrees
			"rotation_matrix":rotation_matrix}

#input:

#output:
# locked_hemisphere= 0 for unlocked, 1 for left, 2 for right
def getOrientationAlongNodeConnection(elapsed_time_seconds,segment_list):
	for segment_id in range(len(segment_list)):
		pass
	
	

#if the segment_list is not long enough, extend it
#if there are elements of the segment_list no longer needed, delete them
def updateSegmentBuffer(elapsed_time):
	if(len(segment_list)==0):
		start_rotation_matrix=np.identity(3)
		start_position=np.array([0,0,0])
		start_time=0
		this_segment_id=0
		next_segment_id=1
	else:
		pass
		
