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
This is an abstract base class that all Chapters inherent from

Usage:
for chapter in book
	chapter=Chapter() #chapter is created
for playthrough=1:inf
	for chapter in book
		chapter.clean() #chapter is given dedicated time for
		#resource/time-intensive tasks to reset the chapter assets for the next play through
		#chapter is prepared and transitions to standby
	for chapter in book
		enterChapter() #chapter now has control of the screen
		while(!chapter.is_done)
			chapter.update() #one step of the game state
			chapter.draw() #one frame rendered
		exitChapter() #chapter no longer has control of the screen
for chapter in book
	chapter.dispose(True) #chapter releases all resources, assets, threads, etc

"""

from abc import ABC, abstractmethod
import math
import numpy as np

class Chapter():
	UTIL_ASSET_FOLDER='util/assets/'
	FONT_3D_FILENAME='CenturyGothicBold.ttf'#'NotoSans-Regular.ttf'
	
	@abstractmethod
	def __init__(self,this_book,book_title=None):
		#print("Chapter: Hello World")
		self._is_done=False
		self._book=this_book
		self._resource_manager=None if this_book is None else this_book.resource_manager
		#print("Chapter.io: "+str(this_book.io_manager))
		#self._io_manager=this_book.io_manager
		self.my_title=book_title

	#called immmediately prior to updating/drawing frames
	#method should execute very quickly, ~<30 ms (no asset loads)
	def enterChapter(self,unix_time_seconds):
		print("Book."+str(self.getTitle())+".enterChapter()")
		self._is_visible=True
	
	#called every frame by the Book to update the chapter state
	#prior to calling draw()
	@abstractmethod
	def update(self,this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds): pass
	
	#called to render one frame
	@abstractmethod
	def draw(self): pass
	
	#called after last frame draw for this chapter in this playthrough
	#method should execute very quickly, ~<30 ms (no asset loads/dumps)
	def exitChapter(self):
		self._is_visible=False

	#called between play-throughs and prior to first play through
	#method run time is not a limitation
	def clean(self):
		self._is_done=False
		self._osd_debug_strings=[]
		
		#on-screen graphics debug tools
		#2d
		self._debug_font=None if self.rm.pygame is None else self.rm.pygame.font.SysFont('Comic Sans MS',70)
		self._debug_font_color=(0,255,0)
		self._debug_font_line_height_px=0 if self.rm.pygame is None else self._debug_font.get_height()
		
		#3d (on screen display overlay)
		MAX_NUM_CHARACTERS_PER_LINE=40
		FONT_SIZE_3D=70
		font_path=self.UTIL_ASSET_FOLDER+self.FONT_3D_FILENAME
		self._debug_font_3d=None if self.rm.pi3d is None else self.rm.pi3d.Font(font_path, self._debug_font_color, codepoints=list(range(32,128)))
		self._debug_point_text_3d_overlay = self.rm.pi3d.PointText(self._debug_font_3d,self.rm.camera_3d_overlay, max_chars=200, point_size=FONT_SIZE_3D)
		self._debug_font_line_height_px_3d_overlay=FONT_SIZE_3D
		
		screen_dims=self.rm.getScreenDimensions()
		HWIDTH=screen_dims[0]/2
		HHEIGHT=screen_dims[1]/2
		MAX_NUM_CHARACTERS_PER_LINE=40
		self._debug_block_text_3d_overlay = self.rm.pi3d.TextBlock(-HWIDTH+30, HHEIGHT-30, 0.1, 0.0, MAX_NUM_CHARACTERS_PER_LINE, #text_format="Static str",
						size=0.99, spacing="F", space=0.05, colour=(0.0, 0.0, 1.0, 1.0))
		self._debug_point_text_3d_overlay.add_text_block(self._debug_block_text_3d_overlay)
		
	#discontinue asset use, stop threads and async processes in preparation
	#for a clean exit to the terminal
	def dispose(self,is_final_call): pass
		
	#scope like "Book" or "Chapter"
	def getScope(self):
		return "Chapter"
		
	#Multiple chapters of the same class may exist (ex. Standby)
	#Differentiate them using a unique title string in the constructor
	#Default value is class name
	def getTitle(self):
		if(self.my_title is None):
			return self.__class__.__name__
		return self.my_title
		
	#list of strings to be shown on screen
	def setDebugStringList(self,string_list,this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds):
		seconds_since_last_frame=this_frame_elapsed_seconds-previous_frame_elapsed_seconds
		remaining_time_seconds=self.book.getCountdownRemaining()
		remaining_minutes=int(remaining_time_seconds/60)
		remaining_seconds=int(remaining_time_seconds%60)
		string_list.insert(0,self.book.getTitle()+"."+self.getTitle())
		string_list.insert(1,"FPS: "+str(math.floor(1/np.max((0.00001,seconds_since_last_frame)))))
		string_list.insert(2,"Frame: "+str(this_frame_number))
		string_list.insert(3,"Remaining: "+str(remaining_minutes)+" m "+str(remaining_seconds)+" s")
		self._osd_debug_strings=string_list
	
	#if debug is enabled, show debug strings on screen
	# if is_2d, use pygame 2D graphics
	# else render to pi3d text overlay layer
	def displayDebugStringList(self,is_2d=True):
		if(self.is_debug): #display debug text
			if(is_2d):
				if(not self.rm.pygame is None):
					for this_string_index in range(len(self._osd_debug_strings)):
						this_string=self._osd_debug_strings[this_string_index]
						this_y_px=this_string_index*self._debug_font_line_height_px #vertically offset each line of text
						rendered_string=self._debug_font.render(this_string,False,self._debug_font_color)
						self.rm.screen_2d.blit(rendered_string,(0,this_y_px))
			else:
				if(not self.rm.pi3d is None):
					screen_dims=self.rm.getScreenDimensions()
					HWIDTH=screen_dims[0]/2
					HHEIGHT=screen_dims[1]/2
					for this_string_index in range(len(self._osd_debug_strings)):
						this_string=self._osd_debug_strings[this_string_index]
						self._debug_block_text_3d_overlay.y=HHEIGHT-30-self._debug_font_line_height_px_3d_overlay*this_string_index
						self._debug_block_text_3d_overlay.set_text(this_string)
						self._debug_point_text_3d_overlay.regen()
						self._debug_point_text_3d_overlay.draw()
					
		
	#during a single chapter run
	@property
	def is_done(self): return self._is_done

	#is_done is reset within clean() only to allow external actors to stop chapter asyncronously
	@is_done.setter
	def is_done(self, value):
		if(not value):
			pass #silently ignore attempts to clear is_done
			#is_done can only be set to True by the Chapter or Book (asyncronously)
			#clearing of is_done occurs in super().clean()
		self._is_done = bool(value)
		
	@property
	def is_debug(self):
		return True if self.rm is None else self.rm.is_debug
	
	@is_debug.setter
	def is_debug(self, value): self.rm.is_debug=value
		
	@property
	def book(self): return self._book
	
	@book.setter
	def book(self, value):
		raise ValueError("Book pointer cannot be set except within the Chapter contrustor")
		
	@property
	def rm(self): return self._resource_manager

	@rm.setter
	def rm(self, value):
		raise ValueError("Changing resource_manager after initialization is not supported: "+str(value))
		
