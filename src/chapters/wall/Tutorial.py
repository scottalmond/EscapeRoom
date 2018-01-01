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
This tutorial presents the players with an iconic representation of
all player controls, whith al marked as inactive.  When players actuate the
corresponding controls, that sub-component is marked as active.  Once
players have activated all controls (and presumably sat in the chairs next to
the controls) then the chapter is considered done

Usage:


"""

from util.Chapter import Chapter

class Tutorial(Chapter):
	def __init__(self,this_book):
		super().__init__(this_book)
		print("Tutorial: Hello World")
		
	def update(self):
		pass
		
	def draw(self):
		pass
