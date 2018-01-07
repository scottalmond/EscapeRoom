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
   
Purpose: Provides the interface between the Chapters and the TCP socket; used to execute a series of Chapters
Serves as the MASTER to the SLAVE chapters by calling initialize, clean, update and draw methods
Coordinates preparation, execution and disposal of Chapters

Usage:
from util.Book import Book
book=Book(BOOK_TYPE)
book.start()
book.dispose()
"""

#supporting libraries
from enum import Enum #for Enum references like book type
import time

#custom support assets
from util.IO_Manager import IO_Manager #interface for reading button state
from util.ResourceManager import ResourceManager #wrapper for fetching art assets
from util.MasterListener import MasterListener#interface for receiving external commands from Proctor or Wall computer
from util.Chapter import Chapter

#Wall Chapters
import chapters.wall.Standby
import chapters.wall.LightPuzzle
import chapters.wall.Tutorial
import chapters.wall.Snake
import chapters.wall.Hyperspace
import chapters.wall.Credits
import chapters.wall.CorporateLogo

#Helm Chapters
import chapters.helm.Standby
import chapters.helm.MorseCode
import chapters.helm.BlackScreen
import chapters.helm.Map

class BOOK_TYPE(Enum):
	WALL=0 #for running operationally on main monitor
	HELM=1 #for running operationally on auxilary monitor

class Book:
	#CONSTANTS
	
	#VARIABLES
	
	#CONSTRUCTOR
	
	# this_book_type - an ENUM defining 
	def __init__(self,this_book_type):
		print("Book.__init__: Hello World")
		#configure variables
		self._is_alive=True
		self._book_type=this_book_type
		self._is_running=False
		self.playthrough_index=0 #this is the number of playthroughs completed
		self._index_next_chapter=0 #next chapter to play after the current one completes
		
		#configure lists and object consuctors
		self._visible_chapter=None #pointer to currently running chapter
		self._resource_manager=ResourceManager()
		self._io_manager=IO_Manager(self.book_type)
		self._chapter_list=self.__get_all_chapters(self.book_type,self._resource_manager,self._io_manager)
		self._master_listener=MasterListener(self)
		
	#METHODS
	
	
	"""
	kicks off threads and other resource/time-heavy tasks
	"""
	def start(self):
		#initialize objects
		#self.clean()
		self.run()
	
	def clean(self):
		self._index_next_chapter=0 #index of the next chapter within _chapter_list
		self._playthrough_start_unix_seconds=0 #cont time from a specific Proctor-commanded epoc
		self._playthrough_time_offset_seconds=0 #allow for proctor to add/subtract time
		self.__cleanSlaves()
		self._io_manager.clean()
		self._resource_manager.clean()
		for chapter in self._chapter_list:
			chapter.clean()
		self._master_listener.clean()
	
	def dispose(self):
		self.__disposeSlaves()
		for chapter in self._chapter_list:
			chapter.dispose()
		# master_listener will self-dispose when book.is_alive becomes False
		self._resource_manager.dispose()
		self._io_manager.dispose()
	
	def run(self):	
		self._is_running=True
		while(self.is_alive): #for each playthrough
			#step out of current chapter and into next chapter when ready
			chapter_empty_or_error=self._visible_chapter is None or not isinstance(self._visible_chapter,Chapter)
			chapter_done=False if chapter_empty_or_error else self._visible_chapter.is_done
			if(chapter_empty_or_error or chapter_done):
				if(chapter_done):
					self._visible_chapter.is_visible=False
				if(self._index_next_chapter<0 or self._index_next_chapter>=len(self._chapter_list)):
					self._index_next_chapter=0#prevent illegal values from being used as indexes
				#if proceeding to first chapter, clean all chapters
				#(ie, if at end of playthrough, where Book will wait at chapter
				#zero for a proctor command, then clean all resource usage)
				if(self._index_next_chapter==0): 
					self.clean()
				self._visible_chapter=self._chapter_list[self._index_next_chapter]
				#Queue the next chapter now
				self._index_next_chapter=self._index_next_chapter+1
				self._visible_chapter.is_visible=True
				frame_number=0
				seconds_since_last_frame=0
				while(self.is_alive and not self._visible_chapter.is_done):
					this_frame_unix_seconds=time.time()
					if(frame_number==0): last_frame_unix_seconds=this_frame_unix_seconds
					seconds_since_last_frame=this_frame_unix_seconds-last_frame_unix_seconds
					last_frame_unix_seconds=this_frame_unix_seconds
					self._visible_chapter.update(frame_number,seconds_since_last_frame)
					#only draw if book is alive and chapter is not done
					if(self.is_alive and not self._visible_chapter.is_done):
						self._visible_chapter.draw(frame_number,seconds_since_last_frame)
						#self.overlay_draw()
					frame_number=frame_number+1
			print("Book: Playthrough number "+str(self.playthrough_index)+" complete")
			self.playthrough_index+=1
					

	#list of chapters in order as they will be played in the book
	def __get_all_chapters(self,this_book_type,resource_manager,io_manager):
		#only create if not already initialized
		if(this_book_type==BOOK_TYPE.WALL):
			return [
				chapters.wall.Standby.Standby(self,resource_manager,io_manager), #chapter 0
				chapters.wall.LightPuzzle.LightPuzzle(self,resource_manager,io_manager), #chapter 1
				#chapters.wall.Tutorial.Tutorial(self),
				#chapters.wall.Snake.Snake(self),
				#chapters.wall.Hyperspace.Hyperspace(self),
				#chapters.wall.Credits.Credits(self),
				#chapters.wall.CorporateLogo.CorporateLogo(self)
			]
		elif(this_book_type==BOOK_TYPE.HELM):
			return [ #Wall book assumes the sane number of chapters exist in the Helm book
				chapters.helm.Standby.Standby(self), #chapter 0
				chapters.helm.MorseCode.MorseCode(self), #chapter 1
				chapters.helm.BlackScreen.BlackScreen(self),
				#chapters.helm.BlackScreen.BlackScreen(self),
				#chapters.helm.Map.Map(self),
				#chapters.helm.BlackScreen.BlackScreen(self),
				#chapters.helm.BlackScreen.BlackScreen(self)
			]
		raise ValueError("Book chapters have not been specified for book_type: "+str(this_book_type))
	
	def __cleanSlaves(self):
		pass #Need to notify Helm via TCP to perform clean: set next chapter to zero and current chapter to done
	
	def __disposeSlaves(self):
		pass #Need to notify Helm via TCP that play has ceased
	
	def get_current_chapter_index(self):
		for chapter_iter in range(len(self._chapter_list)):
			chapter=self._chapter_list(chapter_iter)
			if(self._visible_chapter==chapter): return chapter_iter
		return -1
	
	def __create_TCP_listener(self,this_book_type):
		#only create if not already initialized
		if(self._tcp_listener is None):
			pass
	
	#GET/SET
	
	@property
	def is_alive(self): return self._is_alive

	@is_alive.setter
	def is_alive(self, value):
		if(not value):
			self._is_alive = False
			self.dispose()
		else:
			#only allow external actors to set is_alive to False to
			#avoid conflicting access/revival in multi-threaded environment
			raise ValueError("Cannot configure is_alive to: "+str(value))
	
	@property
	def book_type(self): return self._book_type
	
	@book_type.setter
	def book_type(self,value):
		raise ValueError("Changing book_type after initialization is not supported: "+str(value))
		
