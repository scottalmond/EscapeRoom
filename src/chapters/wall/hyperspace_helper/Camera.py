#retains the state of the camera in regards to the playing field

class Camera:
	def __init__(self):
		pass

	#accept user input and change the field of view
	def update(self):
		pass

	#unit vector in x dimension with origin at center of player pod play field (not pod itself)
	def getFieldXvector(self):
		return (1,0,0)
		
	def getFieldYvector(self):
		return (0,1,0)

	def getFieldZvector(self):
		return (0,0,1)
		
	#X,Y,Z rotation angles of play field with respect to the starting orientation
	def getFieldRotation(self):
		return (0,0,0)
		
	#take user inputs to control camera and update state
	def update(self,
			   rm):
		pass
