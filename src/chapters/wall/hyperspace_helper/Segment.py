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


Usage:


"""

#representation of segment between one node and another
#rings, asteroids
#contains method to check for intersection with player

class Segment:
	def __init__(self):
		self.start_time=0 #seconds elapsed since the start of the level when this Segment was activated
		self.ring_list=[] #list of branches, rings and asteroids
		
	def update(self):
		pass
		
	def draw(self):
		pass
		
	def reset(self):
		pass
