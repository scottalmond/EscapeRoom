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
from chapters.wall.hyperspace_helper import *

class Hyperspace(Chapter):
	HYPERSPACE_BACKGROUND_VIDEO='/home/pi/Documents/aux/out_M170_b50_FPS20_SEC10.mp4'
	VIDEO_ENABLED=False #if True, play looping video
	MUSIC_PATH='./chapters/wall/assets/hyperspace/escaperoom01_pre01_0.mp3'
	MUSIC_ENABLED=False #if True, play looping music
	
	ASSET_FOLDER='chapters/wall/assets/hyperspace/'
	POD_3D_MODEL='Pod.obj'
	
	def __init__(self,this_book):
		super().__init__(this_book)
		#variables
		
		
		#objects
		self.background_video_player=None #reference to the omxplayer
		#that plays the background hyperspace video

	def clean(self):
		super().clean()
		if(not self.background_video_player is None):
			self.io.disposeVideo(self.background_video_player)
		if(self.VIDEO_ENABLED):
			self.background_video_player=loadVideo(self.HYPERSPACE_BACKGROUND_VIDEO)
			
		
		#assets - create after resource manager has been initialized
		self.__loadAssets()
			
	def dipose(self,is_final_call):
		super().dipose(self,is_final_call)
		if(not self.background_video_player is None):
			self.io.disposeVideo(self.background_video_player)
		
	def enterChapter(self,unix_time_seconds):
		super().enterChapter(unix_time_seconds)
		if(self.VIDEO_ENABLED):
			self.io.playVideo(self.background_video_player)
		self.background_color=(0,100,255)
		
	def exitChapter(self):
		super().exitChapter()
	
	def update(self,this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds):
		super().update(this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds)
		debug_strings=[]
		debug_strings.append("DEBUG.HERE")
		self.setDebugStringList(debug_strings,this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds)

	def draw(self):
		super().draw()
		self.rm.screen_2d.fill(self.background_color)
		#self.displayDebugStringList(is_2d=True)
		self.rm.pygame.display.flip()
		self.pod_model.draw()
		self.displayDebugStringList(is_2d=False)

	def __loadAssets(self):
		this_filename=self.ASSET_FOLDER + self.POD_3D_MODEL
		this_shader=self.rm.shader_3d
		this_cam=self.rm.camera_3d
		model = self.rm.pi3d.Model(camera=this_cam, file_string=this_filename, x=0.0, y=0.0, z=3*1,rx=90.0*(0),ry=0.0,rz=0.0)
		model.set_shader(this_shader)
		self.pod_model=model
