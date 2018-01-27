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
my_main.dispose() #or press ESCAPE key instead

python3 EscapeRoomMain.py False WALL Hyperspace
is_debug = False
book_type = Wall
chapter_name = Hyperspace
"""

import json
import sys
import time
import threading
from util.Book import Book, BOOK_TYPE
import distutils.util

class Main(threading.Thread):
	
	def __init__(self,this_book_type,is_debug_enabled):
		threading.Thread.__init__(self)
		print("Main.__init__: Hello World")
		#configure constants
		
		#configure lists and objects
		self.my_book=Book(BOOK_TYPE(this_book_type),is_debug_enabled)
		
	"""
	Extends Thread
	"""
	def run(self):
		self.my_book.start()
		#self.__dispose()
	
	def wait_for_book(self):
		self.my_book.wait_until_ready()
		
	#if True, use keyboard inputs for player controls
	#if False, use DI/O inputs for player controls
	def setKeyboard(self,value):
		self.my_book.setKeyboard(value)
	
	def go_to_chapter_by_name(self,chapter_name):
		json_cmd={"command":"set_next_chapter","parameters":{"by_title":chapter_name}}
		self.my_book.execute_command(json.dumps(json_cmd))
		json_cmd={"command":"go_to_next_chapter"}
		self.my_book.execute_command(json.dumps(json_cmd))
		pass
	
	"""
	Close references to open environmental variables
	Do so in reverse order from init()
	"""
	def dispose(self):
		self.my_book.is_alive=False

if __name__ == "__main__":
	print("Main: START")
	is_debug_enabled=bool(distutils.util.strtobool(sys.argv[1]))
	book_type=str(sys.argv[2])
	if(book_type=="Wall"):
		book_type=0
	elif(book_type=="Helm"):
		book_type=1
	else:
		raise ValueError("Book type not defined: "+book_tye)
	go_to_chapter=False
	if(len(sys.argv)>3):
		go_to_chapter=True
		chapter_name=str(sys.argv[3])
	my_main=Main(book_type,is_debug_enabled)
	my_main.start()
	my_main.wait_for_book()
	my_main.setKeyboard(True)
	if(go_to_chapter):
		time.sleep(1) #if first chapter plays video, the video load/unload will take time
		#trying to change chapters shortly after entering will cause a segmentation fault
		my_main.go_to_chapter_by_name(chapter_name)
	print("Main: DONE")



