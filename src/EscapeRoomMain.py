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
This class is responsible for initializing a thread and running the escape room operations within that thread
Encapsulating all processes within a thread allows for asyncronous debugging operations

Usage:
my_main=Main(0)
my_main.start() #creates a DEBUG BOOK_TYPE per the ENUM definition in Book
time.sleep(5)
my_main.is_live=False
"""

import time
import threading
from util.Book import Book, BOOK_TYPE

class Main(threading.Thread):
	
	def __init__(self,this_book_type):
		threading.Thread.__init__(self)
		print("Main.__init__: Hello World")
		#configure constants
		
		#configure lists and objects
		self.my_book=Book(BOOK_TYPE(this_book_type))
		
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
		self.my_book.is_alive=False
	
print("Main: START")
my_main=Main(0)
my_main.start()
for iter in range(2):
	time.sleep(1)
	print("Main: "+str(iter))
my_main.dispose()
print("Main: DONE")

