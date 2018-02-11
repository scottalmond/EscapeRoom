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
This tutorial presents the players with an iconic representation of
all player controls, whith al marked as inactive.  When players actuate the
corresponding controls, that sub-component is marked as active.  Once
players have activated all controls (and presumably sat in the chairs next to
the controls) then the chapter is considered done

Usage:


"""

from enum import Enum
import time
import numpy as np
import math

from util.Chapter import Chapter
from util.ResourceManager import DEVICE,DIRECTION

class BUTTON_STATE(Enum):
	IDLE=0 #button has not been actuated
	ACTIVE=1 #input is being actuated now
	DONE=3 #button was previously actuated but is not right now

class Tutorial(Chapter):
	def __init__(self,this_book):
		super().__init__(this_book)
		
		if(self.is_debug):
			print("Wall."+self.getTitle()+": Create Chapter Object")
		
	def clean(self):
		super().clean()
		
		self.image_input_standby=self.rm.pygame.image.load('./chapters/wall/assets/tutorial_button_idle.png').convert_alpha() #players have not activate input yet
		self.image_input_active=self.rm.pygame.image.load('./chapters/wall/assets/tutorial_button_active.png').convert_alpha() #players are currently actuating this input
		self.image_input_done=self.rm.pygame.image.load('./chapters/wall/assets/tutorial_button_done.png').convert_alpha() #players previously stimulated this input
		
		#the status of device inputs are clustered around a central point on screen, offset by this much from that point
		self.image_offset_x_px=100
		self.image_offset_y_px=100
		
		#joysticks in order: up, left, down, right, fire
		#morse: dot, dash
		self.input_states={DEVICE.DIRECTION:[BUTTON_STATE.IDLE,BUTTON_STATE.IDLE,BUTTON_STATE.IDLE,BUTTON_STATE.IDLE],
						   DEVICE.CAMERA:[BUTTON_STATE.IDLE,BUTTON_STATE.IDLE,BUTTON_STATE.IDLE,BUTTON_STATE.IDLE],
						   DEVICE.LASER:[BUTTON_STATE.IDLE,BUTTON_STATE.IDLE,BUTTON_STATE.IDLE,BUTTON_STATE.IDLE,BUTTON_STATE.IDLE],
						   DEVICE.MORSE:[BUTTON_STATE.IDLE,BUTTON_STATE.IDLE]
						   }
		
	def dispose(self,is_final_call):
		super().dispose(is_final_call)
		
	def enterChapter(self,unix_time_seconds):
		super().enterChapter(unix_time_seconds)
		
		self.background_color=(100,255,255)
			
		if(self.is_debug):
			print("Wall."+self.getTitle()+": enterChapter()")
			print("Wall."+self.getTitle()+": create font")
			self.font=self.rm.pygame.font.SysFont('Comic Sans MS',100)
			self.font_color=(0,0,255)
			print("Wall."+self.getTitle()+": get font height")
			self.font_line_height_px=self.font.get_height()
			
	def exitChapter(self):
		super().exitChapter()
		
		if(self.is_debug):
			print("wall."+self.getTitle()+": exitChapter()")
		
		
	def update(self,this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds):#perhaps include total time elapsed in chapter... and playthrough number...
		super().update(this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds)
		
		self.seconds_since_last_frame=this_frame_elapsed_seconds-previous_frame_elapsed_seconds
		self.this_frame_number=this_frame_number
		
		#iterate through devices, set all active inputs to done
		for device in self.input_states:
			device_state=self.input_states[device]
			for input_state_index in range(len(device_state)):
				if(device_state[input_state_index]==BUTTON_STATE.ACTIVE):
					device_state[input_state_index]=BUTTON_STATE.DONE
		#then set any that are depressed to active
		for device in [DEVICE.DIRECTION,DEVICE.CAMERA,DEVICE.LASER]:
			for direction in [DIRECTION.NORTH,DIRECTION.WEST,DIRECTION.SOUTH,DIRECTION.EAST]:
				if(direction in self.rm.getJoystickDirection(device)):
					self.input_states[device][direction.value]=BUTTON_STATE.ACTIVE
		if(self.rm.isFirePressed(DEVICE.LASER)): self.input_states[DEVICE.LASER][4]=BUTTON_STATE.ACTIVE
		if(self.rm.isDotPressed()): self.input_states[DEVICE.MORSE][0]=BUTTON_STATE.ACTIVE
		if(self.rm.isDashPressed()): self.input_states[DEVICE.MORSE][1]=BUTTON_STATE.ACTIVE
		#if all have been depressed, or are curerntly depressed, set is_done=True
		all_done=True
		for device in self.input_states:
			device_state=self.input_states[device]
			for input_state_index in range(len(device_state)):
				#if any input has not been actuated, then is_done cannot be set
				if(device_state[input_state_index]==BUTTON_STATE.IDLE): all_done=False
		if(all_done): self.is_done=True
		
		if(self.is_debug):
			self.debug_strings=[self._book.getTitle()+"."+self.getTitle(),
								'FPS: '+str(math.floor(1/np.max((0.00001,self.seconds_since_last_frame)))),
								'Frame: '+str(self.this_frame_number),
								'Is Keyboard: '+str(self.rm.isKeyboard()),
								'DOT, DASH: '+str(self.rm.isDotPressed())+', '+str(self.rm.isDashPressed()),
								'JOYSTICK_DIRECTION: '+self.__getDebugDirectionString(DEVICE.DIRECTION),
								'JOYSTICK_CAMERA: '+self.__getDebugDirectionString(DEVICE.CAMERA),
								'JOYSTICK_LASER, FIRE: '+self.__getDebugDirectionString(DEVICE.LASER)+', '+
									str(self.rm.isFirePressed(DEVICE.LASER))
								]
	
	def __getDebugDirectionString(self,joystick):
		this_list=self.rm.getJoystickDirection(joystick)
		string=""
		for direction in this_list:
			if(len(string)>0): string+=", "
			string+=direction.name
		if(len(string)==0): string="None"
		return string
	
	def draw(self):
		super().draw()
		
		self.rm.screen_2d.fill(self.background_color)
		
		for device in self.input_states:
			self.__drawDeviceState(device)
		
		if(self.is_debug): #display debug text
			for this_string_index in range(len(self.debug_strings)):
				this_string=self.debug_strings[this_string_index]
				this_y_px=this_string_index*self.font_line_height_px #vertically offset each line of text
				rendered_string=self.font.render(this_string,False,self.font_color)
				self.rm.screen_2d.blit(rendered_string,(0,this_y_px))
		
		self.rm.pygame.display.flip()

	#display the state of one device on screen
	#laser bottom-right
	#morse bottom left
	#direction top-left
	#camera top-right
	def __drawDeviceState(self,device):
		screen_dim=self.rm.getScreenDimensions()
		if(device==DEVICE.MORSE):
			device_centroid=(int(screen_dim[0]*1/4),int(screen_dim[1]*3/4))
			self.__drawInputStateAt(self.input_states[device][0],device_centroid[0]-self.image_offset_x_px,device_centroid[1])
			self.__drawInputStateAt(self.input_states[device][1],device_centroid[0]+self.image_offset_x_px,device_centroid[1])
		elif(device==DEVICE.DIRECTION):
			device_centroid=(int(screen_dim[0]*1/4),int(screen_dim[1]*1/4))
		elif(device==DEVICE.CAMERA):
			device_centroid=(int(screen_dim[0]*3/4),int(screen_dim[1]*1/4))
		elif(device==DEVICE.LASER):
			device_centroid=(int(screen_dim[0]*3/4),int(screen_dim[1]*3/4))
		else:
			raise ValueError("Invalid device provided: "+str(device))
		if(device==DEVICE.DIRECTION or device==DEVICE.CAMERA or device==DEVICE.LASER):
			self.__drawInputStateAt(self.input_states[device][0],device_centroid[0],device_centroid[1]-self.image_offset_y_px)
			self.__drawInputStateAt(self.input_states[device][1],device_centroid[0]-self.image_offset_x_px,device_centroid[1])
			self.__drawInputStateAt(self.input_states[device][2],device_centroid[0],device_centroid[1]+self.image_offset_y_px)
			self.__drawInputStateAt(self.input_states[device][3],device_centroid[0]+self.image_offset_x_px,device_centroid[1])
		if(device==DEVICE.LASER):
			self.__drawInputStateAt(self.input_states[device][4],device_centroid[0],device_centroid[1])
			
	#render a graphic of the input state at the given location
	#note: given location is the center of the image
	def __drawInputStateAt(self,input_state,x_px,y_px):
		if(input_state==BUTTON_STATE.IDLE):
			img=self.image_input_standby
		elif(input_state==BUTTON_STATE.ACTIVE):
			img=self.image_input_active
		elif(input_state==BUTTON_STATE.DONE):
			img=self.image_input_done
		else:
			raise ValueError("Invalid device state: "+str(input_state))
		img_size=img.get_size()
		self.rm.screen_2d.blit(img,(x_px-img_size[0],y_px-img_size[1]))
