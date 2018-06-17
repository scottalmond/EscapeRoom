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

#responsible for Maze (map definition), Environment (3D object definitions, video, music)
#ConnectionManager (relay object state between PCs)

import time
import numpy as np
import math

from util.Chapter import Chapter
from util.ResourceManager import DIRECTION,DEVICE
from chapters.wall.hyperspace_helper.SceneManager import SceneManager

class Hyperspace(Chapter):
	HYPERSPACE_BACKGROUND_VIDEO='/home/pi/Documents/aux/out_M170_b50_FPS20_SEC10.mp4'
	#HYPERSPACE_BACKGROUND_VIDEO='/home/pi/Documents/aux/out.mp4'
	VIDEO_ENABLED=False #if True, play looping video
	LOOP_VIDEO=True
	MUSIC_PATH='./chapters/wall/assets/hyperspace/escaperoom02_pre06_2.mp3'
	MUSIC_ENABLED=True #if True, play looping music
	ASSET_FOLDER='chapters/wall/assets/hyperspace/'
	BACKGROUND_2D='./chapters/wall/assets/hyperspace/background.png'
	
	def __init__(self,this_book):
		super().__init__(this_book)
		#variables
		
		
		#objects
		self.scene_manager=SceneManager()
		self.background_video_player=None #reference to the omxplayer
		#that plays the background hyperspace video
		self.is_first_frame=True #if is first frame, draw pygame background

	def clean(self):
		super().clean()
		self.scene_manager.clean(self.rm.pi3d,self.rm.display_3d,self.rm.camera_3d)
		if(not self.background_video_player is None):
			self.rm.disposeVideo(self.background_video_player)
		if(self.VIDEO_ENABLED):
			self.background_video_player=None#self.rm.loadVideo(self.HYPERSPACE_BACKGROUND_VIDEO)
			if(self.background_video_player is None):
				print("Hyperspace.clean: video player is None")
			else:
				print("Hyperspace.clean: video player created")
			print("Hyperspace.clean.sleep...")
			time.sleep(2)
			self.rm.pauseVideo(self.background_video_player)
			print("Hyperspace.clean.sleep done")
		self.image_background=self.rm.pygame.image.load(self.BACKGROUND_2D).convert() #temp placehold for video
			
	def dipose(self,is_final_call):
		super().dipose(self,is_final_call)
		if(not self.background_video_player is None):
			self.rm.disposeVideo(self.background_video_player)
		
	def enterChapter(self,unix_time_seconds):
		super().enterChapter(unix_time_seconds)
		if(self.MUSIC_ENABLED):
			print("Hyperspace.enterChapter.MUSIC: here")
			self.rm.pygame.mixer.music.load(self.MUSIC_PATH)
			self.rm.pygame.mixer.music.play(loops=-1) #TODO: move to later in game sequence storyboard
		if(self.VIDEO_ENABLED):
			self.rm.playVideo(self.background_video_player)
			self.background_video_player=self.rm.loadVideo(self.HYPERSPACE_BACKGROUND_VIDEO,self.LOOP_VIDEO)
		self.background_color=(0,100,255)
		
	def exitChapter(self):
		super().exitChapter()
		if(self.MUSIC_ENABLED):
			self.rm.pygame.mixer.music.stop()
		if(self.VIDEO_ENABLED):
			#self.rm.pauseVideo(self.background_video_player)
			self.rm.disposeVideo(self.background_video_player)#temp
			self.background_video_player=None#temp
	
	def update(self,this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds,packets):
		super().update(this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds,packets)
		debug_strings=[]
		debug_strings.append("DEBUG.HEREXXXXXX")
		
		#navigation_joystick=self.rm.getJoystickDirection(DEVICE.DIRECTION)
		#camera_joystick=self.rm.getJoystickDirection(DEVICE.CAMERA)
		#laser_joystick=self.rm.getJoystickDirection(DEVICE.LASER)
		is_fire_laser=self.rm.isFirePressed(DEVICE.LASER)
		
		is_input_active=np.zeros((3,4), dtype=bool) #list of user input states (bool)
		device_list=[DEVICE.DIRECTION,DEVICE.CAMERA,DEVICE.LASER]
		direction_list=[DIRECTION.NORTH,DIRECTION.WEST,DIRECTION.SOUTH,DIRECTION.EAST]
		for input_device in range(len(device_list)):
			joystick_inputs=self.rm.getJoystickDirection(device_list[input_device])
			for direction_id in range(len(direction_list)):
				if(direction_list[direction_id] in joystick_inputs):
					is_input_active[input_device,direction_id]=True
		
		self.scene_manager.update(this_frame_number,
			this_frame_elapsed_seconds,previous_frame_elapsed_seconds,None,
			is_input_active[0,:],is_input_active[1,:],is_input_active[2,:],is_fire_laser)
		
		self.is_first_frame=this_frame_number==0
		self.setDebugStringList(debug_strings,this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds)
		
	def draw(self):
		super().draw()
		self.scene_manager.draw()
		self.displayDebugStringList(is_2d=False)
		#	self.rm.pygame.display.flip()
			
		#self.environment.draw()
		if(self.is_first_frame):
		#	self.rm.screen_2d.fill(self.background_color)
			self.rm.screen_2d.blit(self.image_background,(0,0))
			self.rm.pygame.display.flip()
		
