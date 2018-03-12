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

#either opponent (is_player=False) or player pod (is_player=True)

class Pod:
	def __init__(self,is_player=True):
		pass
		
	def update(self,maze):
		pass
		#if right/left/up/down pressed, incremetn position of pod (based on GUI state)
		#update lazer state
		#enable render of gas effects
		
	def draw(self):
		pass
		#draw pod
		#draw gas effects
		#draw lazer (based on GUI state)
		#draw lazer effects
