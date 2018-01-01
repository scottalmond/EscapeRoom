"""
Author: Scott Almond
Date: December 31, 2017

Purpose:
Chapter waits for a command from the proctor
Routinely checks on the status of the Helm PC, commands it to Standby
if the detected chapter is incorrect (ie, if Helm got out of sync with Master)

Usage:


"""

import util.Chapter

class Standby(util.Chapter.Chapter):
	def __init__(self,this_book):
		super.__init__(this_book)
		print("Standby: Hello World")
