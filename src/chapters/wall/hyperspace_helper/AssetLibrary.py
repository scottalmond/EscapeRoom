import sys
#sys.path.insert(1,'/home/pi/pi3d') # to use local 'develop' branch version
#import pi3d
import numpy as np
import math
import random
import time

#quick accessors for all 3d models
# allows for cloning to minimize GPU usage

class AssetLibrary:
	MODEL_PATH = 'chapters/wall/assets/hyperspace/'
	
	def __init__(self,pi3d):
		#init
		self.pi3d=pi3d
		MODEL_PATH=AssetLibrary.MODEL_PATH
		shader = self.pi3d.Shader('uv_light')
		self.invisible = self.pi3d.Triangle(corners=((0,0),(.001,.001),(-.001,.001)))
		
		#pod
		self.pod_frame=self.invisible.shallow_clone()
		#the frame is the central location, but the pod may be rotated about the local axes for an animatic rotation effect during translation
		self.pod_frame.children=[]
		self.pod=self.pi3d.Model(file_string=MODEL_PATH+'pod_2.obj', z=0.0)
		pod_scale=0.33
		self.pod.scale(pod_scale,pod_scale,pod_scale)
		self.laser_base = self.pi3d.Model(file_string=MODEL_PATH+'laser_base_2.obj', y=3.15)
		self.laser_gun = self.pi3d.Model(file_string=MODEL_PATH+'laser_gun_2.obj', y=0.4, z=-0.4)
		self.laser_base.add_child(self.laser_gun)
		self.pod.add_child(self.laser_base)
		self.pod_frame.add_child(self.pod)
		self.pod.set_shader(shader)
		self.laser_gun.set_shader(shader)
		self.laser_base.set_shader(shader)
		
		#asteroids
		asteroid_large_scale=0.55
		self.asteroid_large=self.pi3d.Model(file_string=MODEL_PATH+'asteroid_large_1.obj',sx=asteroid_large_scale,sy=asteroid_large_scale,sz=asteroid_large_scale)
		self.asteroid_large.set_shader(shader)
		self.__setFog(self.asteroid_large)
		
		self.asteroid_medium=None
		
		
		self.asteroid_small=None
		
		#rings
		self.rings=[]
		ring_filename=['branched_ring_1.obj','straight_ring_1.obj']
		for ring_id in range(2):
			ring = self.pi3d.Model(file_string=MODEL_PATH+ring_filename[ring_id])
			ring.set_shader(shader)
			self.__setFog(ring)
			self.rings.append(ring)

	def __setFog(self,model):
		model.set_fog((0.0, 0.0, 0.0, 0.0), 110.8)
