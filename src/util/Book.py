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
#from util.IO_Manager import IO_Manager #interface for reading button state
from util.ResourceManager import ResourceManager #wrapper for fetching art assets
from util.CommunicationManager import CommunicationManager#interface for receiving external commands from Proctor or Wall computer
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
	DEFAULT_COUNTDOWN_DURATION_SECONDS=65*60
	MAX_COUNTDOWN_DURATION_FOR_SUCCESS_SECONDS=60*60 #if playing longer than this, playthrough is a failure
	#note: timer is only active within the Wall Book
	#timer is started by the Wall.Standby chapter exiting()
	#timer is ended by Credits entering()
	#all other timer interactions are managed by the Wall Book, not chapters
	
	#VARIABLES
	
	#CONSTRUCTOR
	
	# this_book_type - an ENUM defining 
	def __init__(self,this_book_type,is_debug,is_windowed,is_keyboard):
		print("Book.__init__: Hello World")
		#configure variables
		self._is_alive=True
		self._book_type=this_book_type
		self.playthrough_index=0 #this is the number of playthroughs completed
		self._index_next_chapter=0 #next chapter to play after the current one completes
		
		#configure lists and object consuctors
		self._is_ready=threading.Event()
		self._is_ready.clear()
		self._visible_chapter=None #pointer to currently running chapter
		self._resource_manager=ResourceManager(self.book_type,is_debug,is_windowed,is_keyboard)
		#self._io_manager=IO_Manager(self.book_type,is_debug_enabled)
		self._chapter_list=self.__get_all_chapters(self.book_type,self.resource_manager)
		self._communication_manager=CommunicationManager(self)
		
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
		#variables to track the state of the countdown timer
		self.cleanCountdown()
		self._index_next_chapter=0 #index of the next chapter within _chapter_list
		self._playthrough_start_unix_seconds=0 #cont time from a specific Proctor-commanded epoc
		self._playthrough_time_offset_seconds=0 #allow for proctor to add/subtract time
		self.__cleanSlaves()
		#self._io_manager.clean()
		self.resource_manager.clean()
		for chapter in self._chapter_list:
			chapter.clean()
		self._communication_manager.clean()
	
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
		self.resource_manager.dispose()
		#self._io_manager.dispose()
	
	def run(self):
		while(self.is_alive): #for each playthrough
			#step out of current chapter and into next chapter when ready
			chapter_empty_or_error=self._visible_chapter is None or not isinstance(self._visible_chapter,Chapter)
			chapter_done=False if chapter_empty_or_error else self._visible_chapter.is_done
			if(chapter_empty_or_error or chapter_done):
				#if(chapter_done):
				#	self._visible_chapter.exitChapter() #only called after the end of a chpater
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
					self.resource_manager.update() #used to look for things like the programmer hitting the tab key
					if(self.resource_manager.isStopped()):
						self.is_alive=False
					if(self.resource_manager.isNextChapter()):
						self._visible_chapter.is_done=True
					if(this_frame_number==0):
						this_frame_elapsed_seconds=0
						last_frame_elapsed_seconds=this_frame_elapsed_seconds
						print("Book.run: frame 0")
					else:
						this_frame_elapsed_seconds=time.time()-first_frame_unix_seconds
					self._visible_chapter.update(this_frame_number,this_frame_elapsed_seconds,last_frame_elapsed_seconds)
					#only draw if book is alive and chapter is not done
					if(self.is_alive and not self._visible_chapter.is_done):
						self._visible_chapter.draw()
						#self.overlay_draw()
					if(self.isCountdownExpired()):
						self.goToPlaythroughEnd()
					this_frame_number+=1
					last_frame_elapsed_seconds=this_frame_elapsed_seconds
				#if(not self.is_alive): #dirty exit
				self._visible_chapter.exitChapter()
			if(self._index_next_chapter>=len(self._chapter_list)): 
				print("Book: Playthrough "+str(self.playthrough_index)+" complete")
				self.playthrough_index+=1
		self.dispose()
	
	"""
	executes the external command
	DEBUG calls this method directly
	MASTER sends a command to CommunicationManager, which then executes this method
	
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
	def executeCommand(self,json_cmd):
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
				chapter_index=self.__getChapterIndexByTitle(seek_chapter_name)
				#for chapter_index_iter in range(len(self._chapter_list)):
				#	this_chapter=self._chapter_list[chapter_index_iter]
				#	if(this_chapter.getTitle() == seek_chapter_name):
				#		chapter_index=chapter_index_iter
				#		break #use the first matching chapter
				if(chapter_index<0):
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
		
	#given a Chapter title string, return the index within theis books' chapter list
	# return -1 if not found
	def __getChapterIndexByTitle(self,seek_chapter_name):
		chapter_index=-1
		for chapter_index_iter in range(len(self._chapter_list)):
			this_chapter=self._chapter_list[chapter_index_iter]
			if(this_chapter.getTitle() == seek_chapter_name):
				chapter_index=chapter_index_iter
				break #use the first matching chapter
		return chapter_index
		
	def setNextChapterByTitle(self,chapter_name):
		json_cmd={"command":"set_next_chapter","parameters":{"by_title":chapter_name}}
		self.executeCommand(json.dumps(json_cmd))
	
	def goToNextChapter(self):
		json_cmd={"command":"go_to_next_chapter"}
		self.executeCommand(json.dumps(json_cmd))
	
	#list of chapters in order as they will be played in the book
	def __get_all_chapters(self,this_book_type,resource_manager):
		#only create if not already initialized
		if(this_book_type==BOOK_TYPE.WALL):
			return [
				chapters.wall.Standby.Standby(self),
				chapters.wall.LightPuzzle.LightPuzzle(self),
				chapters.wall.Tutorial.Tutorial(self),
				chapters.wall.Snake.Snake(self),
				chapters.wall.Hyperspace.Hyperspace(self),
				chapters.wall.Credits.Credits(self)
			]
		elif(this_book_type==BOOK_TYPE.HELM):
			return [ #Wall book assumes the sane number of chapters exist in the Helm book
				#chapters.helm.Standby.Standby(self),
				#chapters.helm.MorseCode.MorseCode(self),
				#chapters.helm.BlackScreen.BlackScreen(self,"Tutorial"),
				#chapters.helm.BlackScreen.BlackScreen(self, "Snake"),
				chapters.helm.Map.Map(self),
				#chapters.helm.BlackScreen.BlackScreen(self, "Credits")
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
	
	#delay single-threaded operations until the book is ready to receive commands
	#advise using this only for debugging
	def waitUntilReady(self):
		self._is_ready.wait() #I would prefer this also check if is_alive is still True...
	
	#reset timer state to default
	def cleanCountdown(self):
		self.countdown_start_seconds=0
		self.countdown_end_seconds=0
		self.max_countdown_seconds=self.DEFAULT_COUNTDOWN_DURATION_SECONDS
	
	#begin the 60-ish minute countdown
	def startCountdown(self,start_time_seconds=None):
		if(start_time_seconds is None): start_time_seconds=time.time()
		if(self.countdown_start_seconds>0): return #only start if not already started
		self.countdown_start_seconds=start_time_seconds
		
	#command the timer to stop counting down
	def endCountdown(self,end_time_seconds=None):
		if(end_time_seconds is None): end_time_seconds=time.time()
		if(self.countdown_end_seconds>0): return #only end if not already ended
		self.countdown_end_seconds=end_time_seconds
	
	#extend the countdown timer (seconds) so the playthrough is longer before auto-exiting
	def extendPlaythrough(self,seconds):
		self.max_countdown_seconds=self.max_countdown_seconds+seconds
	
	#if countdown is expired, return True, else return False
	def isCountdownExpired(self):
		if(not self._book_type==BOOK_TYPE.WALL): return False
		if(self.countdown_start_seconds<=0): return False
		if(self.countdown_end_seconds>0): return False
		return self.getCountdownElapsed()>=self.max_countdown_seconds
		
	#get the time used to complete the room in seconds
	def getCountdownElapsed(self):
		if(self.countdown_start_seconds==0): return 0
		latest_time=time.time()
		if(self.countdown_end_seconds>0):
			latest_time=self.countdown_end_seconds
		return max(0,min(self.max_countdown_seconds,latest_time-self.countdown_start_seconds))
	
	#get the time remining to complete the playthrough in seconds
	def getCountdownRemaining(self):
		return self.max_countdown_seconds-self.getCountdownElapsed()
	
	#return True if the playthrough was completed within the max window (successful run) 
	def isSuccessfulPlaythrough(self):
		return self.getCountdownElapsed()<self.MAX_COUNTDOWN_DURATION_FOR_SUCCESS_SECONDS
	
	#if not already on Credits, jump to credits
	def goToPlaythroughEnd(self):
		if(not self.isAtPlaythroughEnd()):
			self.setNextChapterByTitle("Credits")
			self.goToNextChapter()
		
	#return True if book is at or beyond the Credits
	def isAtPlaythroughEnd(self):
		current_chapter_index=self._chapter_list.index(self._visible_chapter)
		#credits_index=-1
		#for chapter_index in range(len(self._chapter_list)):
		#	if(self._chapter_list[chapter_index].getTitle()=="Credits"):
		#		credits_index=chapter_index
		#		break
		credits_index=self.__getChapterIndexByTitle("Credits")
		if(credits_index<0):
			raise ValueError("Unable to find index of Credits Chapter within this Book")
		return current_chapter_index>=credits_index
	
	#GET/SET
	
	def getTitle(self):
		return self._book_type.name
		
	#if True, then keyboard inputs are used for player inputs
	#if False, DI/O inputs are used for player inputs
	#can be toggled anytime by pressing the TAB key
	def setKeyboard(self,value):
		self.resource_manager.is_keyboard=value
		
	#debug includes on-screen-displays
	@property
	def is_debug(self): return self.resource_manager.is_debug
		
	@is_debug.setter
	def is_debug(self,value): self.resource_manager.is_debug=value
		
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
	
	#@property
	#def io_manager(self): return self._io_manager
	
	#@io_manager.setter
	#def io_manager(self,value):
	#	raise ValueError("Changing io_manager after initialization is not supported: "+str(value))
		
	@property
	def resource_manager(self): return self._resource_manager
	
	@resource_manager.setter
	def resource_manager(self,value):
		raise ValueError("Changing resource_manager after initialization is not supported: "+str(value))
	
