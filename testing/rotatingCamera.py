from numpy import sin, cos, radians

class RotatingCamera:
	def __init__(self, CAMRAD, mouse):
		pi3d=self.getpi3d()
		self.CAMERA = pi3d.Camera()
		self.CAMRAD = CAMRAD
		self.mouserot=0.0
		self.tilt=15.0
		self.frame=0
		self.omx,self.omy=mouse.position()
		
	def update(self,mouse):
		self.mx,self.my= mouse.position()
		self.mouserot -= (self.mx - self.omx) * 0.2
		self.tilt -= (self.my - self.omy) * 0.1
		self.omx=self.mx
		self.omy=self.my
		self.CAMERA.reset()
		self.CAMERA.rotate(-self.tilt,self.mouserot,0)
		self.CAMERA.position((self.CAMRAD * sin(radians(self.mouserot)) * cos(radians(self.tilt)),
							  self.CAMRAD * sin(radians(self.tilt)),
							  -self.CAMRAD * cos(radians(self.mouserot)) * cos(radians(self.tilt))))

	@staticmethod
	def getpi3d():
		import sys
		sys.path.insert(1, '/home/pi/pi3d')
		import pi3d
		return pi3d
