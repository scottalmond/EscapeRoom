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
The wall monitor is filled with static noise.  The IO_Manager is polled
for the status of the light puzzle components which are relayed to the Proctor
when all four components have changed state, the chapter is considered done

Usage:


"""

from util.Chapter import Chapter

class LightPuzzle(Chapter):
	def __init__(self,this_book,this_resource_manager,this_io_manager):
		super().__init__(this_book,this_resource_manager,this_io_manager)
		print("LightPuzzle: Hello World")
		
	def update(self,frame_number,seconds_since_last_frame):
		super().update(frame_number,seconds_since_last_frame)
		
	def draw(self,frame_number,seconds_since_last_frame):
		super().draw(frame_number,seconds_since_last_frame)
