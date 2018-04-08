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
RINGS_PER_SECOND=0.5 #how many rings per second the player passes through
DISTANCE_BETWEEN_RINGS=45.0 #Pi3D units of distance between rings
RING_ROTATION_DEGREES_PER_SECOND=30
ALPHA=2.6 #a lower alpha means the pod "cuts the corners" when moving through a ring
# a high alpha means the pod is lined up the next ring long before going through it (or overshoots the alignment)

prevX_random=[random.random()]
prevY_random=[random.random()]

#a subassembly consists of ring center, ring itself, and any asteroids within ring
def instantiateRingSubassembly():
	ring_subassembly=ring_subassembly_template.shallow_clone()
	nextX_random=random.random()
	nextY_random=random.random()
	prev_mix_ratio=0.05
	rotX=((prevX_random[0]*prev_mix_ratio+nextX_random*(1-prev_mix_ratio))-0.5)*20.0
	rotY=((prevY_random[0]*prev_mix_ratio+nextY_random*(1-prev_mix_ratio))-0.5)*20.0
	prevX_random[0]=prevX_random[0]*prev_mix_ratio+nextX_random*(1-prev_mix_ratio)
	prevY_random[0]=prevY_random[0]*prev_mix_ratio+nextY_random*(1-prev_mix_ratio)
	z_0=DISTANCE_BETWEEN_RINGS/2.0
	c_x=math.cos(math.radians(rotX))
	s_x=math.sin(math.radians(rotX))
	c_y=math.cos(math.radians(rotY))
	s_y=math.sin(math.radians(rotY))
	v_0=np.array([-z_0*c_x*s_y,z_0*s_x,z_0+z_0*c_x*c_y])
	v_0_prime=np.array([ALPHA*z_0*c_x*s_y,-ALPHA*z_0*s_x,-ALPHA*z_0*c_x*c_y])
	v_1=np.array([0,0,0])
	v_1_prime=np.array([0,0,-ALPHA*z_0])
	a=2*v_0-2*v_1+v_0_prime+v_1_prime
	b=-3*v_0+3*v_1-2*v_0_prime-v_1_prime
	c=v_0_prime
	d=v_0
	
	posZ=DISTANCE_BETWEEN_RINGS #legacy
	ring_subassembly.positionX(v_0[0]) #distance between rings
	ring_subassembly.positionY(v_0[1]) #distance between rings
	ring_subassembly.positionZ(v_0[2]) #distance between rings
	ring_subassembly.rotateIncX(-rotX) #rotation between sequential rings
	ring_subassembly.rotateIncY(-rotY)
	ring=ring_template.shallow_clone()
	#TODO: asteroids here
	ring_subassembly.children=[ring] #add_child will add children to all shallow_cloned objects (?) resulting in a recursion depth overflow error
	return (ring_subassembly,posZ,rotX,rotY,a,b,c,d)

#add a new ring subsassembly at the end of the path
def pushRingSubassembly():
	if(len(ring_list)==0):
		previous_ring_subassembly=instantiateRingSubassembly()
		ring_list.append(previous_ring_subassembly)
		scene.add_child(ring_list[0][0])
	else:
		previous_ring_subassembly=ring_list[-1]
	new_ring_subassembly=instantiateRingSubassembly()
	previous_ring_subassembly[0].add_child(new_ring_subassembly[0])
	#previous_ring_subassembly.draw() #need to generate MRaw
	#previous_ring_position,previous_ring_rotation=previous_ring_subassembly.transform_direction([0.0,0.0,20.0])
	#previous_ring_subassembly.children.remove(new_ring_subassembly)
	#new_ring_subassembly.rotate_to_direction(previous_ring_rotation)
	#new_ring_subassembly.position(*(previous_ring_position + previous_ring_rotation*0.0))
	ring_list.append(new_ring_subassembly)
	#scene.add_child(new_ring_subassembly)
	
#remove the ring asembly closest to the camera and return it
def popRingSubassembly():
	#print("ring_list 2: "+str(len(ring_list)))
	poped_ring_assembly=ring_list.pop(0)
	scene.children.remove(poped_ring_assembly[0])
	scene.add_child(ring_list[0][0])
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
previous_ring_subassembly=(ring_list[0][0],20,0,0)#model, posZ, rotX, rotY

poped_ring=0
print_burst=0

while display.loop_running():
	scene.draw()
	time_elapsed+=time.time()-previous_time
	previous_time=time.time()
	
	ring_time=(time_elapsed-previous_ring_pass) #time spent with this ring
	ring_ratio_remaining=ring_time*RINGS_PER_SECOND #seconds * Hz = ratio of ring elapsed
	
	if(ring_ratio_remaining>=1): #if trying to advance beyond current ring, update environemnt accordingly
	#if(time_elapsed>4 and not poped_ring):
		previous_ring_subassembly=popRingSubassembly()
		pushRingSubassembly()
		#poped_ring=True
		previous_ring_pass=time_elapsed
		
	ring_time=(time_elapsed-previous_ring_pass) #time spent with this ring
	ring_ratio_remaining=ring_time*RINGS_PER_SECOND #seconds * Hz = ratio of ring elapsed
	ring_ratio_elapsed=1-ring_ratio_remaining
	#else: #somewhere between consecutive rings, update partial motion state accordingly
	if(True):
		but_pt, aim_vec = ring_list[0][0].transform_direction([0.0, 0.0, -1.0],
															  [0.0, 0.0,  0.0])
		if(time_elapsed>poped_ring+0.9):
			print("but_pt: "+str(but_pt))
			poped_ring=time_elapsed
		rotX_prev=ring_ratio_remaining*previous_ring_subassembly[2]
		rotY_prev=ring_ratio_remaining*previous_ring_subassembly[3]
		posZ_next=ring_ratio_elapsed*ring_list[0][1]
		rotX_next=ring_ratio_elapsed*ring_list[0][2]
		rotY_next=ring_ratio_elapsed*ring_list[0][3]
		posZ=posZ_next
		#ring_ratio_elapsed=0 if ring_ratio_elapsed<0.5 else 1
		#raised_cos=math.cos(ring_ratio_elapsed*3.1415)*.5+.5
		#rotX=rotX_prev*raised_cos+rotX_next*(1-raised_cos)
		#rotY=rotY_prev*raised_cos+rotY_next*(1-raised_cos)
		#rotX=rotX_next*(1-raised_cos*raised_cos)
		#rotY=rotY_next*(1-raised_cos*raised_cos)
		flat_region=0.08 # half the length that the "camera" (closes ring subassembly) remains in a fixed angle
		#raised_cos_redux=0.5-math.cos((ring_ratio_elapsed-flat_region)*3.1415/(1-2*flat_region))*0.5
		#scalar=1 if ring_ratio_elapsed<=flat_region else 0 if ring_ratio_elapsed>=(1-flat_region) else raised_cos_redux
		#rotX=rotX_next*raised_cos_redux
		#rotY=rotY_next*raised_cos_redux
		if(print_burst<100):
			print(ring_ratio_remaining)
			print_burst+=1
		raised_cos_redux2=0.5+0.5*math.cos(3.1415*(ring_ratio_remaining-flat_region)/(1-2*flat_region)) #defiend for [flat_region,1-flat_region]
		rot_progress=1 if ring_ratio_remaining<=flat_region else 0 if ring_ratio_remaining>=(1-flat_region) else pow(raised_cos_redux2,1.5)
		rotX=rotX_next*rot_progress
		rotY=rotY_next*rot_progress
		t=ring_ratio_remaining
		a=ring_list[0][4]
		b=ring_list[0][5]
		c=ring_list[0][6]
		d=ring_list[0][7]
		pos=a*t*t*t+b*t*t+c*t+d
		#ring_list[0][0].positionZ(posZ)
		ring_list[0][0].positionX(pos[0])
		ring_list[0][0].positionY(pos[1])
		ring_list[0][0].positionZ(pos[2])
		ring_list[0][0].rotateToX(-rotX)
		ring_list[0][0].rotateToY(-rotY)
		
	
	#pod_frame.draw()
	
	camera.reset()
	camera.position((0,0,-10))
	
	#ring_template.draw()
	for ring_assembly in ring_list:
		ring_assembly[0].children[0].rotateToZ(time_elapsed*RING_ROTATION_DEGREES_PER_SECOND+(ring_assembly[2]+ring_assembly[3])*100)
	#	ring_assembly.draw()

	#if last ring in list is visible, add another one
	
	
	#if first ring in list is not visible, remove
	
	
	k = keys.read()
	if k==27:
		keys.close()
		display.destroy()
		break
	#print("hello world: "+str(len(scene.children[0].children)))
	#print("hello world: "+str(len(ring_list)))
	#print("hello world")
