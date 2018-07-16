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
Chapter waits for a command from the proctor
Routinely checks on the status of the Helm PC, commands it to Standby
if the detected chapter is incorrect (ie, if Helm got out of sync with Master)

Usage:


"""

from util.Chapter import Chapter
from chapters.wall.hyperspace_helper.Maze import Maze
from pygame import gfxdraw #antialias edges
import math

class Map(Chapter):
	
	def __init__(self,this_book):
		super().__init__(this_book)
		self.maze=Maze()
		
	def clean(self):
		super().clean()
		self.maze.clean()
		
	def dipose(self,is_final_call):
		super().dipose(self,is_final_call)
		
	def enterChapter(self,unix_time_seconds):
		super().enterChapter(unix_time_seconds)
		
	def exitChapter(self):
		super().exitChapter()
	
	def update(self,this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds,packets):
		super().update(this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds,packets)
		debug_strings=[]
		debug_strings.append("DEBUG.HEREXXXXXX")
		self.setDebugStringList(debug_strings,this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds)
		
	def draw(self):
		self.__drawBackground()
		self.__drawPaths()
		self.__drawNodes()
		self.__drawPod()
		self.displayDebugStringList()
		self.rm.pygame.display.flip()
		
	def __drawBackground(self):
		self.rm.screen_2d.fill((200,200,200))
		
	def __drawPaths(self):
		pass
		
	def __drawNodes(self):
		sprite_circle=self.__getSprite('circle',(255,255,255),(0,0,0),0.75,24)
		sprite_triangle=self.__getSprite('triangle',(255,255,255),(0,0,0),0.5,24)
		sprite_square=self.__getSprite('square',(255,255,255),(0,0,0),0.7,24)
		sprite_dead=self.__getSprite('dead',(255,255,255),(0,0,0),0.5,24)
		self.__drawSprite(300,300,sprite_circle)
		self.__drawSprite(400,400,sprite_triangle)
		self.__drawSprite(500,500,sprite_square)
		self.__drawSprite(600,600,sprite_dead)
		pass
		
	def __drawPod(self):
		pass
		
	def __getbackgroundImage(self):
		image_cropped=self.rm.pygame.Surface((self.GRID_CELL_PX,self.GRID_CELL_PX),self.rm.pygame.SRCALPHA,32)

	#given center of sprite location, draw the given shape
	#'circle', 'square', 'triangle'
	#triangle is pointing up 
	def __drawSprite(self,local_x,local_y,out_image):
		global_x,global_y,angle=self.__rotateCoordinates(local_x,local_y)
		x_tl=global_x-out_image.get_width() #top left handle of image
		y_tl=global_y-out_image.get_height()
		self.rm.screen_2d.blit(out_image,(x_tl,y_tl))

	#returns an image
	#shape is a string: circle, triangle, square, dead ('x' for dead end)
	#SPRITE_COLOR_FILL and SPRITE_COLOR_OUTLINE are tuples up to (255,255,255) RGB
	#INNER_FILL_RATIO is between 0.0 (ALL outline) to 1.0 (NO outline)
	def __getSprite(self,shape,
		SPRITE_COLOR_FILL,SPRITE_COLOR_OUTLINE,
		SPRITE_INNER_FILL_RATIO,SPRITE_DIAMETER_PIXELS):
		#add two pixels to edges to account for anti-aliasing
		IMG_WIDTH=SPRITE_DIAMETER_PIXELS+50
		IMG_HEIGHT=SPRITE_DIAMETER_PIXELS+50
		out_image=self.rm.pygame.Surface((IMG_WIDTH,IMG_HEIGHT),self.rm.pygame.SRCALPHA,32)
		out_image=out_image.convert_alpha()
		out_image.fill((255,0,0))
		#INNER_FILL_RATIO=0.5
		#SPRITE_COLOR_OUTLINE=(0,0,0)
		#SPRITE_COLOR_FILL=(255,255,255)
		temp1,temp2,rotation_angle_degrees=self.__rotateCoordinates(0,0)
		screen_x_c=int(IMG_WIDTH/2)
		screen_y_c=int(IMG_HEIGHT/2)
		if(shape=='circle'):
			rxo=int(SPRITE_DIAMETER_PIXELS/2) #outer radius
			rxi=int(SPRITE_INNER_FILL_RATIO*SPRITE_DIAMETER_PIXELS/2) #inner radius
			self.rm.pygame.gfxdraw.aacircle(out_image,screen_x_c,screen_y_c,rxo,SPRITE_COLOR_OUTLINE)
			self.rm.pygame.gfxdraw.filled_circle(out_image,screen_x_c,screen_y_c,rxo,SPRITE_COLOR_OUTLINE)
			#urg, drawing white aacircle on top of black outline causes white semi-transparent pixels
			#to occur around inner circle - hack-fix by spitting draw of inner
			#circle on a separate clear-background image and then blitting that onto output shape
			if(not SPRITE_COLOR_FILL is None):
				temp_image=self.rm.pygame.Surface((IMG_WIDTH,IMG_HEIGHT),self.rm.pygame.SRCALPHA,32)
				temp_image=temp_image.convert_alpha()
				self.rm.pygame.gfxdraw.aacircle(temp_image,screen_x_c,screen_y_c,rxi,SPRITE_COLOR_FILL)
				self.rm.pygame.gfxdraw.filled_circle(temp_image,screen_x_c,screen_y_c,rxi,SPRITE_COLOR_FILL)
				out_image.blit(temp_image,(0,0))
		elif(shape=='triangle'):
			#x1=int(SPRITE_DIAMETER_PIXELS*0.5)
			#y1=int(0)
			#x2=int(SPRITE_DIAMETER_PIXELS*(0.5-math.sqrt(3)/4))
			#y2=int(SPRITE_DIAMETER_PIXELS*0.75)
			#x3=int(SPRITE_DIAMETER_PIXELS*(0.5+math.sqrt(3)/4))
			#y3=y2
			#self.rm.pygame.gfxdraw.aatrigon(out_image,x1,y1,x2,y2,x3,y3,SPRITE_COLOR_OUTLINE)
			#self.rm.pygame.gfxdraw.filled_trigon(out_image,x1,y1,x2,y2,x3,y3,SPRITE_COLOR_OUTLINE)
			#x1i=x1
			#y1i=int(SPRITE_DIAMETER_PIXELS*(0.5-0.5*SPRITE_INNER_FILL_RATIO))
			#x2i=int(SPRITE_DIAMETER_PIXELS*(0.5-math.sqrt(3)*0.25*SPRITE_INNER_FILL_RATIO))
			#y2i=int(SPRITE_DIAMETER_PIXELS*(0.5+0.25*SPRITE_INNER_FILL_RATIO))
			#x3i=int(SPRITE_DIAMETER_PIXELS*(0.5+math.sqrt(3)*0.25*SPRITE_INNER_FILL_RATIO))
			#y3i=y2i
			#temp_image=self.rm.pygame.Surface((IMG_WIDTH,IMG_HEIGHT),self.rm.pygame.SRCALPHA,32)
			#temp_image=temp_image.convert_alpha()
			#self.rm.pygame.gfxdraw.aatrigon(temp_image,x1i,y1i,x2i,y2i,x3i,y3i,SPRITE_COLOR_FILL)
			#self.rm.pygame.gfxdraw.filled_trigon(temp_image,x1i,y1i,x2i,y2i,x3i,y3i,SPRITE_COLOR_FILL)
			#out_image.blit(temp_image,(0,0))
			x1o=int(0)+screen_x_c #outer
			y1o=int(-0.5*SPRITE_DIAMETER_PIXELS)+screen_y_c
			x2o=int(-math.sqrt(3)*SPRITE_DIAMETER_PIXELS/4)+screen_x_c
			y2o=int(0.25*SPRITE_DIAMETER_PIXELS)+screen_y_c
			x3o=int(math.sqrt(3)*SPRITE_DIAMETER_PIXELS/4)+screen_x_c
			y3o=y2o
			self.rm.pygame.gfxdraw.aatrigon(out_image,x1o,y1o,x2o,y2o,x3o,y3o,SPRITE_COLOR_OUTLINE)
			self.rm.pygame.gfxdraw.filled_trigon(out_image,x1o,y1o,x2o,y2o,x3o,y3o,SPRITE_COLOR_OUTLINE)
			if(not SPRITE_COLOR_FILL is None):
				x1i=int(0)+screen_x_c #inner
				y1i=int(-0.5*SPRITE_DIAMETER_PIXELS*SPRITE_INNER_FILL_RATIO)+screen_y_c
				x2i=int(-math.sqrt(3)*SPRITE_DIAMETER_PIXELS*SPRITE_INNER_FILL_RATIO/4)+screen_x_c
				y2i=int(0.25*SPRITE_DIAMETER_PIXELS*SPRITE_INNER_FILL_RATIO)+screen_y_c
				x3i=int(math.sqrt(3)*SPRITE_DIAMETER_PIXELS*SPRITE_INNER_FILL_RATIO/4)+screen_x_c
				y3i=y2i
				temp_image=self.rm.pygame.Surface((IMG_WIDTH,IMG_HEIGHT),self.rm.pygame.SRCALPHA,32)
				temp_image=temp_image.convert_alpha()
				self.rm.pygame.gfxdraw.aatrigon(temp_image,x1i,y1i,x2i,y2i,x3i,y3i,SPRITE_COLOR_FILL)
				self.rm.pygame.gfxdraw.filled_trigon(temp_image,x1i,y1i,x2i,y2i,x3i,y3i,SPRITE_COLOR_FILL)
				out_image.blit(temp_image,(0,0))
		elif(shape=='square'):
			x1o=int(-SPRITE_DIAMETER_PIXELS/2)+screen_x_c
			y1o=int(-SPRITE_DIAMETER_PIXELS/2)+screen_y_c
			out_image.fill(SPRITE_COLOR_OUTLINE,(x1o,y1o,SPRITE_DIAMETER_PIXELS,SPRITE_DIAMETER_PIXELS))
			if(not SPRITE_COLOR_FILL is None):
				x1i=int(-SPRITE_DIAMETER_PIXELS*SPRITE_INNER_FILL_RATIO/2)+screen_x_c
				y1i=int(-SPRITE_DIAMETER_PIXELS*SPRITE_INNER_FILL_RATIO/2)+screen_y_c
				wi=int(SPRITE_INNER_FILL_RATIO*SPRITE_DIAMETER_PIXELS)
				hi=wi
				out_image.fill(SPRITE_COLOR_FILL,(x1i,y1i,wi,hi))
		elif(shape=='dead'): #dead end
			pass
		else:
			raise NotImplementedError("Map.__getSprite: shape type not defined: ",shape)
		out_image=self.rm.pygame.transform.rotate(out_image,rotation_angle_degrees) #rotate sprites to account for screen installation direction
		return out_image
	
	#returns the coordinates rotated to accomodate the installation direction of the screen
	def __rotateCoordinates(self,x,y):
		ANGLE_DEGREES=0 #rotation of sprites in degrees due to screen installation direction
		return x,y,ANGLE_DEGREES
