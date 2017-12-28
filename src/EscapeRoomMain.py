"""
Author: Scott Almond
Date: December 26, 2017

Purpose: 
This class is responsible for initializing a thread and running the escape room operations within that thread
Encapsulating all processes within a thread allows for asyncronous debugging operations

Usage:
Main(0).start() #creates a DEBUG BOOK_TYPE per the ENUM definition in Book
"""

import time
import threading
from util.Book import Book

class Main(threading.Thread):
	
	def __init__(self,this_book_type):
		threading.Thread.__init__(self)
		print("Main.__init__: Hello World")
		#configure constants
		
		#configure lists and objects
		self.my_book=Book(this_book_type)
		
	"""
	Extends Thread
	"""
	def run(self):
		self.__init()
		#self.__main()
		#self.__dispose()
	
	"""
	Create Environment and Book
	"""
	def __init(self):
		self.my_book.init()
	
	"""
	Loop execution here until ready to exit
	"""
	def __main(self):
		while(not self.__isStopped()):
			print("Main: HERE")
			self.my_book.run()
			time.sleep(3.0)
	
	"""
	Close references to open environmental variables
	Do so in reverse order from init()
	"""
	def __dispose(self):
		self.my_book.dispose()
	
Main(0).start()	
