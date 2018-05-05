"""
   Copyright 2018 Scott Almond

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

Purpose:



Usage:


"""

import numpy as np
import math

#from transforms3d.euler import euler2mat, mat2euler

from util.ResourceManager import DEVICE,DIRECTION
#retains the state of the center of the player cargo pod

class PlayerPod:
	TRANSLATION_RATE_DISTANCE_PER_SECOND=5.0 #distance units are arbitrary Pi3D units
	MAX_X_DISTANCE=4 #The positive limit (half of full range) of the
	# horizontal range of pod motion on screen
	MAX_Y_DISTANCE=4
	MAX_HITS=3 #number of obstacles the player needs to run into in order to die (restart level)
	
	def __init__(self,pod_model,laser_joint_model,laser_model):
		self.pod={"name":"pod","model":pod_model} #rotation in degrees
		self.laser_base={"name":"laser_base","model":laser_joint_model}
		self.laser_gun={"name":"laser_gun","model":laser_model}
		self.laser_tip={"name":"laser_tip"}
		self.is_user_input_active=True #False #user inputs are only active after intro plays, but gas effects will still appear
		self.deaths=-1 #number of times the player has died
		self.restart(0)
		
	#accept user inputs and change the state of the pod
	def update(self,this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds,
			   rm):
		#if right/left/up/down pressed, increment position of pod
		delta_seconds=this_frame_elapsed_seconds-previous_frame_elapsed_seconds
		translation_distance=self.TRANSLATION_RATE_DISTANCE_PER_SECOND*delta_seconds
		self.user_input=rm.getJoystickDirection(DEVICE.DIRECTION) #guaranteed north, south, neither, but not both
		if(len(self.user_input)==2): translation_distance=translation_distance/1.414 #if moving in two direction (North and East), each dimension gets 1/sqrt(2) of the translation component
		x_offset=self.pod["translation"][0]
		y_offset=self.pod["translation"][1]
		if(self.is_user_input_active):
			if(DIRECTION.EAST in self.user_input):
				x_offset+=translation_distance
			elif(DIRECTION.WEST in self.user_input):
				x_offset-=translation_distance
			if(DIRECTION.NORTH in self.user_input):
				y_offset+=translation_distance
			elif(DIRECTION.SOUTH in self.user_input):
				y_offset-=translation_distance
			x_offset=np.clip(x_offset,-self.MAX_X_DISTANCE,self.MAX_X_DISTANCE) #may want to clamp to a circle rather than a square to stay within a circular ring...
			y_offset=np.clip(y_offset,-self.MAX_Y_DISTANCE,self.MAX_Y_DISTANCE)
			vector=np.array([x_offset,y_offset,self.pod["translation"][2]])
			self.pod["translation"]=vector
		#self.pod["translation"][0]=x_offset #doesn't work, no assignment is made, retains original value
		
		self.mouserot=this_frame_elapsed_seconds*30
		#enable render of gas effects
		
	#pod, laser points at pointer, gas effects
	#pi3d rotates objects about their origin, then moves them along
	# the global reference frame axes to the given translation offset
	def draw(self):
		for obj in [self.pod,self.laser_base,self.laser_gun]:
			position,rotation=self.__getOrientation(obj["name"])
			model=obj["model"]
			model.position(position[0],position[1],position[2])
			#model.rotateToX(0)
			#model.rotateToy(0)
			#model.rotateToz(0)
			#tr1=model.tr1
			#for row in range(3):
			#	for col in range(3):
			#		tr1[row][col]=rotation_matrix[row][col]
			#model.tr1=tr1
			model.rotateToX(math.degrees(rotation[0])) #pi3d operates in degrees
			model.rotateToY(math.degrees(rotation[1]))
			model.rotateToZ(math.degrees(rotation[2]))
			model.draw()
			
	#accessor method for GUI to echo the user input joystick states
	#also for laser to determine if laser is firing
	def getUserInput(self):
		return self.user_input
		
	def hit(self):
		self.hits=self.hits+1
		
	def is_dead(self):
		if(self.hits>=MAX_HITS):
			return True
	
	#the Laser GUI reports the position of the laser pointer on screen
	# x is the horizontal position on the screen, +x is right/East
	# y is vertical, +y is up/North, max pixel extent: (+540,-540)
	#movement in x changes the rotation of the laser_base about the local y-axis
	#movement in y changes the rotation of the laser_gun about the local x-axis
	def setLaserPointer(self,screen_x,screen_y):
		radians_hori=math.atan(screen_x/500) #radians
		radians_vert=math.atan(screen_y/500)
		rotation_base=np.array([self.laser_base["rotation"][0],radians_hori,self.laser_base["rotation"][2]])
		rotation_gun= np.array([radians_vert,self.laser_gun["rotation"][1], self.laser_gun["rotation"][2]])
		if(self.is_user_input_active):
			self.laser_base["rotation"]=rotation_base
			self.laser_gun["rotation"]=rotation_gun
	
	#restart level, reset player to default config
	def restart(self,level_start_time_elapsed_seconds):
		self.hits=0
		self.pod["translation"]=np.array([0,0,0]) # (X,Y,Z)
		self.pod["rotation"]=np.array([0,0,0]) #rotation in radians, euler angles (X,Y,Z)
		self.laser_base["translation"]=np.array([0,3.03,0]) #property of the specific .obj file
		self.laser_base["rotation"]=np.array([0,0,0])
		self.laser_gun["translation"]=np.array([0,0.48,-0.45])
		self.laser_gun["rotation"]=np.array([0,0,0])
		self.laser_tip["translation"]=np.array([0,0.25,2.76])
		self.level_start_seconds=level_start_time_elapsed_seconds
		self.deaths=self.deaths+1

	#extract the X, Y, Z position of, and alpha, beta, gamma angles of, the
	# given object to feed into Pi3D
	#obj is a String: "pod", "laser_base", "laser_gun", "laser_tip"
	#returns translation,rotation=getOrientation()
	# where translaction and rotation are 3 element numpy arrays
	def __getOrientation(self,obj):
		position=np.array([0,0,0]) #start at origin
		rotation_matrix=np.identity(3) # local_xyz * __rotation__ = global_XYZ
		
		#translation of pod in x,y in original coordinate frame
		position=np.dot(self.pod["translation"],rotation_matrix)+position
		#rotation of pod about x, z (TODO: implement x,z motion elsewhere in program)
		xyz=self.pod["rotation"]
		R=[0,0,0] #euler2mat(xyz[0],xyz[1],xyz[2],'sxyz')
		rotation_matrix=np.dot(R,rotation_matrix)
		z,x,y=[0,0,0] #mat2euler(rotation_matrix,'szxy') #pi3d uses ZXY rotation https://pi3d.github.io/html/_modules/pi3d/Shape.html
		rotation_euler=np.array([x,y,z])
		#return pod
		if(obj=="pod"):
			return position,rotation_euler
			
		#translation from center of pod to top gun base
		position=np.dot(self.laser_base["translation"],rotation_matrix)+position
		#rotation of gun base about y
		xyz=self.laser_base["rotation"]
		R=[0,0,0] #euler2mat(xyz[0],xyz[1],xyz[2],'sxyz')
		rotation_matrix=np.dot(R,rotation_matrix)
		z,x,y=[0,0,0] #mat2euler(rotation_matrix,'szxy')
		rotation_euler=np.array([x,y,z])
		#return gun base
		if(obj=="laser_base"):
			return position,rotation_euler
			
		#translation from center of gun base to center of gun turret
		position=np.dot(self.laser_gun["translation"],rotation_matrix)+position
		#rotation of gun turret about x
		xyz=self.laser_gun["rotation"]
		R=[0,0,0] #euler2mat(xyz[0],xyz[1],xyz[2],'sxyz')
		rotation_matrix=np.dot(R,rotation_matrix)
		z,x,y=[0,0,0] #mat2euler(rotation_matrix,'szxy')
		rotation_euler=np.array([x,y,z])
		#rotation_euler=np.array([self.laser_gun["rotation"][0],self.laser_base["rotation"][1],0]) #hotpatch for ZXY euler angle rotation back-calculation issue - no change in behavior
		#return gun turret
		if(obj=="laser_gun"):
			return position,rotation_euler
			
		#translation from center of gun turret to tip of laser
		# TODO: implement laser visal effect from tip to asteroid
		position=np.dot(self.laser_tip["translation"],rotation_matrix)+position
		return position,rotation_euler
		
