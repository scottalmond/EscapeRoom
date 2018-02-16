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
This is a helper class that delivers noise that filles the screen.
Rather than generating noise from scratch, this class reads pre-generated
noise

Usage:


"""

from os import listdir
from os.path import isfile,join
import random

class ScreenNoise:
	ASSET_FOLDER='./chapters/wall/assets/screen_noise/'
	
	def __init__(self):
		self.image_filename_list=sorted([f for f in listdir(self.ASSET_FOLDER) if (isfile(join(self.ASSET_FOLDER, f)) and '.jpg' in f)])
		
	def clean(self,rm):
		self.flip_h=False
		self.flip_v=False
		self.image_index=0
		self.image_handles=[]
		for image_file in self.image_filename_list:
			self.image_handles.append(rm.pygame.image.load(self.ASSET_FOLDER+image_file).convert())

	#iterate through all images
	#to save disk space (and Github space), recycle images with permutations (vertical and horizontal flip)
	def update(self):
		self.image_index=self.image_index+1
		if(self.image_index>=len(self.image_handles)): #after reaching end of image sequence in folder
			self.image_index=0 #restart image index
			self.flip_h=not self.flip_h #toggle the horizontal flip
			if(self.flip_h): self.flip_v=not self.flip_v #every-other toggle of the horizontal triggers a toggle in the vertical
				
	def draw(self,rm):
		img=self.image_handles[self.image_index]
		img=rm.pygame.transform.flip(img,self.flip_h,self.flip_v)
		rm.screen_2d.blit(img,(0,0))
