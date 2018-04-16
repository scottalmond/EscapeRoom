from Segment import Segment
from AssetLibrary import AssetLibrary
from RingAssembly import RingAssembly
from Curve import Curve

import sys
import sys
sys.path.insert(1,'/home/pi/pi3d') # to use local 'develop' branch version
import pi3d
import numpy as np
import math
import random
import time

random.seed(0) #desire predicable results so it's possible to reproduce any visual anomalies seen

MAX_POD_DISPLACEMENT=3.7 #2.8 #maximum distance the pod can be from the center of the playfield
POD_TRANSLATION_PER_SECOND=10.0 #rate of pod movement per second

#playfield
display = pi3d.Display.create(background=(0.0, 0.0, 0.0, 0.0))
camera = pi3d.Camera()
light=pi3d.Light(lightpos=(10,-10,-7),lightcol=(0.75,0.75,0.45), lightamb=(0.1,0.1,0.42),is_point=False)
keys = pi3d.Keyboard()

#objects
asset_library=AssetLibrary()
pod=asset_library.pod.shallow_clone() #note: all children remain intact

#variables
frame_id=0	
previous_time=time.time()
time_elapsed=0
pod_x=0 #temp, should be in Pod class
pod_y=0
last_key=-1

ring_counts=[5,10,8]
segment_1=Segment(asset_library,False,np.array([0,0,0]),np.identity(3),0,
	120,60,ring_counts[0])
segment_1_out=segment_1.getEndPoints()[0]
for ring_id in range(ring_counts[0]):
	u=ring_id/ring_counts[0]
	segment_1.addRingAssembly(asset_library,u,ring_rotation_rate=RingAssembly.RING_ROTATION_DEGREES_PER_SECOND)
	
is_branch=True
segment_2=Segment(asset_library,is_branch,segment_1_out["position"],
	segment_1_out["rotation_matrix"],segment_1_out["timestamp_seconds"],
	200,330,ring_counts[1])
segment_2_out=segment_2.getEndPoints()[0]
if(not is_branch):
	for ring_id in range(ring_counts[1]):
		u=ring_id/ring_counts[1]
		segment_2.addRingAssembly(asset_library,u,ring_rotation_rate=RingAssembly.RING_ROTATION_DEGREES_PER_SECOND)

segment_3=Segment(asset_library,False,segment_2_out["position"],
	segment_2_out["rotation_matrix"],segment_2_out["timestamp_seconds"],
	90,90,ring_counts[2])
segment_3_out=segment_3.getEndPoints()[0]
for ring_id in range(ring_counts[2]):
	u=ring_id/ring_counts[2]
	segment_3.addRingAssembly(asset_library,u,ring_rotation_rate=RingAssembly.RING_ROTATION_DEGREES_PER_SECOND)

#raise AssertionError("stop")

while display.loop_running():
	#housekeeping
	frame_id+=1
	#restart motion at end of segments
	if(time_elapsed>segment_3_out["timestamp_seconds"]):
	#if(time_elapsed>segment_2_out["timestamp_seconds"]):
		time_elapsed=0
		previous_time=time.time()
		previous_time=time.time()
	this_timestamp=time.time()
	delta_time=this_timestamp-previous_time
	time_elapsed+=delta_time
	previous_time=this_timestamp
	
	#pod
	
	if(segment_1.isValidTime(time_elapsed)):
		target_orientation=segment_1.getOrientationAtTime(time_elapsed)
	elif(segment_2.isValidTime(time_elapsed)):
		target_orientation=segment_2.getOrientationAtTime(time_elapsed)
	else:
		target_orientation=segment_3.getOrientationAtTime(time_elapsed)
	
	position_target=target_orientation["position"]
	x_axis=target_orientation["rotation_matrix"][0,:]
	y_axis=target_orientation["rotation_matrix"][1,:]
	position_target+=x_axis*pod_x
	position_target+=y_axis*pod_y
	
	pod.position(position_target[0],position_target[1],position_target[2])
	pod.rotateToX(target_orientation["rotation_euler"][0])
	pod.rotateToY(target_orientation["rotation_euler"][1])
	pod.rotateToZ(target_orientation["rotation_euler"][2])
	
	#camera
	camera.reset()
	
	CAMERA_DELAY_SECONDS=0.5
	
	if(segment_1.isValidTime(time_elapsed-CAMERA_DELAY_SECONDS) or segment_1.isValidTime(time_elapsed)):
		camera_orientation=segment_1.getOrientationAtTime(time_elapsed-CAMERA_DELAY_SECONDS)
	#else:
	elif(segment_2.isValidTime(time_elapsed-CAMERA_DELAY_SECONDS)):
		camera_orientation=segment_2.getOrientationAtTime(time_elapsed-CAMERA_DELAY_SECONDS)
	else:
		camera_orientation=segment_3.getOrientationAtTime(time_elapsed-CAMERA_DELAY_SECONDS)
	
	x_axis=camera_orientation["rotation_matrix"][0,:]
	y_axis=camera_orientation["rotation_matrix"][1,:]
	position_camera=camera_orientation["position"]
	camera_movement_scale=0.4
	position_camera+=x_axis*pod_x*camera_movement_scale
	position_camera+=y_axis*pod_y*camera_movement_scale
	
	camera_orientation_to_target=Curve.euler_angles_from_vectors(position_target-position_camera,'z',y_axis,'y')
	
	camera.position(camera_orientation["position"])
	cam_XYZ=camera_orientation_to_target["rotation_euler"]
	camera.rotate(cam_XYZ[0],cam_XYZ[1],cam_XYZ[2])
	
	cam_mtx=camera_orientation_to_target["rotation_matrix"]
	light_vect=np.array([10,-10,7])
	light_vect = np.dot(cam_mtx, light_vect) * [1.0, 1.0, -1.0] #https://github.com/tipam/pi3d/issues/220
	light.position((light_vect[0],light_vect[1],light_vect[2]))
	
	segment_1.update(time_elapsed,light)
	segment_2.update(time_elapsed,light)
	segment_3.update(time_elapsed,light)
	pod.set_light(light)
	
	segment_1.draw()
	segment_2.draw()
	segment_3.draw()
	pod.draw()
	
	#user input
	buttons=[]
	k=0
	while k>=0:
		k = keys.read()
		buttons.append(k)
	k=max(buttons)
	last_key=k
	k=max(k,last_key)
	
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
	delta_pod=pod_target*POD_TRANSLATION_PER_SECOND*delta_time*(0.707 if (is_x and is_y) else 1.0)
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
