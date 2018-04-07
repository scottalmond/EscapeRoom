import sys
sys.path.insert(1,'/home/pi/pi3d') # to use local 'develop' branch version
import pi3d
import numpy as np
import math
import random
import time

random.seed(0) #desire predicable results so it's possible to reproduce any visual anomalies seen

MODEL_PATH = 'models/'
RINGS_PER_SECOND=0.5 #how many rings per second the player passes through

#a subassembly consists of ring center, ring itself, and any asteroids within ring
def instantiateRingSubassembly():
	ring_subassembly=ring_subassembly_template.shallow_clone()
	ring_subassembly.positionZ(20.0) #distance between rings
	ring_subassembly.rotateIncX(random.random()*40.0)#-20.0) #rotation between sequential rings
	ring_subassembly.rotateIncY(random.random()*40.0)#-20.0)
	ring=ring_template.shallow_clone()
	#TODO: asteroids here
	ring_subassembly.children=[ring] #add_child will add children to all shallow_cloned objects (?) resulting in a recursion depth overflow error
	return ring_subassembly

#add a new ring subsassembly at the end of the path
def pushRingSubassembly():
	if(len(ring_list)==0):
		previous_ring_subassembly=instantiateRingSubassembly()
		ring_list.append(previous_ring_subassembly)
		#scene.add_child(ring_list[0])
	else:
		previous_ring_subassembly=ring_list[-1]
	new_ring_subassembly=instantiateRingSubassembly()
	previous_ring_subassembly.add_child(new_ring_subassembly)
	previous_ring_subassembly.draw() #need to generate MRaw
	previous_ring_position,previous_ring_rotation=previous_ring_subassembly.transform_direction([0.0,0.0,20.0])
	previous_ring_subassembly.children.remove(new_ring_subassembly)
	new_ring_subassembly.rotate_to_direction(previous_ring_rotation)
	new_ring_subassembly.position(*(previous_ring_position + previous_ring_rotation*0.0))
	ring_list.append(new_ring_subassembly)
	#scene.add_child(new_ring_subassembly)
	
#remove the ring asembly closest to the camera and return it
def popRingSubassembly():
	print("ring_list 2: "+str(len(ring_list)))
	poped_ring_assembly=ring_list.pop(0)
	#scene.children.remove(poped_ring_assembly)
	#scene.add_child(ring_list[0])
	return poped_ring_assembly
	
#when the first ring is far enoguh back, delete it
#def advanceThroughRing():
	
	
#objective:
# position ring subassemblies in global reference frame (but first in relation to each other)
# position pod subassembly in global reference frame (but first in relation to ring subassemblies)
# position camera in global reference frame (maintain in relation to ...)

#RINGS_PER_SECOND=0.5 #number of rings the pod passes through per second
# the number of frames/updates is non-deterministic based on render speed

display = pi3d.Display.create(background=(0.0, 0.0, 0.0, 0.0))
camera = pi3d.Camera()
shader = pi3d.Shader('uv_light')

#generate reference frames
scene=pi3d.Triangle(corners=((0,0),(1,1),(-1,1)))
pod_subassembly = pi3d.Triangle(corners=((0,0),(1,1),(-1,1)))
ring_subassembly_template = pi3d.Triangle(corners=((0,0),(1,1),(-1,1)))

# rings
ring_list=[]
ring_template = pi3d.Model(file_string=MODEL_PATH+'straight_ring_1.obj')
ring_template.set_shader(shader)
# is there a way to getHeight (z dimension) of a Shape in Pi3D...?

#apriori ring subassemblies
pushRingSubassembly()
pushRingSubassembly()
pushRingSubassembly()
pushRingSubassembly()
print("ring_list: "+str(len(ring_list)))
#popRingSubassembly()

keys = pi3d.Keyboard()

time_elapsed=0
previous_time=time.time()
previous_ring_pass=0

poped_ring=False

while display.loop_running():
	time_elapsed+=time.time()-previous_time
	previous_time=time.time()
	
	if(time_elapsed>4 and not poped_ring):
		popRingSubassembly()
		poped_ring=True
	
	#pod_frame.draw()
	
	camera.reset()
	camera.position((0,0,-40))
	
	#ring_template.draw()
	scene.draw()
	for ring_assembly in ring_list:
		ring_assembly.draw()

	#if last ring in list is visible, add another one
	
	
	#if first ring in list is not visible, remove
	
	
	k = keys.read()
	if k==27:
		keys.close()
		display.destroy()
		break
	#print("hello world: "+str(len(scene.children[0].children)))
	print("hello world: "+str(len(ring_list)))
	#print("hello world")
