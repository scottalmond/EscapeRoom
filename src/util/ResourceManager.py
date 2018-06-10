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


Notes:
Originally this code was intended to flush the 2D and 3D libraries every play through to ensure a clean state
for each playthrough.  However, the pygame library has a heisenbug segmentation fault when creating a font
after a pygame library reboot.  This may be due to an interaction with Pi3D.
Either way, libraries are no longer rebooted after the initial creation but instead persist between playthroughs

"""

#General Support Libraries
import time
import numpy as np
from enum import Enum
import threading

#joystick directions
#units increasing from 0, per WASD order, used as indecies in Tutorial
class DIRECTION(Enum):
	NORTH=0
	WEST=1
	SOUTH=2
	EAST=3

#id for each joystick (2 physical joysticks from the singular DIRECTION joystick)
class DEVICE(Enum):
	DIRECTION=0
	CAMERA=1
	LASER=2
	MORSE=3
	
#discrete input pin mapping
#refer to "wPi" column in resources/project_box_pinout.ods
class DI_PINS(Enum):
	BUTTON_DOT=8
	BUTTON_DASH=9
	DIRECTION_JOYSTICK_0=7
	DIRECTION_JOYSTICK_1=0
	DIRECTION_JOYSTICK_2=2
	DIRECTION_JOYSTICK_3=3
	CAMERA_JOYSTICK_0=12
	CAMERA_JOYSTICK_1=13
	CAMERA_JOYSTICK_2=14
	CAMERA_JOYSTICK_3=30
	LASER_JOYSTICK_0=21
	LASER_JOYSTICK_1=22
	LASER_JOYSTICK_2=23
	LASER_JOYSTICK_3=24
	LASER_JOYSTICK_FIRE=25
	LIGHT_0=15
	LIGHT_1=16
	LIGHT_2=1
	LIGHT_3=4

class ResourceManager:
	OVERSAMPLE_RATIO_3D=4 #min is 1, integer values only - higher values used to reduce pixelation in 3D graphics
	SCREENSHOT_PATH='/home/pi/Documents/aux/screencaps/' #captured by pressing F2
	
	def __init__(self,this_book_type,is_debug=False,is_windowed=False,is_keyboard=False):
		from util.Book import BOOK_TYPE #must be run after Book.py is initialized, otherwise fails to load (cannot find import)
		self.pygame=None
		self.pi3d=None
		if(this_book_type==BOOK_TYPE.WALL or this_book_type==BOOK_TYPE.HELM): #should probably generalize to be book-type agnostic... just is_2d_enabled, is_3d_enabled, etc
			print("ResourceManager.init: here")
			#if need supporting libraries, load them
			#Physical Interfaces
			import wiringpi as wp
			self.wp=wp
			wp.wiringPiSetup()
			for pin in DI_PINS:
				wp.pinMode(pin.value,wp.GPIO.INPUT)
				wp.pullUpDnControl(pin.value,wp.GPIO.PUD_UP)
			#2D Graphics
			import pygame
			#3D graphics
			# moved to __create3DGraphics due to dependence in
			# pi3d.Shader.__init__ which calls pi3d.Loadable.is_display_thread()
			# which asserts that the thread where pi3d was loaded from
			# is the same as the thread which is calling the pi3d.Shader
			# ie, pi3d cannot be loaded in the main thread (ResourceManager constructor)
			# and then used in another thread (Book run() method)
			# https://github.com/tipam/pi3d/blob/master/pi3d/Shader.py
			# https://pi3d.github.io/html/_modules/pi3d/util/Loadable.html
			self.pi3d=None
			#Video
			#from omxplayer.player import OMXPlayer
			self.pygame=pygame
			import omxplayer.player
			#from omxplayer.player import OMXPlayer
			self.omxplayer=omxplayer.player
		self.pygame_init=False
		self.display_3d=None
		self.is_windowed=is_windowed
		self.is_keyboard=is_keyboard
		self.was_keyboard_toggle=False #retain previous state of keyboard_toggle key state (2/10/18, why was this needed...?)
		self.pygame_event=[]
		self.pygame_keys_pressed=[]
		#self.morse_sequence=[] #list of True, False the represent Morse Code sequence
		#self.morse_cleared_seconds=0 #last time that the morse code sequence was cleared
		print("ResourceManager.init: set debug: "+str(is_debug))
		self._is_debug=is_debug
		
	def update(self):
		#pygame insists on removing all events with a single method call,
		#so there is only one oportunity to fetch the keys that are pressed
		#do so here every frame
		if(not self.pygame is None):
			self.pygame_event=self.pygame.event.get()
			self.pygame_keys_pressed=self.pygame.key.get_pressed()
			#when programmer hits the tab key, toggle between listening to keyboard inputs and DI/O inputs
			for event in self.pygame_event:
				if(event.type == self.pygame.KEYDOWN and event.key == self.pygame.K_F1):
					self._is_debug=not self._is_debug
				if(event.type == self.pygame.KEYDOWN and event.key == self.pygame.K_F2):
					#take screenshot
					if(not self.pygame is None and not self.screen_2d is None):
						self.pygame.image.save(self.screen_2d,self.SCREENSHOT_PATH+"screenshot_"+str(int(time.time()))+".jpg")
				if(event.type == self.pygame.KEYDOWN and event.key == self.pygame.K_TAB):
					if(not self.was_keyboard_toggle):
						self.is_keyboard=not self.is_keyboard
					self.was_keyboard_toggle=True
		self.was_keyboard_toggle=False
		#self.updateMorse() #TODO - implement, but be mindful proctor does not use feature
		if(not self.display_3d is None):
			#print("ResourceManager.update: loop_running checkup")
			self.display_3d.loop_running()
		
	def clean(self):
		print("ResourceManager clean()")
		self.dispose()
		#needs to be 3D first then 2D, because 3D graphics has some pygame interaction/conflicts
		self.__create3Dgraphics()
		self.__create2Dgraphics()
		
	def dispose(self):
		self.pygame_event=[]
		#self.morse_sequence=[]
		#self.morse_cleared_seconds=0
		self.__dispose3Dgraphics()
		self.__dispose2Dgraphics()

	def __create2Dgraphics(self):
		print("ResourceManager: Create 2D Graphics")
		if(not self.pygame_init and not self.pygame is None):
			self.pygame_init=True
			self.pygame.init()
			self.pygame.font.init()
			self.pygame.mouse.set_visible(False)
			screen_dimensions=self.getScreenDimensions()
			#display_info=pygame.display.Info()
			if(self.is_windowed):
				self.screen_2d=self.pygame.display.set_mode(screen_dimensions)
			else:
				self.screen_2d=self.pygame.display.set_mode(screen_dimensions,self.pygame.FULLSCREEN)
			self.pygame.display.flip()
		
	def __dispose2Dgraphics(self):
		if(False): #note that pygame does not dipose() gracefully (3/11/18 forgot the exact issue...), so it is necessary to keep pyagme, and all other assets, live between playthroughs rather than doing a clean refresh each time
			self.pygame.display.quit()
			self.pygame.quit()
		
	def __create3Dgraphics(self):
		print("ResourceManager: Create 3D Graphics")
		if(self.display_3d is None): # and not self.pi3d is None
			
			#3D Graphics
			import sys
			sys.path.insert(1, '/home/pi/pi3d')
			import pi3d
			print("ResourceManager.__create3Dgraphics: Thread: "+str(threading.current_thread()))
			self.pi3d=pi3d
			
			self.display_3d = self.pi3d.Display.create(samples=self.OVERSAMPLE_RATIO_3D)
			self.display_3d.set_background(0,0,0,0)#transparent background
			
			self.camera_3d = self.pi3d.Camera(is_3d=True)
			self.camera_3d_overlay = self.pi3d.Camera(is_3d=False) #2d graphics overlay for GUI
			
			self.shader_3d = self.pi3d.Shader("uv_light") #grr, pi3d has an assertion that shaders need to be created in the same thread that pi3d was loaded in
			self.shader_3d_overlay = self.pi3d.Shader("uv_flat")
			
			print("ResourceManager.__create3dgraphics: complete")
		
	def __dispose3Dgraphics(self):
		if(False):#not self.display_3d is None):
			self.display_3d.destroy()
	
	"""
	given a filename, fetch the contents into an array or dictionaries
	with dictionary keys as the column titles
	ex: [{'key1':'value1','key2':'value2'},{'key1':'value3','key2':'value4'}]
	ref: https://www.reddit.com/r/learnpython/comments/2l07bz/help_reading_csv_file_and_putting_data_into_arrays/
	"""
	@staticmethod
	def loadCSV(filename,print_debug=False):
		import csv
		data=[]
		with open(filename) as file_obj:
			reader = csv.DictReader(file_obj, delimiter=',')
			for row in reader:
				data.append(row)
				if(print_debug):
					print(row)
		return data
		
	@staticmethod
	def loadTXT(filename):
		text_file = open(filename, "r")
		lines = text_file.readlines()
		text_file.close()
		return lines
		
	
	# -- VIDEO --
	
	#loads a video from a file, pauses the video, hides the video
	#and returns the reference, to the video player	
	def loadVideo(self,video_path,is_loop=False):
		video_args=['--no-osd','-o','local','--layer','-100']
		if(is_loop):
			video_args.append('--loop')
		print("ResourceManager.loadVideo, video args: "+str(video_args))
		#video_player=OMXPlayer(video_path,args=video_args)
		video_player=self.omxplayer.OMXPlayer(video_path,args=video_args)
		#-100 places the video player visually above the desktop and pygame, but behind pi3d
		#-o directs any any audio output out the local audio jack rather than hdmi
		#no-osd turns off on-screen displays like "play" when starting a video
		video_player.set_alpha(255)
		video_player.pause()
		#video_player.set_aspect_mode('stretch')
		return video_player
	
	#unhides the video and plays it
	def playVideo(self,video_player):
		if(video_player is None):
			print("ResourceManager.playVideo: video_player is None")
		else:
			try:
				video_player.set_alpha(0)
				video_player.play()
				return True
			except self.omxplayer.OMXPlayerDeadError:
				pass
		return False
	
	def pauseVideo(self,video_player):
		if(video_player is None):
			print("ResourceManager.pauseVideo: video_player is None")
		else:
			try:
				video_player.pause()
				video_player.set_alpha(255)
				return True
			except self.omxplayer.OMXPlayerDeadError:
				pass
		return False
	
	#change the location of the video with respect to the screen displayed to players
	def setVideoLocation(self,video_player,top_left_x,top_left_y,bottom_right_x,bottom_right_y):
		video_player.set_video_pos(top_left_x,top_left_y,bottom_right_x,bottom_right_y)
	
	#cleanly exits the current video player instance
	def disposeVideo(self,video_player):
		if(video_player is None):
			return False
		try:
			video_player.quit()
			return True
		except OMXPlayerDeadError:
			pass #silence errors about player already being closed
		return False
		
	# -- AUDIO --
	
	#pygame restricts music tracks to one-at-a-time, so queue that one file here
	def loadMusic(self,filename):
		pygame.mixer.music.load(filename)
		
	def playMusic(self):
		pygame.mixer.music.play()
		
	
	
	# -- 3D assets --
	
	#loads the 3D asset into memory and returns a pointer
	#if object has already been loaded in this playthrough, returns the existing
	# 3D object reference instead of loading another instance
	def get3dAsset(self,filename):
		pass
	
	# -- RPi Environment --
	
	def getCPU_Temperature(self):
		pass
		
	def getGPU_Temperature(self):
		pass
		
	def getRAM_Usage(self):
		pass
		
	#query user and programmer inputs to determine if a STOP command has been placed
	def isStopped(self):
		for event in self.pygame_event:
			if(event.type == self.pygame.KEYDOWN and event.key == self.pygame.K_ESCAPE):
				return True
		return False
		
	#pressing the enter/return key advances to the next chapter
	def isNextChapter(self):
		for event in self.pygame_event:
			if(event.type == self.pygame.KEYDOWN and (event.key == self.pygame.K_RETURN or
													  event.key == self.pygame.K_KP_ENTER)):
				return True
		return False
		
	def isDotPressed(self,is_keyboard=None):
		if(is_keyboard is None): is_keyboard=self.is_keyboard
		if(is_keyboard):
			if(self.pygame_keys_pressed[self.pygame.K_PERIOD]): return True
		else:
			if(self.__readPin(DI_PINS.BUTTON_DOT)): return True
		return False
			
	def isDashPressed(self,is_keyboard=None):
		if(is_keyboard is None): is_keyboard=self.is_keyboard
		if(is_keyboard):
			if(self.pygame_keys_pressed[self.pygame.K_MINUS]): return True
		else:
			if(self.__readPin(DI_PINS.BUTTON_DASH)): return True
		return False
		
	#True if depressed (eletrical contact between weak pull-up and GND)
	#False if button is NOT depressed (eletrical pull-up is the only input)
	def __readPin(self,pin_enum):
		out=self.wp.digitalRead(pin_enum.value)
		return 1-out
		
	#returns a list of 0, 1 or 2 elements.  List of two are orthogonal directions.  ex:
	#[] #no direction selected
	#[IO_Manager.NORTH] #only north selected
	#[IO_Manager.SOUTH,IO_Manager.WEST] #southwest
	#when using is_keyboard, then the following keys are assigned:
	#DIRECTION: numpad 8,4,5,6 for up, left, down, right
	#LASER: w,a,s,d,space for up, left, down, right, fire
	#CAMERA: arrow keys up, left, down, right
	def getJoystickDirection(self,joystick,is_keyboard=None):
		if(is_keyboard is None): is_keyboard=self.is_keyboard
		directions=[]
		if(is_keyboard):
			if(joystick==DEVICE.DIRECTION):
				if(self.pygame_keys_pressed[self.pygame.K_KP8]): directions.append(DIRECTION.NORTH)
				if(self.pygame_keys_pressed[self.pygame.K_KP5]): directions.append(DIRECTION.SOUTH)
				if(self.pygame_keys_pressed[self.pygame.K_KP6]): directions.append(DIRECTION.EAST)
				if(self.pygame_keys_pressed[self.pygame.K_KP4]): directions.append(DIRECTION.WEST)
			elif(joystick==DEVICE.CAMERA):
				if(self.pygame_keys_pressed[self.pygame.K_UP]): directions.append(DIRECTION.NORTH)
				if(self.pygame_keys_pressed[self.pygame.K_DOWN]): directions.append(DIRECTION.SOUTH)
				if(self.pygame_keys_pressed[self.pygame.K_RIGHT]): directions.append(DIRECTION.EAST)
				if(self.pygame_keys_pressed[self.pygame.K_LEFT]): directions.append(DIRECTION.WEST)
			elif(joystick==DEVICE.LASER):
				if(self.pygame_keys_pressed[self.pygame.K_w]): directions.append(DIRECTION.NORTH)
				if(self.pygame_keys_pressed[self.pygame.K_s]): directions.append(DIRECTION.SOUTH)
				if(self.pygame_keys_pressed[self.pygame.K_d]): directions.append(DIRECTION.EAST)
				if(self.pygame_keys_pressed[self.pygame.K_a]): directions.append(DIRECTION.WEST)
			else:
				raise ValueError("Invalid joystick enum: "+str(joystick))
		else:
			if(joystick==DEVICE.DIRECTION):
				if(self.__readPin(DI_PINS.DIRECTION_JOYSTICK_0)): directions.append(DIRECTION.NORTH)
				if(self.__readPin(DI_PINS.DIRECTION_JOYSTICK_1)): directions.append(DIRECTION.SOUTH)
				if(self.__readPin(DI_PINS.DIRECTION_JOYSTICK_2)): directions.append(DIRECTION.EAST)
				if(self.__readPin(DI_PINS.DIRECTION_JOYSTICK_3)): directions.append(DIRECTION.WEST)
			elif(joystick==DEVICE.CAMERA):
				if(self.__readPin(DI_PINS.CAMERA_JOYSTICK_0)): directions.append(DIRECTION.NORTH)
				if(self.__readPin(DI_PINS.CAMERA_JOYSTICK_1)): directions.append(DIRECTION.SOUTH)
				if(self.__readPin(DI_PINS.CAMERA_JOYSTICK_2)): directions.append(DIRECTION.EAST)
				if(self.__readPin(DI_PINS.CAMERA_JOYSTICK_3)): directions.append(DIRECTION.WEST)
			elif(joystick==DEVICE.LASER):
				if(self.__readPin(DI_PINS.LASER_JOYSTICK_0)): directions.append(DIRECTION.NORTH)
				if(self.__readPin(DI_PINS.LASER_JOYSTICK_1)): directions.append(DIRECTION.SOUTH)
				if(self.__readPin(DI_PINS.LASER_JOYSTICK_2)): directions.append(DIRECTION.EAST)
				if(self.__readPin(DI_PINS.LASER_JOYSTICK_3)): directions.append(DIRECTION.WEST)
			else:
				raise ValueError("Invalid joystick enum: "+str(joystick))
		if(DIRECTION.NORTH in directions and DIRECTION.SOUTH in directions):
			directions.remove(DIRECTION.NORTH)
			directions.remove(DIRECTION.SOUTH)
		if(DIRECTION.EAST in directions and DIRECTION.WEST in directions):
			directions.remove(DIRECTION.EAST)
			directions.remove(DIRECTION.WEST)
		return directions
		
	#return true of the joystick has the fire button depressed
	def isFirePressed(self,joystick,is_keyboard=None):
		if(is_keyboard is None): is_keyboard=self.is_keyboard
		if(is_keyboard):
			if(joystick==DEVICE.DIRECTION):
				pass
			elif(joystick==DEVICE.CAMERA):
				pass
			elif(joystick==DEVICE.LASER):
				if(self.pygame_keys_pressed[self.pygame.K_SPACE]): return True
			else:
				raise ValueError("Invalid joystick enum: "+str(joystick))
		else:
			if(joystick==DEVICE.DIRECTION):
				pass
			elif(joystick==DEVICE.CAMERA):
				pass
			elif(joystick==DEVICE.LASER):
				if(self.__readPin(DI_PINS.LASER_JOYSTICK_FIRE)): return True
			else:
				raise ValueError("Invalid joystick enum: "+str(joystick))
		return False
		
	
	def isLightPuzzleInputActive(self,input_index,is_keyboard=None):
		if(is_keyboard is None): is_keyboard=self.is_keyboard
		if(is_keyboard):
			if(input_index==0):
				return self.pygame_keys_pressed[self.pygame.K_1]>0
			elif(input_index==1):
				return self.pygame_keys_pressed[self.pygame.K_2]>0
			elif(input_index==2):
				return self.pygame_keys_pressed[self.pygame.K_3]>0
			elif(input_index==3):
				return self.pygame_keys_pressed[self.pygame.K_4]>0
			else:
				raise ValueError("Invalid input queried, light puzzle index: "+str(input_index))
		else:
			if(input_index==0):
				if(self.__readPin(DI_PINS.LIGHT_0)): return True
			elif(input_index==1):
				if(self.__readPin(DI_PINS.LIGHT_1)): return True
			elif(input_index==2):
				if(self.__readPin(DI_PINS.LIGHT_2)): return True
			elif(input_index==3):
				if(self.__readPin(DI_PINS.LIGHT_3)): return True
			else:
				raise ValueError("Light puzzle input not yet implemented: "+str(input_index))
		return False
	
	# **Aditya Edit** moved Morse sequence handling to MorseCode.py
	#
	#a list of morse code key presses are maintained internally
	#update the list here based on user inputs
	#def updateMorse(self):
	#	is_dot=self.isDotPressed()
	#	is_dash=self.isDashPressed()
	#	if(is_dot and is_dash):
	#		self.morse_sequence=[] #if both keys are down, clear entry
	#		self.morse_cleared_seconds=time.time()
	#	elif(is_dot):
	#		self.morse_sequence.append(False)
	#	elif(is_dash):
	#		self.morse_sequence.append(True)
	#	else:
	#		pass
			
		
	#def getMorse(self):
	#	return self.morse_sequence
		
	#indicates whether IO_Manager is listening for inputs from the keyboard or from DI/O pins
	def isKeyboard(self): return self.is_keyboard
	
	#return tuple with (width,height)
	def getScreenDimensions(self):
		if(not self.pygame is None):#attempt 2d fetch
			display_info=self.pygame.display.Info()
			return (int(display_info.current_w),int(display_info.current_h))
		else:#attempt 3d fetch
			display_info=self.display_3d
			return (int(display_info.width),int(display_info.height))

	#debug includes on-screen-displays
	@property
	def is_debug(self): return self._is_debug
		
	@is_debug.setter
	def is_debug(self,value): self._is_debug=value
		#raise ValueError("Debug mode cannot be set except by the book in response to an external command: either as TCP, within the terminal command, or in response to the F1 key")

if __name__ == "__main__":
	#io=IO_Manager(None)
	#io.clean()
	#print("stopped: "+str(io.isStopped()))
	rm=ResourceManager.loadCSV('configuration_map_connections.csv')
	print(rm)
	
