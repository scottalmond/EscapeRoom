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

import time
import numpy as np
import math

from util.Chapter import Chapter
from util.IO_Manager import JOYSTICK,DIRECTION

class Tutorial(Chapter):
	def __init__(self,this_book):
		super().__init__(this_book)
		
		self.is_debug=True #enable additional text displays
		
		if(self.is_debug):
			print("Wall."+self.getTitle()+": Create Chapter Object")
		
	def clean(self):
		super().clean()
		
		self.image_input_standby=None #players have not activate input yet
		self.image_input_active=None #players are currently actuating this input
		self.image_input_done=None #players previously stimulated this input
		
		state_joystick_direction=[False,False,False,False]
		state_joystick_camera=[False,False,False,False]
		state_joystick_laser=[False,False,False,False,False]
		state_morse_code_buttons=[False,False]
		
	def dispose(self,is_final_call):
		super().dispose(is_final_call)
		
	def enterChapter(self,unix_time_seconds):
		super().enterChapter(unix_time_seconds)
		
		self.background_color=(255,255,255)
			
		if(self.is_debug):
			print("Wall."+self.getTitle()+": enterChapter()")
			self.font=self.io.pygame.font.SysFont('Comic Sans MS',100)
			self.font_color=(0,0,255)
			self.font_line_height_px=self.font.get_height()
			
	def exitChapter(self):
		super().exitChapter()
		
		if(self.is_debug):
			print("wall."+self.getTitle()+": exitChapter()")
		
		
	def update(self,this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds):#perhaps include total time elapsed in chapter... and playthrough number...
		super().update(this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds)
		
		self.seconds_since_last_frame=this_frame_elapsed_seconds-previous_frame_elapsed_seconds
		self.this_frame_number=this_frame_number
		
		
		
		if(self.is_debug):
			self.debug_strings=[self._book.getTitle()+"."+self.getTitle(),
								'FPS: '+str(math.floor(1/np.max((0.00001,self.seconds_since_last_frame)))),
								'Frame: '+str(self.this_frame_number),
								'Is Keyboard: '+str(self.io.isKeyboard()),
								'DOT, DASH: '+str(self.io.isDotPressed())+', '+str(self.io.isDashPressed()),
								'JOYSTICK_DIRECTION: '+self.__getDebugDirectionString(JOYSTICK.DIRECTION),
								'JOYSTICK_CAMERA: '+self.__getDebugDirectionString(JOYSTICK.CAMERA),
								'JOYSTICK_LASER, FIRE: '+self.__getDebugDirectionString(JOYSTICK.LASER)+', '+
									str(self.io.isFirePressed(JOYSTICK.LASER))
								]
	
	def __getDebugDirectionString(self,joystick):
		this_list=self.io.getJoystickDirection(joystick)
		string=""
		for direction in this_list:
			if(len(string)>0): string+=", "
			string+=direction.name
		if(len(string)==0): string="None"
		return string
	
	def draw(self):
		super().draw()
		
		self.io.screen_2d.fill(self.background_color)
		
		if(self.is_debug): #display debug text
			for this_string_index in range(len(self.debug_strings)):
				this_string=self.debug_strings[this_string_index]
				this_y_px=this_string_index*self.font_line_height_px #vertically offset each line of text
				rendered_string=self.font.render(this_string,False,self.font_color)
				self.io.screen_2d.blit(rendered_string,(0,this_y_px))
		
		self.io.pygame.display.flip()
