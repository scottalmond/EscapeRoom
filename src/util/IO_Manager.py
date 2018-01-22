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
This code provides accessor methods for frequently polled interfaces
like buttons

Usage:

"""

#General Support Libraries
import time
import numpy as np

#Physical Interfaces
import wiringpi as wp

#2D Graphics
import pygame

#3D Graphics
import pi3d
import sys
sys.path.insert(1, '/home/pi/pi3d')

#Video
#from omxplayer.player import OMXPlayer

class IO_Manager:
	OVERSAMPLE_RATIO_3D=4 #min is 1, integer values only
	
	def __init__(self,this_book_type,is_debug_enabled=False):
		self.pygame=pygame
		self.display_3d=None
		self.is_windowed=is_debug_enabled
		pass

	def clean(self):
		print("IO_Manager clean()")
		self.dispose()
		#needs to be 3D first then 2D, because 3D graphics has some pygame interaction/conflicts
		self.__create3Dgraphics()
		self.__create2Dgraphics()
		
	def dispose(self):
		self.__dispose3Dgraphics()
		self.__dispose2Dgraphics()

	def __create2Dgraphics(self):
		print("IO_Manager: Create 2D Graphics")
		self.pygame.init()
		self.pygame.font.init()
		self.pygame.mouse.set_visible(False)
		display_info=pygame.display.Info()
		if(self.is_windowed):
			self.screen_2d=pygame.display.set_mode((int(display_info.current_w),int(display_info.current_h)))
		else:
			self.screen_2d=pygame.display.set_mode((display_info.current_w,display_info.current_h),pygame.FULLSCREEN)
		self.pygame.display.flip()
		
	def __dispose2Dgraphics(self):
		self.pygame.display.quit()
		self.pygame.quit()
		
	def __create3Dgraphics(self):
		print("IO_Manager: Create 3D Graphics")
		self.display_3d = pi3d.Display.create(samples=self.OVERSAMPLE_RATIO_3D)
		self.display_3d.set_background(0,0,0,0)#transparent background
		
	def __dispose3Dgraphics(self):
		if(not self.display_3d is None):
			self.display_3d.destroy()
	
	#loads a video from a file, pauses the video, hides the video
	#and returns the reference, to the video player	
	def loadVideo(self,video_path,is_loop=False):
		video_args=['--no-osd','-o','local','--layer','-100']
		if(is_loop):
			video_args.append('--loop')
		print("IO_Manager.loadVideo, video args: "+str(video_args))
		video_player=OMXPlayer(video_path,args=video_args)
		#-100 places the video player visually above the desktop and pygame, but behind pi3d
		#-o directs any any audio output out the local audio jack rather than hdmi
		#no-osd turns off on-screen displays like "play" when starting a video
		video_player.pause()
		#video_player.set_aspect_mode('stretch')
		video_player.set_alpha(255)
	
	#unhides the video and plays it
	def playVideo(self,video_player):
		video_player.set_alpha(0)
		video_player.play()
	
	#change the location of the video with respoct to the screen displayed to players
	def setVideoPosition(self,video_player,top_left_x,top_left_y,bottom_right_x,bottom_right_y):
		video_player.set_video_pos(top_left_x,top_left_y,bottom_right_x,bottom_right_y)
	
	#cleanly exits the current video player instance
	def disposeVideo(self,video_player):
		video_player.quit()
		
	#query user and programmer inputs to determine if a STOP command has been placed
	def isStopped(self):
		for event in self.pygame.event.get():
			if(event.type == self.pygame.KEYDOWN and event.key == self.pygame.K_ESCAPE):
				return True
		return False

if __name__ == "__main__":
	io=IO_Manager(None)
	io.clean()
	print("stopped: "+str(io.isStopped()))
