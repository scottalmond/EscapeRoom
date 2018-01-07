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

from omxplayer.player import OMXPlayer

class Standby(Chapter):
	def __init__(self,this_book,this_resource_manager,this_io_manager):
		super().__init__(this_book,this_resource_manager,this_io_manager)
		print("Wall Standby: Hello World")
		
		self.vid_back=None
		
	def clean(self):
		super().clean()
		
	def dispose(self):
		super().dispose() 
		
	def enterChapter(self):
		super().enterChapter()
		print("wall.standby.enterChapter")
		#set 2D layer to top
		self.chapter_start_unix_seconds=time.time()
		try:
			self.font=self._io_manager.pygame.font.SysFont('Comic Sans MS',300)
		except:
			pass
			
		self.screen_width=1920#self._io_manager.display_3d.width
		self.screen_height=1080#self._io_manager.display_3d.height
		
		if(True):
			video_file3='/home/pi/Documents/aux/FIBER OPTICAL (loop).mp4'
			self.vid_back=OMXPlayer(video_file3,args=['--no-osd','-o','local','--layer','-100'])
			#time.sleep(2)
			#vid_back.pause()
			#self.vid_back.set_aspect_mode('stretch')
			vid_back_width=1920*2
			vid_back_height=1080*2
			HWIDTH=self.screen_width/2
			HHEIGHT=self.screen_height/2
			#vid_back.set_video_pos(-vid_back_width/2+HWIDTH,-vid_back_height/2+HHEIGHT,vid_back_width/2+HWIDTH, vid_back_height/2+HHEIGHT)
			
	def exitChapter(self):
		super().exitChapter()
		print("wall.Standby: exitChapter()")
		
		if(not self.vid_back is None):
			print("T1: "+str(time.time()-self.chapter_start_unix_seconds))
			self.vid_back.stop()
			print("T2: "+str(time.time()-self.chapter_start_unix_seconds))
			self.vid_back.quit()
			print("T3: "+str(time.time()-self.chapter_start_unix_seconds))
		
		
	def update(self,frame_number,seconds_since_last_frame):#perhaps include total time elapsed in chapter... and playthrough number...
		super().update(frame_number,seconds_since_last_frame)
		#print("wall.standby.update, frame: "+str(frame_number))
		#pass #frame number, time since last frame, time of start of frame
		if(self.chapter_start_unix_seconds+3<time.time()):
			self.is_done=True
		
	def draw(self,frame_number,seconds_since_last_frame):
		super().draw(frame_number,seconds_since_last_frame)
		#fill screen with black
		#draw standby...
		#print("wall.standby.draw, frame: "+str(frame_number))#observing ~100 FPS on home PC, ~30 FPS on RPi 3
		try:
			textsurface=self.font.render('Standby FPS: '+str(math.floor(1/np.max((0.00001,seconds_since_last_frame)))),False,(0,0,0))
			self._io_manager.screen_2d.fill((0,0,255))
			self._io_manager.screen_2d.blit(textsurface,(0,0))
			self._io_manager.pygame.display.flip()
		except:
			pass
