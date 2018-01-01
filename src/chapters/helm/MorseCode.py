"""
Author: 
Date: 

Purpose:
Chapter displays a prompt to the player for a code
When Morse code buttons are pressed, the password field is filled with the pressed characters
If the sequence of characters matches the password defined elsewhere in the room, the screen unlocks
When the screen is unlocked, a hint for another puzzle is displayed

Usage:


"""

import util.Chapter

class Standby(util.Chapter.Chapter):
	def __init__(self,this_book):
		super.__init__(this_book)
		
