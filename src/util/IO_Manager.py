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

class IO_Manager:
	OVERSAMPLE_RATIO_3D=4 #min is 1, integer values only
	
	def __init__(self,this_book_type):
		self.pygame=pygame

	def clean(self):
		self.__create2Dgraphics()
		self.__create3Dgraphics()
		
	def dispose(self):
		self.__dispose3Dgraphics()
		self.__dispose2Dgraphics()

	def __create2Dgraphics(self):
		self.pygame.init()
		self.pygame.font.init()
		self.pygame.mouse.set_visible(False)
		display_info=pygame.display.Info()
		self.screen_2d=pygame.display.set_mode((display_info.current_w,display_info.current_h),pygame.FULLSCREEN)
		#self.screen_2d.fill((0,0,255))
		self.pygame.display.flip()
		
	def __dispose2Dgraphics(self):
		self.pygame.display.quit()
		self.pygame.quit()
		
	def __create3Dgraphics(self):
		self.display_3d = pi3d.Display.create(samples=OVERSAMPLE_RATIO_3D)
		self.display_3d.set_background(0,0,0,0)#transparent background
		
	def __dispose3Dgraphics(self):
		pass
