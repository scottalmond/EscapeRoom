# python3 /home/pi/Documents/EscapeRoom/testing/test24_global_reference_frame_and_camera_motion.py 
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
RINGS_PER_SECOND=1.0 #how many rings per second the player passes through
DISTANCE_BETWEEN_RINGS=20.0 #Pi3D units of distance between rings
RING_ROTATION_DEGREES_PER_SECOND=30
ALPHA=2.6 #a lower value alpha means the pod "cuts the corners" when moving through a ring
# a high alpha means the pod is lined up the next ring long before going through it (or overshoots the alignment)
MAX_POD_DISPLACEMENT=2.8 #maximum distance the pod can be from the center of the playfield
POD_DISTANCE_PER_SECOND=7.0 #rate of pod moveemnt per second

prevX_random=[random.random()]
prevY_random=[random.random()]

#a subassembly consists of ring center, ring itself, and any asteroids within ring
def instantiateRingSubassembly():
	ring_subassembly=ring_subassembly_template.shallow_clone()
	nextX_random=random.random()
	nextY_random=random.random()
	prev_mix_ratio=0.1
	rotX=((prevX_random[0]*prev_mix_ratio+nextX_random*(1-prev_mix_ratio))-0.5)*10.0*2
	rotY=((prevY_random[0]*prev_mix_ratio+nextY_random*(1-prev_mix_ratio))-0.5)*40.0*2
	prevX_random[0]=prevX_random[0]*prev_mix_ratio+nextX_random*(1-prev_mix_ratio)
	prevY_random[0]=prevY_random[0]*prev_mix_ratio+nextY_random*(1-prev_mix_ratio)
	#model the motion between consecutive rings as a vector following a cubic function of time
	#first ring (v_1) is at origin, second ring (v_0) is z_0 forward, then
	# another z_0 forward, but after a x-axis and y-axis rotation
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
	#for t between 0.0 and 1.0
	#v(t) = a*t^3 + b*t^2 + c*t + d
	
	posZ=DISTANCE_BETWEEN_RINGS #legacy
	ring_subassembly.positionX(v_0[0]) #distance between rings
	ring_subassembly.positionY(v_0[1]) #distance between rings
	ring_subassembly.positionZ(v_0[2]) #distance between rings
	ring_subassembly.rotateIncX(-rotX) #rotation between sequential rings
	ring_subassembly.rotateIncY(-rotY)
	ring=ring_template.shallow_clone()
	ring.children=[]
	ring_subassembly.children=[ring] #add_child will add children to all shallow_cloned objects (?) resulting in a recursion depth overflow error
	
	#add asteroids
	num_asteroids=int(random.random()*4)
	asteroid_list=[]
	asteroid_displacement=4.0
	for asteroid_id in range(num_asteroids):
		x_val=asteroid_displacement if asteroid_id%2==0 else 0
		y_val=asteroid_displacement if asteroid_id%2==1 else 0
		if(asteroid_id>=2):
			x_val=-x_val
			y_val=-y_val
		asteroid=asteroid_template.shallow_clone()
		asteroid.positionX(x_val)
		asteroid.positionY(y_val)
		asteroid.rotateToX(random.random()*360)
		asteroid.rotateToY(random.random()*360)
		asteroid.rotateToZ(random.random()*360)
		#ring_subassembly.add_child(asteroid)
		#ring.children.append(asteroid)
#		ring.add_child(asteroid) #hide for now to help debugging other issues
		
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
#shader = pi3d.Shader('uv_bump')
print("-- light")
#pi3d.Light()
#print("lightpos: "+str(pi3d.Light.lightpos))
#print("lightcol: "+str(pi3d.Light.lightcol))
#print("lightamb: "+str(pi3d.Light.lightamb))
#print("is_point: "+str(pi3d.Light.is_point))
#pi3d.Light(lightpos=(-100,100,-100),lightcol=(1.0,1.0,0.8), lightamb=(0.25,0.2,0.3))
#pi3d.Light(lightpos=(10,-10,-10),lightcol=(0.7,0.7,0.0), lightamb=(0.1,0.1,0.5),is_point=False)
pi3d.Light(lightpos=(10,-10,-7),lightcol=(0.75,0.75,0.45), lightamb=(0.1,0.1,0.42),is_point=False)
light_scale=850
light_dist=0.5
ambient=(0.02,0.02,0.15)
#pi3d.Light(lightpos=(-40*light_dist,30*light_dist,-40*light_dist),lightcol=(1.0*light_scale,1.0*light_scale,0.7*light_scale), lightamb=ambient,is_point=True)
#pi3d.Light(lightpos=(-40*light_dist,30*light_dist,-40*light_dist),lightcol=(1.0*light_scale,1.0*light_scale,0.7*light_scale), lightamb=ambient,is_point=True)

#generate reference frames
scene=pi3d.Triangle(corners=((0,0),(1,1),(-1,1)))
pod_subassembly = pi3d.Triangle(corners=((0,0),(1,1),(-1,1)))
ring_subassembly_template = pi3d.Triangle(corners=((0,0),(1,1),(-1,1)))

# rings
ring_list=[]
ring_template = pi3d.Model(file_string=MODEL_PATH+'straight_ring_1.obj')
ring_template.set_shader(shader)
ring_template.set_fog((0.0, 0.0, 0.0, 0.0), 130.8)
# is there a way to getHeight (z dimension) of a Shape in Pi3D...?

#pod
pod = pi3d.Model(file_string=MODEL_PATH+'pod_2.obj', z=0.0)
#print("pod model dims: "+str(pod.w())+", "+str(pod.h())+", "+str(pod.d()))
pod_scale=0.33
pod.scale(pod_scale,pod_scale,pod_scale)
#print("pod scale dims: "+str(pod.w())+", "+str(pod.h())+", "+str(pod.d()))
laser_base = pi3d.Model(file_string=MODEL_PATH+'laser_base_2.obj', y=3.15)
laser_gun = pi3d.Model(file_string=MODEL_PATH+'laser_gun_2.obj', y=0.4, z=-0.4)
laser_base.add_child(laser_gun)
pod.add_child(laser_base)
pod.set_shader(shader) # all use uv_light shader
scene.add_child(pod)

#asteroid
asteroid_scale=0.55
asteroid_template = pi3d.Model(file_string=MODEL_PATH+'asteroid_large_1.obj',sx=asteroid_scale,sy=asteroid_scale,sz=asteroid_scale)
asteroid_template.set_shader(shader)
#asteroid_template.set_fog((0.0, 0.0, 0.0, 0.0), 300.6)

#apriori ring subassemblies
pushRingSubassembly()
pushRingSubassembly()
pushRingSubassembly()
pushRingSubassembly()
pushRingSubassembly()
pushRingSubassembly()
pushRingSubassembly()
print("ring_list: "+str(len(ring_list)))
#popRingSubassembly()

scene.draw() #populate children rotation matrices (MRaw) relative to origin
global_list=[]
for ring_assembly_id in range(len(ring_list)):
	ring_assembly=ring_list[ring_assembly_id]
	#print(ring_assembly[0].MRaw)
	#print(np.dot(ring_assembly[0].MRaw.T,np.array([0,0,0,1])))
	MRaw=ring_assembly[0].MRaw
	print("Ring: "+str(ring_assembly_id))
	print("-- pos: "+str(MRaw[3]))
	global_ring=ring_template.shallow_clone()
	#global_ring.scale(0.95,0.95,1.05)
	global_list.append(global_ring)
	global_ring.position(ring_assembly[0].MRaw[3][0],ring_assembly[0].MRaw[3][1],ring_assembly[0].MRaw[3][2])
	xyz_angles_deg=pi3d.Camera.euler_angles(None,MRaw)
	xyz_angles_deg=[x for x in xyz_angles_deg] #convert tuple to array
	xyz_angles_deg[0]=-xyz_angles_deg[0] #because reasons (idk), ref. v2.23 Shape.rotate_to_direction() which does the same
	xyz_angles_deg[1]=-xyz_angles_deg[1]
	print("-- rot1: "+str(np.array([ring_assembly[2],ring_assembly[3],0])))
	print("-- rot2: "+str(xyz_angles_deg))
	global_ring.rotateToX(-xyz_angles_deg[0])
	global_ring.rotateToY(-xyz_angles_deg[1])
	global_ring.rotateToZ(xyz_angles_deg[2])

keys = pi3d.Keyboard()

time_elapsed=0
previous_time=time.time()
previous_ring_pass=0
previous_ring_subassembly=(ring_list[0][0],20,0,0)#model, posZ, rotX, rotY

poped_ring=0
print_burst=0

CAM_RATE=50

while display.loop_running():
	cam_angle=(time.time()*CAM_RATE)%360
	camera.reset()
	camera.position((0,0,-10))
	#camera.position((200*math.cos(math.radians(cam_angle)),0,150+200*math.sin(math.radians(cam_angle))))
	#camera.rotate(0,cam_angle+90,0)
	#camera.rotate(-pod.y(),-3*pod.x(),0)
	
	scene.draw()
	for this_ring in global_list:
		pass#this_ring.draw()
	
	delta_time=time.time()-previous_time #time between frames
	time_elapsed+=delta_time #total time elapsed
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
	#else: #somewhere between consecutive rings, update partial motion state
	if(True):
		but_pt, aim_vec = ring_list[0][0].transform_direction([0.0, 0.0, -1.0],
															  [0.0, 0.0,  0.0])
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
			#print(ring_ratio_remaining)
			print_burst+=1
		raised_cos_redux2=0.5+0.5*math.cos(3.1415*(ring_ratio_remaining-flat_region)/(1-2*flat_region)) #defiend for [flat_region,1-flat_region]
		rot_progress=1 if ring_ratio_remaining<=flat_region else 0 if ring_ratio_remaining>=(1-flat_region) else pow(raised_cos_redux2,1.2) #cos^pow drives how 'snappy' the camera movement about the corner is
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
	
	#ring_template.draw()
	for ring_assembly in ring_list:
		ring_assembly[0].children[0].rotateToZ(time_elapsed*RING_ROTATION_DEGREES_PER_SECOND+(ring_assembly[2]+ring_assembly[3])*100)
		for asteroid in ring_assembly[0].children[0].children:
			asteroid.rotateIncZ(0.5)
			asteroid.rotateIncX(0.17)
			asteroid.rotateIncY(0.13)
	#	ring_assembly.draw()

	#if last ring in list is visible, add another one
	
	
	#if first ring in list is not visible, remove
	
	
	buttons=[]
	k=0
	while k>=0:
		k = keys.read()
		buttons.append(k)
	k=max(buttons)
	
	pod_target=np.array([0,0])
	is_x=False
	is_y=False
	a_pressed=False
	if(k==ord('a')):
		pod_target[0]=-1
		is_x=True
		a_pressed=True
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
	pod_pos=np.array([pod.x(),pod.y()])+delta_pod
	scale=np.linalg.norm(pod_pos)
	if(scale>MAX_POD_DISPLACEMENT):
		pod_pos=pod_pos*MAX_POD_DISPLACEMENT/scale
	pod.positionX(pod_pos[0])
	pod.positionY(pod_pos[1])

	if(400<print_burst<300):
		print(buttons)
	print_burst+=1
	
	#camera.reset()
	#camera.position((0,0,-10))
	#camera.position((0,-100,0))
	#camera.rotate(90,0,0)
	#camera.rotate(-pod.y(),-3*pod.x(),0)
	
	if k==27:
		keys.close()
		display.destroy()
		break
	
		
	#print("hello world: "+str(len(scene.children[0].children)))
	#print("hello world: "+str(len(ring_list)))
	#print("hello world")
