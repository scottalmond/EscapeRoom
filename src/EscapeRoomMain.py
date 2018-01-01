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
		self.my_book.start()
		#self.__dispose()
	
	"""
	Close references to open environmental variables
	Do so in reverse order from init()
	"""
	def dispose(self):
		self.my_book.dispose()
	
my_main=Main(0)
my_main.start()
sleep(20)
my_main.dispose()
