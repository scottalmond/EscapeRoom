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
Chapter waits for a command from the proctor
Routinely checks on the status of the Helm PC, commands it to Standby
if the detected chapter is incorrect (ie, if Helm got out of sync with Master)

Usage:


"""

from util.Chapter import Chapter
from chapters.wall.hyperspace_helper import Maze

class Map(Chapter):
	def __init__(self,this_book):
		super().__init__(this_book)
		self.state=HyperspaceState()
		
	def clean(self):
		super().clean(self)
		self.dispose(False)
		
	def dipose(self,is_final_call):
		super().dipose(self,is_final_call)
		
	def enterChapter(self,unix_time_seconds):
		super().enterChapter(unix_time_seconds)
		
	def exitChapter(self):
		super().exitChapter()
	
	def update(self,this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds,packets):
		super().update(this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds,packets)
		
	def draw(self):
		super().draw()
