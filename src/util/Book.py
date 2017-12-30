"""
Author: Scott Almond
Date: December 25, 2017

Purpose: Provides the interface between the Chapters and the TCP socket; used to execute a series of Chapters
Serves as the MASTER to the SLAVE chapters by calling initialize, clean, update and draw methods
Coordinates preparation, execution and disposal of Chapters

Usage:
from util.Book import Book
book=Book(BOOK_TYPE)
book.init()
book.start()
book.dispose()
"""

from enum import Enum #for Enum references like book type
import util.Environment
import util.ResourceManager

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
		
		#configure lists and object consuctors
		self._chapter_list=[]
		self._tcp_listener=None #placeholder, need to define object and create constructor
		self._io_manager=None #placeholder, need to define object and create constructor
	
	#METHODS
	
	"""
	use a stand-alone init() method to allow long-duration tasks to be
	completed in a separate method call from the constructor
	"""
	def init(self):
		#initialize objects
		self.__init_resources()
	
	def __init_resources(self):
		self.__create_all_chapters(self.book_type)
		self.__create_TCP_listener(self.book_type)
	
	def dispose(self):
		self.is_alive=False
	
	#allow easy extensibility for Book extend a Thread
	def start(self):
		self.run()
	
	def run(self):	
		pass
	
	def __create_all_chapters(self,this_book_type):
		#only create if not already initialized
		if(len(self._chapter_list)==0):
			if(this_book_type==BOOK_TYPE.WALL):
				pass
			elif(this_book_type==BOOK_TYPE.HELM):
				pass
	
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
		else:
			#only allow external actors to set is_alive to False to
			#avoid conflicting access/revival in multi-threaded environment
			raise ValueError("Cannot configure is_alive to: "+str(value))
	
	@property
	def book_type(self): return self._book_type
	
	@book_type.setter
	def book_type(self,value):
		raise ValueError("Changing book_type after initialization is not supported: "+str(value))
