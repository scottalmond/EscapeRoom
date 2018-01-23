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

class Chapter():
	
	@abstractmethod
	def __init__(self,this_book,book_title=None):
		print("Chapter: Hello World")
		self._this_book=this_book
		print("Chapter.rm: "+str(this_book.resource_manager))
		self._resource_manager=this_book.resource_manager
		print("Chapter.io: "+str(this_book.io_manager))
		self._io_manager=this_book.io_manager
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
		
	#discontinue asset use, stop threads and async processes in preparation
	#for a clean exit to the terminal
	def dispose(self,is_final_call): pass
		
	#Multiple chapters of the same class may exist (ex. Standby)
	#Differentiate them using a unique title string in the constructor
	#Default value is class name
	def getTitle(self):
		if(self.my_title is None):
			return self.__class__.__name__
		return self.my_title
		
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
		
	#during a single chapter run
	@property
	def io(self): return self._io_manager

	@io.setter
	def io(self, value):
		raise ValueError("Changing io_manager after initialization is not supported: "+str(value))
		
