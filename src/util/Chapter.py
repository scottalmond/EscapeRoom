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
	chapter.dispose() #chapter releases all resources, assets, threads, etc

"""

from abc import ABC, abstractmethod

class Chapter():
	
	@abstractmethod
	def __init__(self,this_book):
		print("Chapter: Hello World")
		self._this_book=this_book
		self.clean()

	#called immmediately prior to updating/drawing frames
	def enterChapter(self): pass
	
	#called every frame by the Book to update the chapter state
	#prior to calling draw()
	@abstractmethod
	def update(self): raise NotImplementedError("Chapter abstract method not implemented: update()");
	
	#called to render one frame
	@abstractmethod
	def draw(self): raise NotImplementedError("Chapter abstract method not implemented: draw()");
	
	#called after last frame draw for this chapter in this playthrough
	#method should execute very quickly (no asset loads/dumps)
	def exitChapter(self): pass

	#called between play-throughs and prior to first play through
	#method run time is not a limitation
	def clean(self): self._is_done=False
		
	#discontinue asset use, stop threads and async processes in preparation
	#for a clean exit to the terminal
	def dispose(self): pass

	#called between chapters in a normal play-through
	#intended as a fast-response method to set variables
	#(run time may lag the graphics displayed to users)
	#not load assets - for asset loads, use clean()	
	#during a single chapter run
	@property
	def is_visible(self): return self._is_visible
	
	#overload to re-define behavior
	@is_visible.setter
	def is_visible(self, value):
		self._is_done = bool(value)
		if(self.is_done):
			self.enterChapter()
		else:
			self.exitChapter()
		
	#during a single chapter run
	@property
	def is_done(self):
		return self._is_done

	@is_done.setter
	def is_done(self, value):
		self._is_done = value
