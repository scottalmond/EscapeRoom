

#representation of segment between one node and another
#rings, asteroids
#contains method to check for intersection with player

class Segment:
	def __init__(self):
		self.start_time=0 #seconds elapsed since the start of the level when this Segment was activated
		self.ring_list=[] #list of branches, rings and asteroids
		
	
