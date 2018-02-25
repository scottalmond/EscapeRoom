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


"""

from util.Chapter import Chapter
import time
import numpy as np
import math

class Console(Chapter):
	
	def __init__(self,this_book):
		super().__init__(this_book)
		
		print("Proctor."+self.getTitle()+".init: is_debug: "+str(self.is_debug))
		
	def clean(self):
		super().clean()
		
	def dispose(self,is_final_call):
		super().dispose(is_final_call) 
		
	def enterChapter(self,unix_time_seconds):
		super().enterChapter(unix_time_seconds)
		
		if(self.is_debug):
			print("proctor."+self.getTitle()+": enterChapter()")
			
	def exitChapter(self):
		super().exitChapter()
		
	def update(self,this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds):#perhaps include total time elapsed in chapter... and playthrough number...
		super().update(this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds)
		
		self.seconds_since_last_frame=this_frame_elapsed_seconds-previous_frame_elapsed_seconds
		self.this_frame_number=this_frame_number
		
		self.setDebugStringList([],this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds)
		
	def draw(self):
		super().draw()
		
