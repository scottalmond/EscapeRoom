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
#retains the state of the Laser pointer on screen, how much it has been fired
#retains teh state of the center of the laser pointer

import numpy as np
import math

from util.ResourceManager import DEVICE,DIRECTION

class Laser:
	MAX_X_DISTANCE=440 #The positive limit (half of full range) of the
	MAX_Y_DISTANCE=440
	TRANSLATION_RATE_DISTANCE_PER_SECOND=150 #pixels per second
	
	def __init__(self):
		self.is_firing=False
		self.is_user_input_active=True
		self.reset()

	#accept user inputs: location of pointer on screen, is_firing
	def update(self,this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds,
			   rm,player_pod):
		delta_seconds=this_frame_elapsed_seconds-previous_frame_elapsed_seconds
		translation_distance=self.TRANSLATION_RATE_DISTANCE_PER_SECOND*delta_seconds
		laser_joystick=DEVICE.LASER
		self.is_firing=rm.isFirePressed(laser_joystick)
		self.user_input=rm.getJoystickDirection(laser_joystick)
		if(self.is_user_input_active):
			if(DIRECTION.EAST in self.user_input):
				self.x_offset+=translation_distance
			elif(DIRECTION.WEST in self.user_input):
				self.x_offset-=translation_distance
			if(DIRECTION.NORTH in self.user_input):
				self.y_offset+=translation_distance
			elif(DIRECTION.SOUTH in self.user_input):
				self.y_offset-=translation_distance
			self.x_offset=np.clip(self.x_offset,-self.MAX_X_DISTANCE,self.MAX_X_DISTANCE) #may want to clamp to a circle rather than a square to stay within a circular ring...
			self.y_offset=np.clip(self.y_offset,-self.MAX_Y_DISTANCE,self.MAX_Y_DISTANCE)
			player_pod.setLaserPointer(self.x_offset,self.y_offset)
	
	#pointer on screen, laser from player_pod to pointer
	def draw(self):
		pass
		
	def reset(self):
		self.x_offset=0
		self.y_offset=0
		
