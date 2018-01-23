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
import json
import threading

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
	def __init__(self,this_book_type,is_debug_enabled):
		print("Book.__init__: Hello World")
		#configure variables
		self._is_alive=True
		self._book_type=this_book_type
		self.playthrough_index=0 #this is the number of playthroughs completed
		self._index_next_chapter=0 #next chapter to play after the current one completes
		self.is_debug_enabled=is_debug_enabled
		
		#configure lists and object consuctors
		self._is_ready=threading.Event()
		self._is_ready.clear()
		self._visible_chapter=None #pointer to currently running chapter
		self._resource_manager=ResourceManager()
		self._io_manager=IO_Manager(self.book_type,is_debug_enabled)
		self._chapter_list=self.__get_all_chapters(self.book_type,self._resource_manager,self._io_manager)
		self._master_listener=MasterListener(self)
		
	#METHODS
	"""
	kicks off threads and other resource/time-heavy tasks
	wrapper for run() in case Book needs to extrend Thread later
	"""
	def start(self):
		self.run()
	
	"""
	dispose of old assets (if any)
	initialize all resource-intensive assets
	"""
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
	
	"""
	external operators should call is_alive=False to ensure a clean exit
	from run()
	"""
	def dispose(self):
		print("book.dipose()")
		self.is_alive=False
		self.__disposeSlaves()
		for chapter in self._chapter_list:
			chapter.dispose(True)
		# master_listener will self-dispose when book.is_alive becomes False
		self._resource_manager.dispose()
		self._io_manager.dispose()
	
	def run(self):
		while(self.is_alive): #for each playthrough
			#step out of current chapter and into next chapter when ready
			chapter_empty_or_error=self._visible_chapter is None or not isinstance(self._visible_chapter,Chapter)
			chapter_done=False if chapter_empty_or_error else self._visible_chapter.is_done
			if(chapter_empty_or_error or chapter_done):
				if(chapter_done):
					self._visible_chapter.exitChapter()
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
				this_frame_number=0
				first_frame_unix_seconds=time.time()
				self._visible_chapter.enterChapter(first_frame_unix_seconds)
				self._is_ready.set()
				while(self.is_alive and not self._visible_chapter.is_done):
					if(self._io_manager.isStopped()):
						self.is_alive=False
					if(this_frame_number==0):
						this_frame_elapsed_seconds=0
						last_frame_elapsed_seconds=this_frame_elapsed_seconds
					else:
						this_frame_elapsed_seconds=time.time()-first_frame_unix_seconds
					self._visible_chapter.update(this_frame_number,this_frame_elapsed_seconds,last_frame_elapsed_seconds)
					#only draw if book is alive and chapter is not done
					if(self.is_alive and not self._visible_chapter.is_done):
						self._visible_chapter.draw()
						#self.overlay_draw()
					this_frame_number+=1
					last_frame_elapsed_seconds=this_frame_elapsed_seconds
				if(not self.is_alive): #dirty exit
					self._visible_chapter.exitChapter()
			print("Book: Playthrough "+str(self.playthrough_index)+" complete")
			self.playthrough_index+=1
		self.dispose()
	
	"""
	executes the external command
	DEBUG calls this method directly
	MASTER sends a command to MasterListener, which then executes this method
	
	Used for the following:
	to set the next chapter
	to move to the next chapter
	to change the time remaining to solve the room
	to change the state of a chapter
	
	expecting JSON with the following format (parameters are optional based on command):
	{"command":"COMMAND","parameters":{"PARAMETERS"}}
	
	Set the next chapter that will play after the current one is done
	Note: the current chapter will continue running as-is
	{"command":"set_next_chapter","parameters":{"by_title":"CHAPTER_STRING"}}
	
	Advance to the next queued chapter:
	{"command":"go_to_next_chapter"}
	"""
	def execute_command(self,json_cmd):
		json_dict=json.loads(json_cmd)
		if(not "command" in json_dict):
			raise ValueError("Command is malformed, missing 'command' key: "+str(json_cmd))
		command=json_dict["command"]
		parameters=None
		if("parameters" in json_dict):
			parameters=json_dict["parameters"]
		#begin switch statement
		if(command=="set_next_chapter"):
			chapter_index=None
			if("by_title" in parameters):
				seek_chapter_name=str(parameters["by_title"])
				for chapter_index_iter in range(len(self._chapter_list)):
					this_chapter=self._chapter_list[chapter_index_iter]
					if(this_chapter.getTitle() == seek_chapter_name):
						chapter_index=chapter_index_iter
						break #use the first matching chapter
				if(chapter_index is None):
					raise ValueError("Chapter title not found for command: "+str(json_cmd))
			elif("by_index" in parameters):
				chapter_index_iter=int(parameters["by_index"])
				if(chapter_index_iter<0 or chapter_index_iter>=len(elf._chapter_list)):
					raise ValueError("Chapter index out of range for command: "+str(json_cmd))
				chapter_index=chapter_index_iter
			else:
				raise ValueError("Insufficient parameters supplied for next chapter command: "+str(json_cmd))
			self._index_next_chapter=chapter_index
			print("Next chapter index set: "+str(chapter_index))
		elif(command=="go_to_next_chapter"):
			self._visible_chapter.is_done=True
			print("Next chapter go")
		
		# ... add new commands here ...
		
		else:
			ValueError("Command not implemented: "+str(json_cmd))
		
	
	#list of chapters in order as they will be played in the book
	def __get_all_chapters(self,this_book_type,resource_manager,io_manager):
		#only create if not already initialized
		if(this_book_type==BOOK_TYPE.WALL):
			return [
				chapters.wall.Standby.Standby(self), #chapter 0
				#chapters.wall.LightPuzzle.LightPuzzle(self), #chapter 1
				#chapters.wall.Tutorial.Tutorial(self),
				#chapters.wall.Snake.Snake(self),
				#chapters.wall.Hyperspace.Hyperspace(self),
				#chapters.wall.Credits.Credits(self)
			]
		elif(this_book_type==BOOK_TYPE.HELM):
			return [ #Wall book assumes the sane number of chapters exist in the Helm book
				#chapters.helm.Standby.Standby(self), #chapter 0
				#chapters.helm.MorseCode.MorseCode(self), #chapter 1
				#chapters.helm.BlackScreen.BlackScreen(self),
				#chapters.helm.BlackScreen.BlackScreen(self),
				chapters.helm.Map.Map(self),
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
	
	#delay single-threaded operations until the book is ready to receive commands
	#advise using this only for debugging
	def wait_until_ready(self):
		self._is_ready.wait() #I would prefer this also check if is_alive is still True...
	
	#GET/SET
	
	"""
	is_alive is prepended with "py_" to avoid unintended interaction with Threading.py
	"""
	@property
	def is_alive(self): return self._is_alive

	@is_alive.setter
	def is_alive(self, value):
		if(not value):
			self._is_alive = False
			#self.dispose() #need to allow natural shut down sequence order to run after life is terminated
		else:
			#only allow external actors to set is_alive to False to
			#avoid conflicting access/revival in multi-threaded environment
			raise ValueError("Cannot configure is_alive to: "+str(value))
	
	@property
	def book_type(self): return self._book_type
	
	@book_type.setter
	def book_type(self,value):
		raise ValueError("Changing book_type after initialization is not supported: "+str(value))
	
	@property
	def io_manager(self): return self._io_manager
	
	@io_manager.setter
	def io_manager(self,value):
		raise ValueError("Changing io_manager after initialization is not supported: "+str(value))
		
	@property
	def resource_manager(self): return self._resource_manager
	
	@resource_manager.setter
	def resource_manager(self,value):
		raise ValueError("Changing resource_manager after initialization is not supported: "+str(value))
	
