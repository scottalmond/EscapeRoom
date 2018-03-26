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
Chapter waits for a command from the Proctor (through the Wall)
before proceeding to the next chapter

Usage:


"""

from util.Chapter import Chapter

class MorseCode(Chapter):
	def __init__(self,this_book):
		super().__init__(this_book)
		
		print("Helm."+self.getTitle()+".init: is_debug: "+str(self.is_debug))
		
		if(self.is_debug):
			print("Helm."+self.getTitle()+": Create Chapter Object")
		
	def clean(self):
		super().clean()
		
	def dispose(self,is_final_call):
		super().dispose(is_final_call) 
		
	def enterChapter(self,unix_time_seconds):
		super().enterChapter(unix_time_seconds)
		
		if(self.is_debug):
			print("Helm."+self.getTitle()+": enterChapter()")
			
		self.background_color=(0,0,0)
		if(self.is_debug):
			self.background_color=(0,0,255)
			
	def exitChapter(self):
		super().exitChapter()
		self.book.startCountdown() #once Proctor commands book out of Standby, begin timer
		
		if(self.is_debug):
			print("Helm."+self.getTitle()+": exitChapter()")
		
		
	def update(self,this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds,packets):
		super().update(this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds,packets)
		
		self.seconds_since_last_frame=this_frame_elapsed_seconds-previous_frame_elapsed_seconds
		self.this_frame_number=this_frame_number
		
		self.setDebugStringList([],this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds)
		
	def draw(self):
		super().draw()
		
		self.rm.screen_2d.fill(self.background_color)
		
		self.displayDebugStringList()
		
		self.rm.pygame.display.flip()
