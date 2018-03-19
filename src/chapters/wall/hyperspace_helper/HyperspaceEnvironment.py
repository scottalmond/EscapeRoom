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



Usage:


"""

#gets rings to display
#get debris to display
#display intro/outro
from chapters.wall.hyperspace_helper.PlayerPod import *
from chapters.wall.hyperspace_helper.Camera import *
from chapters.wall.hyperspace_helper.Laser import *

class HypserspaceEnvironment: #there seems to be a Python class "Environment", so use a longer name...
	def __init__(self,assets_3d,is_video_enabled=False,is_music_enabled=False):
		self.player_pod=PlayerPod(assets_3d["pod"],assets_3d["laser_base"],assets_3d["laser_gun"]) #pointer to player location
		self.laser=Laser()
		self.segment_list=[] #list of segments in play
		#segment=Segment() #fetch rings, ring type
		self.camera=Camera()

	def update(self,this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds,
			   rm):
		self.player_pod.update(this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds,
							   rm)
		self.laser.update(     this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds,
							   rm,self.player_pod)
		#self.__updateIntroOutro()
		#self.__updateRingAsteroid()
		#self.__updatePlayerPod()
		#self.__updateDeath()
		
	def draw(self):
		self.player_pod.draw()
		self.laser.draw()
		
