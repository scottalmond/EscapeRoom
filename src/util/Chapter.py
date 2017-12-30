"""
Author: Scott Almond
Date: December 27, 2017

Purpose:
This is an abstract base class that all Chapters inherent from

Usage:
from chapters.Chapter import Chapter
class CLAZZ_NAME(Chapter):

"""

from abc import ABC, abstractmethod

class Chapter():
	def __init__(self,this_book):
		print("Chapter: Hello World")
		self._this_book=this_book
		self.clean()
	
	#called every frame by the Book to update the cahpter state
	#prior to calling draw()
	@abstractmethod
	def update(self):
		pass
	
	#called to render graphics only	
	@abstractmethod
	def draw(self):
		pass

	#called between chapters in a normal play-through
	#intended as a fast-response method to set variables
	#(run time may lag the graphics displayed to users)
	#not load assets - for asset loads, use reset()
	@abstractmethod
	def clean(self):
		self._is_done=False
	
	#called between play-throughs and prior to first play through
	#method run time is not a limitation
	@abstractmethod
	def reset(self):
		pass
	
	#discontinue asset use, stop treads and async processes in preparation
	#for a clean exit to the terminal
	@abstractmethod
	def dispose(self):
		pass

	#during a single chapter run
	@property
	def is_done(self):
		return self._is_done

	@is_done.setter
	def is_done(self, value):
		self._is_done = value
