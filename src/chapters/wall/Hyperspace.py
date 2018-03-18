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

from util.Chapter import Chapter
from chapters.wall.hyperspace_helper.HypserspaceEnvironment import *
import time
import numpy as np
import math
#from chapters.wall.hyperspace_helper import * #does not import properly
from random import *
from numpy import sin, cos, radians

class Hyperspace(Chapter):
	HYPERSPACE_BACKGROUND_VIDEO='/home/pi/Documents/aux/out_M170_b50_FPS20_SEC10.mp4'
	VIDEO_ENABLED=False #if True, play looping video
	MUSIC_PATH='./chapters/wall/assets/hyperspace/escaperoom01_pre01_0.mp3'
	MUSIC_ENABLED=False #if True, play looping music
	
	ASSET_FOLDER='chapters/wall/assets/hyperspace/'
	#dictionary of description:filename
	ASSETS_3D={"pod":'Pod.obj'}#,"ring0":'ring007.obj',"ring1":'ring006.obj'}
	POD_DEBUG_TEXTURE='circuit.jpg'
	
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
		self.environment=HypserspaceEnvironment(self.assets_3d)
			
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
		debug_strings.append("DEBUG.HEREXXXXXX")
		
		self.is_first_frame=this_frame_number==0
		#if(self.is_first_frame): self.debug_index=0
		#self.debug_index=self.debug_index+1
		
		#cx=(self.debug_index%64<32)*20-10
		#cy=(self.debug_index%16<8)*20-10
		#cz=(self.debug_index%32<16)*20-10
		#debug_strings.append("XYZ: "+str(cx)+", "+str(cy)+", "+str(cz))
		#self.rm.camera_3d.reset()
		#self.rm.camera_3d.rotate(0,0,0)
		#self.rm.camera_3d.position((0,0,-10))
		#self.pod_model.x=cx
		#self.pod_model.y=cy
		#self.pod_model.z=cz
		if(self.is_first_frame):
			self.rm.camera_3d.reset()
			self.rm.camera_3d.rotate(0,0,0)
			self.rm.camera_3d.position((0,0,-10))
		
		mouserot=0#this_frame_elapsed_seconds*30
		tilt=25.0
		camera_radius=20.0
		
		self.environment.update(this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds,
								self.rm)
		
		pod_position_x=self.environment.player_pod.x_offset
		pod_position_y=self.environment.player_pod.y_offset
		debug_strings.append("pod x: "+str(pod_position_x))
		debug_strings.append("pod y: "+str(pod_position_y))
		
		self.rm.camera_3d.reset()
		self.rm.camera_3d.rotate(-tilt,mouserot,0)
		self.rm.camera_3d.position((camera_radius * sin(radians(mouserot)) * cos(radians(tilt)),
									camera_radius * sin(radians(tilt)),
								   -camera_radius * cos(radians(mouserot)) * cos(radians(tilt))))
			
		self.setDebugStringList(debug_strings,this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds)
		
	def draw(self):
		super().draw()
		if(self.is_first_frame):
			self.rm.screen_2d.fill(self.background_color)
			self.displayDebugStringList(is_2d=True)
			self.rm.pygame.display.flip()
			
		self.environment.draw()
			
		self.displayDebugStringList(is_2d=False)
		#self.sphere.draw(self.rm.shader_3d,[self.pod_texture])
		#self.pod_model.draw()
		if(False): #debug overlay of all 3D models
			asset_id=0
			DISTANCE_BETWEEN_DEBUG_ASSETS=6
			for asset_name in sorted(self.assets_3d.keys()):
				asset_model=self.assets_3d[asset_name]
				asset_model.position(DISTANCE_BETWEEN_DEBUG_ASSETS*asset_id,0,0)
				asset_id=asset_id+1
				asset_model.draw()

	#load assets into a dictionary
	def __loadAssets(self):
		#this_filename=self.ASSET_FOLDER + self.POD_3D_MODEL
		#this_shader=self.rm.shader_3d
		#this_cam=self.rm.camera_3d
		#model = self.rm.pi3d.Model(camera=this_cam, file_string=this_filename, x=1.0, y=0.0, z=1.0,rx=90.0,ry=0.0,rz=0.0)
		#model.set_shader(this_shader)
		#self.pod_model=model

		#this_filename=self.ASSET_FOLDER + self.POD_DEBUG_TEXTURE
		#self.pod_texture=self.rm.pi3d.Texture(this_filename)
		
		#self.sphere=self.rm.pi3d.Sphere(radius=2.0, slices=32, sides=32)
		#self.sphere.position(6.0,0.0,0.0)
		#self.sphere.set_shader(self.rm.shader_3d)
		
		self.assets_3d={}
		for asset_name in sorted(self.ASSETS_3D.keys()):
			this_filename=self.ASSET_FOLDER+self.ASSETS_3D[asset_name]
			this_shader=self.rm.shader_3d
			this_cam=self.rm.camera_3d
			model = self.rm.pi3d.Model(camera=this_cam, file_string=this_filename, x=1.0, y=0.0, z=1.0,rx=90.0,ry=0.0,rz=0.0)
			model.set_shader(this_shader)
			self.assets_3d[asset_name]=model
		
