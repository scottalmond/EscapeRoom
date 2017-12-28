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
		self._is_done=False
		self._this_book=this_book

	@abstractmethod
	def update(self):
		pass
		
	@abstractmethod
	def draw(self):
		pass

	@abstractmethod
	def clean(self):
		pass
		
	@abstractmethod
	def dispose(self):
		pass

	@property
	def is_done(self):
		return self._is_done

	@is_done.setter
	def is_done(self, value):
		self._is_done = value
