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

python3 EscapeRoomMain.py WALL Hyperspace WINDOWED OSD KEYBOARD

OSD is on-screen-display (text debugging)
WINDOWED allows 2D pygame window to be moved around to see terminal errors
KEYBOARD uses the keyboard as an input device rather than DI/O

ESC - EXIT
ENTER - Next chapter
TAB - Toggle between using keyboard inputs and DI/O inputs
WASD, SPACE - Laser keyboad controls
up,left,down,right - Camera keyboard controls
Numpad 8,4,5,6 - Position keyboard controls
period (.), dash (-) - dot & dash morse code keyboard inputs
"""

import json
import sys
import time
import threading
from util.Book import Book, BOOK_TYPE
import distutils.util

class Main(threading.Thread):
	
	def __init__(self,this_book_type,is_debug,is_windowed,is_keyboard):
		threading.Thread.__init__(self)
		print("Main.__init__: Hello World")
		#configure constants
		
		#configure lists and objects
		self.my_book=Book(BOOK_TYPE(this_book_type),is_debug,is_windowed,is_keyboard)
		
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
	args=sys.argv
	if(len(args)==0): #print help
		print("No arguments provided, printing help...")
		print("")
		print("python3 EscapeRoomMain.py (Proctor/Wall/Helm) [CHAPTER_NAME] [WINDOWED] [DEBUG] [KEYBOARD]")
		print("")
		print("Arguments:")
		print("Proctor/Wall/Main: specifies which book is being emulated")
		print("CHAPTER_NAME: specifies which chapter to jump to at program start")
		print("WINDOWED: specifies whether pygame should be run in a windowed mode, useful if the program locks up and terminal access is needed")
		print("DEBUG: specifies whetehr on-screen-displays and otehr debugging tools/graphics are to be used within each chapter")
		print("KEYBOARD: specifies if inputs are to be pulled from the keyboard or not")
		print("")
		print("Keyboard commands:")
		print("  ENTER: jump to next chapter")
		print("  TAB: toggle between using KEYBOARD inputs and discrete inputs")
		print("  F1: toggle DEBUG flag")
		print("  WASD, SPACE: the five controls representing the joystick, plus fire button, from the cpatain's chair.  Requires KEYBOARD flag to be True to be active.")
		print("  UP,LEFT,DOWN,RIGHT: the joystick controls for the helm.  Requires KEYBOARD flag to be True to be active.")
		print("  NUM_8,NUM_4,NUM_5,NUM_6: numpad keys for the joystick controls for the wing stations.  Requires KEYBOARD flag to be True to be active.")
		print("  PERIOD,HYPHEN: the dot and dash inputs: . -")
	else: # run program
		print("Main: START")
		is_windowed=False
		if("WINDOWED" in args):
			is_windowed=True
			args.remove("WINDOWED")
		is_debug=False
		if("DEBUG" in args):
			is_debug=True
			args.remove("DEBUG")
		is_keyboard=False
		if("KEYBOARD" in args):
			is_keyboard=True
			args.remove("KEYBOARD")
		book_type=args[1]
		if(book_type=="Wall"):
			book_type=0
		elif(book_type=="Helm"):
			book_type=1
		else:
			raise ValueError("Book type not defined: "+book_tye)
		go_to_chapter=False
		if(len(args)>2):
			go_to_chapter=True
			chapter_name=sys.argv[2]
		my_main=Main(book_type,is_debug,is_windowed,is_keyboard)
		my_main.start()
		my_main.wait_for_book() #wait for book to be booted and past variable initialization so variables can be changed
		#my_main.setKeyboard(is_keyboard)
		if(go_to_chapter):
			#time.sleep(2) #if first chapter plays video, the video load/unload will take time
			#trying to change chapters shortly after entering will cause a segmentation fault
			my_main.go_to_chapter_by_name(chapter_name)
		print("Main: DONE")



