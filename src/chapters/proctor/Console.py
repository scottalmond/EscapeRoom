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
Displays a GUI for the proctor to interact with
The GUI allows the proctor to send and receive commands from the Wall PC

Usage:


Note:
tkinter library used for user interface is not thread safe
for a more elaborate application, use something better, perhaps mkTkinter
https://stackoverflow.com/questions/14694408/runtimeerror-main-thread-is-not-in-main-loop

GUI has problems (locks up OS) if chapter is entered/exited multiple
 times (~5 times) in rapid succession, presumably related to tkinter library
 and the multi-threaded usage here
Ability to restart the chapter (gui.chapter.is_done=False)
 has been removed - need to restart main program
 in order to clean this Chapter

"""

from util.Chapter import Chapter
import time
import numpy as np
import math
import time
import threading
import tkinter as tk


class Console(Chapter):
	
	def __init__(self,this_book):
		super().__init__(this_book)
		
		self.gui=GUI(self)
		self.gui.start()
		
		print("Proctor."+self.getTitle()+".init: is_debug: "+str(self.is_debug))
		
	def clean(self):
		super().clean()
		
	def dispose(self,is_final_call):
		super().dispose(is_final_call) 
		
	def enterChapter(self,unix_time_seconds):
		super().enterChapter(unix_time_seconds)
		print("debug a")
		self.gui.setVisible(True)
		if(self.is_debug):
			print("proctor."+self.getTitle()+": enterChapter()")
			
	def exitChapter(self):
		super().exitChapter()
		print("proctor."+self.getTitle()+".exitChapter()...")
		self.gui.setVisible(False)
		print("proctor."+self.getTitle()+".exitChapter(): done")
		
	def update(self,this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds,packets):#perhaps include total time elapsed in chapter... and playthrough number...
		super().update(this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds,packets)
		
		self.seconds_since_last_frame=this_frame_elapsed_seconds-previous_frame_elapsed_seconds
		self.this_frame_number=this_frame_number
		
		self.setDebugStringList([],this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds)
		
		#self.gui.update(self._osd_debug_strings,
		
	def draw(self):
		super().draw()
		
	def dispose(self):
		self.gui.dipose() #ensure GUI is dead if not termianted directly by user
		self.gui.join()

#helper class since tkinter has a blocking method mainloop(), it needs to
# be run in a seaprate thread to prevent blocking book
#opens a hidden window in a separate thread, then external Chapter calls
# isVisible(bool) when entering/exiting chapter
#need to load window once in __init__ rather than every chapter enter
# due to issue with tkinter (like pygame) where library cannot be cleanly
# diposed/reloaded correctly: https://stackoverflow.com/questions/27073762/tcl-asyncdelete-error-multithreading-python
# at least not without locking up the main root thread
class GUI(threading.Thread):
	BUTTON_HEIGHT_PX=27
	
	def __init__(self,chapter):
		threading.Thread.__init__(self)
		self._is_alive=True
		self.chapter=chapter
		print("proctor."+self.chapter.getTitle()+".GUI.__init_()")
		self.root=None
		
	def getWindow(self):
		print("Console.GUI.run(): start")
		root = tk.Tk()
		print("Console.GUI.run(): tk create done")
		#self.root.overrideredirect(1) #removes window header https://stackoverflow.com/questions/1406145/how-do-i-get-rid-of-python-tkinter-root-window
		root.withdraw()
		
		root.title("Proctor Console")
		root.protocol("WM_DELETE_WINDOW", self.dipose)
		
		nextChapterButton=tk.Button(root,text="Next Chapter",command=self.nextChapter)
		resetButton=tk.Button(root,text="Reset",command=self.resetRoom)
		status=tk.StringVar()
		
		nextChapterButton.pack()
		resetButton.pack()

		label = tk.Label(root, textvariable=status)
		label.pack()
		
		status.set("PLACEHOLDER")
		
		root.geometry("300x600+100+100")
		
		return root

	def nextChapter(self):
		print("Next Chapter")
		connection_manger=self.chapter.cm
		source_book_title=self.chapter.book.getTitle()
		source_chapter_title=self.chapter.getTitle()
		target_book_title="Wall"
		target_scope="Book"
		command="go_to_next_chapter"
		package=None
		packet_go_to_next_chapter=connection_manger.getPacketFor(source_book_title,source_chapter_title,target_book_title,target_scope,command,package)
		connection_manger.send(packet_go_to_next_chapter)
		
	def resetRoom(self):
		print("Reset")
		connection_manger=self.chapter.cm
		source_book_title=self.chapter.book.getTitle()
		source_chapter_title=self.chapter.getTitle()
		target_book_title="Wall"
		target_scope="Book"
		command="set_next_chapter"
		package={"by_index":0}
		packet_next_chapter_is_zero=connection_manger.getPacketFor(source_book_title,source_chapter_title,target_book_title,target_scope,command,package)
		
		command="go_to_next_chapter"
		package=None
		packet_go_to_next_chapter=connection_manger.getPacketFor(source_book_title,source_chapter_title,target_book_title,target_scope,command,package)
		
		connection_manger.send(packet_next_chapter_is_zero)
		connection_manger.send(packet_go_to_next_chapter)
		#self.chapter.is_done=True #testing, only resets chapter on curent book, not extenral PCs

	#if the user closes teh window, treat this as a "root thread program kill":
	# ie, close the book
	def dipose(self):
		if(self._is_alive): #only close once
			print("Closing...")
			self.root.destroy()
			print("PECTOR.Console.GUI.closing(): Terminate program...")
			self.chapter.book.is_alive=False
			print("Closed")
			self._is_alive=False

	def setVisible(self,is_visible):
		while(self.root is None):
			print("Proctor.Console.setVisibile(): Loop until run() init has begun, creating self.root")
		if(is_visible):
			self.root.deiconify()
		else:
			self.root.withdraw()

	def run(self):
		self.root=self.getWindow()
		self.root.mainloop()
		#self.root.quit()
		print("console.gui.run(): DONE")
