from chapters.wall.hyperspace_helper.Segment import Segment
from chapters.wall.hyperspace_helper.AssetLibrary import AssetLibrary
from chapters.wall.hyperspace_helper.RingAssembly import *
from chapters.wall.hyperspace_helper.Curve import Curve

import sys
import sys
#sys.path.insert(1,'/home/pi/pi3d') # to use local 'develop' branch version
#import pi3d
import numpy as np
import math
import random
import time

class SCENE_STATE(Enum):
	INTRO=0 #pod exiting space ship
	OUTRO=1 #pod entering white success
	DEATH=2 #pod entering black death
	PLAY=3 #normal operation (birth and hot controls)

#precon: first segment is id=0 (where to look in file) and is straight
# (ensure camera is lined up with pod after intro sequence)
#strongly advised: last segment before death and outro be straight to allow for extrapolation
#track the status of the pod through the maze
class SceneManager:
	MAX_POD_DISPLACEMENT=3.5 #2.8 #maximum distance the pod can be from the center of the playfield
	# ~4x of Segment.BRANCH_DISPLACEMENT_DISTANCE
	POD_TRANSLATION_PER_SECOND=10.0 #rate of pod movement per second
	POD_ROTATION_DEGREES_PER_SECOND=70.0 #rate of rotation animatic when pod is translating
	POD_MAX_ROTATION=[6.0,12.0] #x-translation, y-translation, degrees
	INTRO_SECONDS=1 #number of seconds to wait on start for cut scene to play
	OUTRO_SECONDS=1
	DEATH_SECONDS=1
	CAMERA_LAG_DISTANCE=12 #pi3d distance unit between camera and pod

	def __init__(self):
		pass
		
	def clean(self,pi3d,display_3d,camera_3d):
		#variables
		self.pi3d=pi3d
		self.pod_offset=np.array([0.0,0.0]) #x,y offset
		self.pod_offset_rate=np.array([0.0,0.0]) #Z,X rotation angles for translation animatic (rotate right to translate right)
		self.scene={'state':SCENE_STATE.INTRO,'start_seconds':0,'end_seconds':self.INTRO_SECONDS,'ratio':0.0}
		self.life=0
		self.level_start_time_seconds=0
		self.segment_list=[]
		self.pod_segment=None
		self.camera_segment=None
		self.last_key=-1 #delete from final program - used for smoothing pi3d keyboard inputs
		
		#playfield
		self.display = display_3d #self.pi3d.Display.create(background=(0.0, 0.0, 0.0, 0.0))
		self.camera = camera_3d #self.pi3d.Camera()
		self.light = self.pi3d.Light(lightpos=(10,-10,-7),lightcol=(0.75,0.75,0.45), lightamb=(0.1,0.1,0.42),is_point=False)
		#self.keys = self.pi3d.Keyboard() #TODO: remove later...
		
		#objects
		self.asset_library=AssetLibrary(self.pi3d)
		self.pod=self.asset_library.pod_frame.shallow_clone() #note: all children remain intact
		
	def __getRingCount(self):
		count=0
		for segment in self.segment_list:
			count+=len(segment.ring_assembly_list)
		return count
		
	#update list of parameterized arcs
	def __updateSegmentQueue(self,level_elapsed_time_seconds):
		#if any segments in list are u<0 for camera (already completely used), then dispose of segment
		#if any segment has no succesor and the [end time - current time] < queue_time_depth
		# then get and append successor
		
		#initialization
		if(len(self.segment_list)==0): 
			segment_joint=self.getSegmentAfter(None)
			first_segment=segment_joint['next_segment'][0]
			self.segment_list.append(first_segment)
			self.pod_segment=first_segment
			self.camera_segment=first_segment
		
		#append segments to end when the end is near
		segment_index=0
		while(segment_index<len(self.segment_list)): #keep adding segments to end when needed
			segment=self.segment_list[segment_index]
			end_time=segment.durationSeconds()+segment.start_time_seconds
			cut_off_time=level_elapsed_time_seconds+RingAssembly.PRE_RENDER_SECONDS
			#if(level_elapsed_time_seconds<7):
			#	print('query: '+str(end_time)+"<"+str(cut_off_time))
			#	print('size: '+str(len(self.segment_list)))
			if(end_time<cut_off_time and segment.hasTraceabilityTo(self.pod_segment)):
				if(segment.is_branch):
					if(segment.successor[1] is None):
						segment_joint=self.getSegmentAfter(segment)
						for itr in range(2):
							seg_id=itr+1
							self.segment_list.append(segment_joint['next_segment'][seg_id])
							segment.successor[seg_id]=segment_joint['next_segment'][seg_id]
							segment_joint['next_segment'][seg_id].predecessor=segment
				else:
					if(segment.successor[0] is None):
						segment_joint=self.getSegmentAfter(segment)
						self.segment_list.append(segment_joint['next_segment'][0])
						segment.successor[0]=segment_joint['next_segment'][0]
						segment_joint['next_segment'][0].predecessor=segment
			segment_index+=1
		
		#remove old segments
		camera_time=self.__getCameraTime(level_elapsed_time_seconds)
		for segment_index in reversed(range(len(self.segment_list))): #traverse backward to allow for deletion
			segment=self.segment_list[segment_index]
			ratio=segment.getRatio(camera_time)
			if(ratio>1):
				if(not segment==self.camera_segment):
					segment=self.segment_list.pop(segment_index) #delete stale segments
					segment.dispose()
	
	#update graphical rotation of rings, derbis, etc
	def __updateSegments(self,level_elapsed_time_seconds):
		for segment in self.segment_list:
			segment.update(level_elapsed_time_seconds,self.light)
			
	#assumes input for 'k' as 4-element bool np.array
	# in the following order: [NORTH,WEST,SOUTH,EAST], where True is an active user input command
	def __updatePodPosition(self,k,delta_time):
		#position
		pod_target=np.array([0,0])
		is_x=False
		is_y=False
		IS_AIRPLANE_CONTROLS=True #True is up joystick means down motion
		#if(k==ord('a')):
			#pod_target[0]=-1
			#is_x=True
		#if(k==ord('d')):
			#pod_target[0]=1
			#is_x=True
		#if(k==ord('s')):
			#pod_target[1]=1
			#is_y=True
		#if(k==ord('w')):
			#pod_target[1]=-1
			#is_y=True
		if(k[1]):
			pod_target[0]=-1
			is_x=True
		if(k[3]):
			pod_target[0]=1
			is_x=True
		if(k[2]):
			if(IS_AIRPLANE_CONTROLS):
				pod_target[1]=-1
			else:
				pod_target[1]=1
			is_y=True
		if(k[0]):
			if(IS_AIRPLANE_CONTROLS):
				pod_target[1]=1
			else:
				pod_target[1]=-1
			is_y=True
		delta_pod=pod_target*self.POD_TRANSLATION_PER_SECOND*delta_time*(0.707 if (is_x and is_y) else 1.0)
		pod_pos=self.pod_offset+delta_pod
		scale=np.linalg.norm(pod_pos)
		if(scale>self.MAX_POD_DISPLACEMENT):
			pod_pos=pod_pos*self.MAX_POD_DISPLACEMENT/scale
		self.pod_offset=pod_pos
		
		#rotation animatic
		x_rate=self.pod_offset_rate[0] #x-translation, Z-rotation
		delta_x=self.POD_ROTATION_DEGREES_PER_SECOND*delta_time
		#if(k==ord('d')):#right
			#delta_x=-delta_x
		#elif(k==ord('a')):#left
			#pass
		if(k[3]):#right
			delta_x=-delta_x
		elif(k[1]):#left
			pass
		else:#neither, return to center
			if(x_rate<0): delta_x=min(-x_rate,delta_x)
			elif(x_rate>0): delta_x=max(-x_rate,-delta_x)
			else: delta_x=0
		self.pod_offset_rate[0]+=delta_x
		
		y_rate=self.pod_offset_rate[1] #y-translation, Y-rotation
		delta_y=self.POD_ROTATION_DEGREES_PER_SECOND*delta_time
		#if(k==ord('s')):#up
			#delta_y=-delta_y
		#elif(k==ord('w')):#down
			#pass
		if(k[0]):#up
			if(IS_AIRPLANE_CONTROLS):
				pass
			else:
				delta_y=-delta_y
		elif(k[2]):#down
			if(IS_AIRPLANE_CONTROLS):
				delta_y=-delta_y
			else:
				pass
		else:#neither, return to center
			if(y_rate<0): delta_y=min(-y_rate,delta_y)
			elif(y_rate>0): delta_y=max(-y_rate,-delta_y)
			else: delta_y=0
		self.pod_offset_rate[1]+=delta_y
		
		for itr in range(2): #bound rotation
			self.pod_offset_rate[itr]=max(self.pod_offset_rate[itr],-self.POD_MAX_ROTATION[itr])
			self.pod_offset_rate[itr]=min(self.pod_offset_rate[itr],self.POD_MAX_ROTATION[itr])
			
	def __updateProps(self,level_elapsed_time_seconds):
		prop_orientation=self.getPropOrientation(level_elapsed_time_seconds)
		
		#light
		light_pos=prop_orientation['light']['position']
		self.light.position((light_pos[0],light_pos[1],light_pos[2]))
		
		#pod
		pod_pos=prop_orientation['pod']['position']
		pod_rot=prop_orientation['pod']['rotation_euler']
		self.pod.children[0].rotateToX(self.pod_offset_rate[1])
		self.pod.children[0].rotateToZ(self.pod_offset_rate[0])
		self.pod.position(pod_pos[0],pod_pos[1],pod_pos[2])
		self.pod.rotateToX(pod_rot[0])
		self.pod.rotateToY(pod_rot[1])
		self.pod.rotateToZ(pod_rot[2])
		self.pod.set_light(self.light)
		#TO DO make recursive set_light method for pod
		self.pod.children[0].set_light(self.light)
		self.pod.children[0].children[0].set_light(self.light)
		self.pod.children[0].children[0].children[0].set_light(self.light)
		
		#camera
		camera_pos=prop_orientation['camera']['position']
		camera_rot=prop_orientation['camera']['rotation_euler']
		self.camera.reset()
		self.camera.position(camera_pos)
#		print("SceneManager.__updateProps: camera_pos:",camera_pos)
		self.camera.rotate(camera_rot[0],camera_rot[1],camera_rot[2])
		
	def __drawSegments(self):
		for segment in self.segment_list:
			segment.draw()
		
	def __updatePodSegment(self,level_elapsed_time_seconds):
		while(self.pod_segment.getRatio(level_elapsed_time_seconds)>1):
			self.pod_segment=self.pod_segment.getSuccessor()
			if(self.pod_segment.is_branch): #when entering a branch, decide which path to take
				is_left=self.pod_offset[0]<0
				self.pod_segment.decideBranch(level_elapsed_time_seconds,is_left)
				#print('is_left: ',self.pod_segment.isLeft())
				
		self.pod_orientation=self.pod_segment.getOrientationAtTime(level_elapsed_time_seconds)
		
	def __updateCameraSegment(self,level_elapsed_time_seconds):
		camera_time=self.__getCameraTime(level_elapsed_time_seconds)
		while(self.camera_segment.getRatio(camera_time)>1):
			self.camera_segment=self.camera_segment.getSuccessor()
		self.camera_orientation=self.camera_segment.getOrientationAtTime(camera_time)
	
	def __getCameraTime(self,level_elapsed_time_seconds):
		camera_lag_time=self.CAMERA_LAG_DISTANCE/(Segment.DISTANCE_BETWEEN_RINGS*Segment.RINGS_PER_SECOND)
		camera_time=level_elapsed_time_seconds-camera_lag_time
		return camera_time
		
	#given a segment ID, return the parameters needed for the next segment
	#input:
	#Segment
	#output:
	#{'previous_segment':Segment,'next_segment':[Segment,Segment,Segment]}
	# where previous_segment is the input
	# and one of the following is True: 'next_segment'[0] is None OR 'next_segment'[1:2] is None
	def getSegmentAfter(self,segment):
		if(segment is None):
			#return first segment
			#TODO load from file
			previous_segment=None
			ring_count=7
			segment=Segment(self.asset_library,False,np.array([0,0,0]),np.identity(3),0,
				120,60,ring_count)
			for ring_id in range(ring_count):
				u=ring_id/ring_count
				segment.addRingAssembly(self.asset_library,u,
					ring_rotation_rate=RingAssembly.RING_ROTATION_DEGREES_PER_SECOND,
					debris_rotation_rate=RingAssembly.DEBRIS_ROTATION_DEGREES_PER_SECOND)
			next_segment=[segment,None,None]
		else:
			#this_segment_id=segment.segment_id
			previous_segment=segment
			ring_count=[2+random.randint(0,3),2+random.randint(0,3)]
			curvature=[random.randint(0,30),random.randint(0,30)]
			orientation=[random.randint(0,360),random.randint(0,360)]
			was_branch=segment.is_branch #input segmenet was a branch
			was_branch2=segment.predecessor is None or segment.predecessor.is_branch
			#print('was_branch: ',was_branch)
			is_branch=[random.randint(0,100)<20,random.randint(0,100)<20] #next segment is a branch
			if(was_branch or was_branch2):
				is_branch=[False,False]
			#is_branch=[False,False]
			end_point=segment.getEndPoints()
			if(was_branch):
				next_segment=[None]
				for itr in range(2):
					this_segment=Segment(self.asset_library,is_branch[itr],end_point[itr]['position'],
						end_point[itr]['rotation_matrix'],end_point[itr]['timestamp_seconds'],
						curvature[itr],orientation[itr],ring_count[itr])
					next_segment.append(this_segment)
					if(not is_branch[itr]):
						for ring_id in range(ring_count[itr]):
							u=ring_id/ring_count[itr]
							this_segment.addRingAssembly(self.asset_library,u,
								ring_rotation_rate=RingAssembly.RING_ROTATION_DEGREES_PER_SECOND,
								debris_rotation_rate=RingAssembly.DEBRIS_ROTATION_DEGREES_PER_SECOND)
			else:
				next_segment=[]
				this_segment=Segment(self.asset_library,is_branch[0],end_point[0]['position'],
					end_point[0]['rotation_matrix'],end_point[0]['timestamp_seconds'],
					curvature[0],orientation[0],ring_count[0])
				next_segment.append(this_segment)
				next_segment.append(None)
				next_segment.append(None)
				if(not is_branch[0]):
					for ring_id in range(ring_count[0]):
						u=ring_id/ring_count[0]
						this_segment.addRingAssembly(self.asset_library,u,
							ring_rotation_rate=RingAssembly.RING_ROTATION_DEGREES_PER_SECOND,
							debris_rotation_rate=RingAssembly.DEBRIS_ROTATION_DEGREES_PER_SECOND)
			#return next segment
		return {'previous_segment':previous_segment,'next_segment':next_segment}
		
	#return the start node, end node, progress and current segment_id
	#return a pointer to the segment where the pod is currently located
	def getPodStatus(self):
		pass
		
	#return the segment where the camera is currently located
	def getCameraStatus(self):
		pass

	#dict with keys:
	# pod
	# camera
	# light
	# sub-keys:
	#  position
	#  rotation_matrix
	#  rotation_euler
	#note: rotations have not been implemented for light
	def getPropOrientation(self,level_elapsed_time_seconds):
		#pod
		pod_orientation=self.pod_segment.getOrientationAtTime(level_elapsed_time_seconds)
		pod_position=pod_orientation["position"]
		x_axis=pod_orientation["rotation_matrix"][0,:]
		y_axis=pod_orientation["rotation_matrix"][1,:]
		pod_position+=x_axis*self.pod_offset[0]
		pod_position+=y_axis*self.pod_offset[1]
		pod_orientation["position"]=pod_position
		
		#camera
		camera_orientation=self.camera_segment.getOrientationAtTime(self.__getCameraTime(level_elapsed_time_seconds))
		x_axis=camera_orientation["rotation_matrix"][0,:]
		y_axis=camera_orientation["rotation_matrix"][1,:]
		position_camera=camera_orientation["position"]
		camera_movement_scale=0.5
		position_camera+=x_axis*self.pod_offset[0]*camera_movement_scale
		position_camera+=y_axis*self.pod_offset[1]*camera_movement_scale
		camera_orientation["position"]=position_camera
		camera_orientation_to_target=Curve.euler_angles_from_vectors(pod_position-position_camera,'z',y_axis,'y')
		camera_orientation["rotation_euler"]=camera_orientation_to_target["rotation_euler"]
		camera_orientation["rotation_matrix"]=camera_orientation_to_target["rotation_matrix"]
		
		#light
		light_vect=np.array([10,-10,7])
		light_vect = np.dot(camera_orientation["rotation_matrix"], light_vect) * [1.0, 1.0, -1.0] #https://github.com/tipam/pi3d/issues/220
		light_orientation={'position':light_vect}
		
		#laser...
		
		return {'pod':pod_orientation,'camera':camera_orientation,'light':light_orientation}

	#assumes inputs for navigation_joystick,camera_joystick,laser_joystick as 4-element bool np.arrays
	# in the following order: [NORTH,WEST,SOUTH,EAST], where True is an active user input command
	def update(self,this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds,packets,
			navigation_joystick,camera_joystick,laser_joystick,is_fire_laser):
		scene_state=self.scene['state']
		level_elapsed_time_seconds=this_frame_elapsed_seconds-self.level_start_time_seconds
		scene_start=self.scene['start_seconds'] #seconds
		scene_end=self.scene['end_seconds']
		delta_time=this_frame_elapsed_seconds-previous_frame_elapsed_seconds #time between frames
		
		#advance from previous state to curent state
		if(scene_end>=0 and level_elapsed_time_seconds>=scene_end):
			if(scene_state==SCENE_STATE.INTRO or scene_state==SCENE_STATE.DEATH):
				self.__setSceneState(SCENE_STATE.PLAY,this_frame_elapsed_seconds)
				
		#make decisions based on current state
		if(scene_end<=scene_start):
			ratio=0.0
		else:
			ratio=(level_elapsed_time_seconds-scene_start)/(scene_end-scene_start)
		self.scene['ratio']=ratio
		if(scene_state==SCENE_STATE.INTRO):
			pass #update pod, space ship, hyperspace effects
		elif(scene_state==SCENE_STATE.OUTRO): #when transitioning TO outro, fade out music
			if(ratio>=1):
				self.is_done=True #stop music in exitChapter()
			pass #update sphere of white
		elif(scene_state==SCENE_STATE.DEATH):
			pass #update sphere of black
		else: #CUT_SCENE.PLAY
			#if(this_frame_number%30==0):
			#	print('ring count: '+str(self.__getRingCount()))
			self.__updateSegmentQueue(level_elapsed_time_seconds)
			self.__updatePodSegment(level_elapsed_time_seconds)
			self.__updateCameraSegment(level_elapsed_time_seconds)
			
			#user input
			#buttons=[]
			#k=0
			#while k>=0:
				#k = sm.keys.read()
				#buttons.append(k)
			#k=max(buttons)
			#temp=k
			#is_smooth_motion_enabled=True
			#if(is_smooth_motion_enabled): 
				#k=max(k,self.last_key)
			#self.last_key=temp
			
			k=-1 #temp disconnect from player controls
			self.__updatePodPosition(navigation_joystick,delta_time)
			
			self.__updateProps(level_elapsed_time_seconds)
			self.__updateSegments(level_elapsed_time_seconds)
			
			#if k==27:
			#	self.is_done=True
			
			#TODO collissions
			#update pod, camera, light, rings, branches, laser, asteroids...
		
	def draw(self):
		scene_state=self.scene['state']
		ratio=self.scene['ratio']
		if(scene_state==SCENE_STATE.INTRO):
			self.pod.draw()
		elif(scene_state==SCENE_STATE.OUTRO):
			pass
		elif(scene_state==SCENE_STATE.DEATH):
			pass
		else:
			self.__drawSegments()#standard play scene
			self.pod.draw()

	#supported state transitions:
	#intro to play
	#play to death
	#play to outro
	#death to play
	def __setSceneState(self,to_scene_state,this_frame_elapsed_seconds):
		from_scene_state=self.scene['state']
		level_elapsed_seconds=this_frame_elapsed_seconds-self.level_start_time_seconds
		play_scene={'state':SCENE_STATE.PLAY,'start_seconds':level_elapsed_seconds,'end_seconds':-1,'ratio':0.0}
		out_scene=None
		if(to_scene_state==SCENE_STATE.PLAY):
			if(from_scene_state==SCENE_STATE.INTRO): #intro -> play
				out_scene=play_scene
				#fade in/start music
			elif(from_scene_state==SCENE_STATE.DEATH): #death -> play
				out_scene=play_scene
				self.segment_list=[] #clear segment list
				self.life+=1
				self.level_start_time_seconds=this_frame_elapsed_seconds
				self.pod_segment=None
				self.camera_segment=None
		elif(to_scene_state==SCENE_STATE.DEATH): #play -> death
			if(from_scene_state==SCENE_STATE.PLAY):
				out_scene={'state':SCENE_STATE.DEATH,'start_seconds':level_elapsed_seconds,'end_seconds':level_elapsed_seconds+self.DEATH_SECONDS,'ratio':0.0}
		elif(to_scene_state==SCENE_STATE.OUTRO):
			if(from_scene_state==SCENE_STATE.PLAY): #play -> outro
				out_scene={'state':SCENE_STATE.OUTRO,'start_seconds':level_elapsed_seconds,'end_seconds':level_elapsed_seconds+self.OUTRO_SECONDS,'ratio':0.0}
				#fade out music
		if(not out_scene is None):
			self.scene=out_scene
			return
		raise NotImplementedError('SceneManager.__setSceneState(): Unable to transition from scene state: '+str(from_scene_state)+', to scene state: '+str(to_scene_state))
