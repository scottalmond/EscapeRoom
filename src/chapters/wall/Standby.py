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
	def __init__(self,this_book,this_resource_manager,this_io_manager):
		super().__init__(this_book,this_resource_manager,this_io_manager)
		print("Wall Standby: Hello World")
		
	def enterChapter(self):
		super().enterChapter()
		print("wall.standby.enterChapter")
		#set 2D layer to top
		self.font=self._io_manager.pygame.font.SysFont('Comic Sans MS',300)
		
	def update(self,frame_number,seconds_since_last_frame):
		super().update(frame_number,seconds_since_last_frame)
		print("wall.standby.update, frame: "+str(frame_number))
		#pass #frame number, time since last frame, time of start of frame
		
	def draw(self,frame_number,seconds_since_last_frame):
		super().draw(frame_number,seconds_since_last_frame)
		#fill screen with black
		#draw standby...
		print("wall.standby.draw, frame: "+str(frame_number))#observing ~100 FPS on home PC, ~30 FPS on RPi 3
		textsurface=self.font.render('Standby FPS: '+str(math.floor(1/np.max((0.00001,seconds_since_last_frame)))),False,(0,0,0))
		self._io_manager.screen_2d.fill((0,0,255))
		self._io_manager.screen_2d.blit(textsurface,(0,0))
		self._io_manager.pygame.display.flip()
