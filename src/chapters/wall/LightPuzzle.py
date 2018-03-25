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
The wall monitor is filled with static noise.  The IO_Manager is polled
for the status of the light puzzle components which are relayed to the Proctor
when all four components have changed state, the chapter is considered done

Usage:


"""

from util.Chapter import Chapter
from chapters.wall.noise_helper.ScreenNoise import ScreenNoise

import numpy as np

class LightPuzzle(Chapter):
	NUMBER_OF_INPUTS=4 #number of discrete inputs to the Wall from light puzzle components
	
	def __init__(self,this_book):
		super().__init__(this_book)
		if(self.is_debug):
			print("LightPuzzle: Hello World")
		self.screen_noise=ScreenNoise()
		
	def clean(self):
		super().clean()
		self.screen_noise.clean(self.rm)
	
	def enterChapter(self,unix_time_seconds):
		super().enterChapter(unix_time_seconds)
		#TO DO, dictate to HELM what chapter to go to and go to it
		
		self.input_activated=[False]*self.NUMBER_OF_INPUTS
		if(self.is_debug):
				print("Wall."+self.getTitle()+": create font")
		#self.font=self.rm.pygame.font.SysFont('Comic Sans MS',100)
		#self.font_line_height_px=self.font.get_height()
		self.background_color=(0,0,0)
		#self.font_color=(0,255,0)
		if(self.is_debug):
			print("Wall."+self.getTitle()+": set debug background color")
			self.background_color=(0,0,255)
		
	def update(self,this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds,packets):
		super().update(this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds,packets)
		all_done=True
		self.screen_noise.update()
		debug_strings=[]
		for input_index in range(self.NUMBER_OF_INPUTS):
			if(self.rm.isLightPuzzleInputActive(input_index)):
				self.input_activated[input_index]=True
			if(not self.input_activated[input_index]): all_done=False
			debug_strings.append("INPUT_"+str(input_index)+": "+str(self.input_activated[input_index])+", now: "+str(self.rm.isLightPuzzleInputActive(input_index)))
		debug_strings.append("is_done: "+str(all_done))
		self.setDebugStringList(debug_strings,this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds)
		if(all_done): self.is_done=True

	def draw(self):
		super().draw()
		self.rm.screen_2d.fill(self.background_color)
		#if(self.is_debug):
		#	for this_string_index in range(len(self.debug_strings)):
		#		this_string=self.debug_strings[this_string_index]
		#		this_y_px=this_string_index*self.font_line_height_px #vertically offset each line of text
		#		rendered_string=self.font.render(this_string,False,self.font_color)
		#		self.rm.screen_2d.blit(rendered_string,(0,this_y_px))
		self.screen_noise.draw(self.rm)
		self.displayDebugStringList()
		self.rm.pygame.display.flip()
				
			
		
			
