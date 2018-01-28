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
Chapter waits for a command from the proctor
Routinely checks on the status of the Helm PC, commands it to Standby
if the detected chapter is incorrect (ie, if Helm got out of sync with Master)

Usage:


"""

from util.Chapter import Chapter
import time
import numpy as np
import math

class Standby(Chapter):
	def __init__(self,this_book):
		super().__init__(this_book)
		
		self.is_debug=True
		
		if(self.is_debug):
			print("Wall."+self.getTitle()+": Create Chapter Object")
		
	def clean(self):
		super().clean()
		
	def dispose(self,is_final_call):
		super().dispose(is_final_call) 
		
	def enterChapter(self,unix_time_seconds):
		super().enterChapter(unix_time_seconds)
		
		self.background_color=(0,0,0)
			
		if(self.is_debug):
			print("Wall."+self.getTitle()+": create debug strings")
			print("Wall."+self.getTitle()+": enterChapter()")
			self.background_color=(0,0,255)
			print("Wall."+self.getTitle()+": create font")
			self.font=self.rm.pygame.font.SysFont('Comic Sans MS',100)
			self.font_color=(0,255,0)
			print("Wall."+self.getTitle()+": get string height")
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
								'Frame: '+str(self.this_frame_number)]
		
	def draw(self):
		super().draw()
		
		self.rm.screen_2d.fill(self.background_color)
		
		if(self.is_debug): #display debug text
			for this_string_index in range(len(self.debug_strings)):
				this_string=self.debug_strings[this_string_index]
				this_y_px=this_string_index*self.font_line_height_px #vertically offset each line of text
				rendered_string=self.font.render(this_string,False,self.font_color)
				self.rm.screen_2d.blit(rendered_string,(0,this_y_px))
		
		self.rm.pygame.display.flip()
