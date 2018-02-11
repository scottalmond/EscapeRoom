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
The wall monitor is filled with static noise.  The IO_Manager is polled
for the status of the light puzzle components which are relayed to the Proctor
when all four components have changed state, the chapter is considered done

Usage:


"""

from util.Chapter import Chapter

class Snake(Chapter):
	NUMBER_OF_PLAYERS=3
	WINNING_LEGNTH=8 #number of blocks behind snake, including head, needed to have a full-length snake
	GRID_ROWS=20
	GRID_COLS=30
	GRID_CELL_PX=40 #number of pixels on a side of a grid cell
	CELL_COLOR_1=(255,255,255)
	CELL_COLOR_2=(162,152,138)
	
	def __init__(self,this_book):
		super().__init__(this_book)
		
		if(self.is_debug):
			print("Wall."+self.getTitle()+": Create Chapter Object")
			
	def clean(self):
		super().clean()
		
	def dispose(self,is_final_call):
		super().dispose(is_final_call)
		
	def enterChapter(self,unix_time_seconds):
		super().enterChapter(unix_time_seconds)
		self.background_color=(0,93,170)
		if(self.is_debug):
			print("Wall."+self.getTitle()+": set debug background color")
			self.background_color=(0,0,255)
		
	def exitChapter(self):
		super().exitChapter()
		
	def update(self,this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds):
		super().update(this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds)
		if(this_frame_number==0 and self.is_debug):
			top_left=self.__RC2XY(0,0)
			bottom_right=self.__RC2XY(self.GRID_ROWS,self.GRID_COLS)
			print("top left: "+str(top_left[0])+","+str(top_left[1]))
			print("bottom right: "+str(bottom_right[0])+","+str(bottom_right[1]))
		
	def draw(self):
		super().draw()
		self.__drawBackground()
		self.__drawGrid()
		
		self.__drawGUI()
		
		self.rm.pygame.display.flip()
		
	def __drawBackground(self):
		self.rm.screen_2d.fill(self.background_color)
		
	#draw background grid in the center of the screen
	def __drawGrid(self):
		top_left=self.__RC2XY(0,0)
		#top-left corner of cell just outside playing area is bottom
		# right pixel of last cell within playing area
		bottom_right=self.__RC2XY(self.GRID_ROWS,self.GRID_COLS)
		#fill background of playing area
		self.rm.pygame.draw.rect(self.rm.screen_2d,self.CELL_COLOR_1,
			(top_left[0],top_left[1],bottom_right[0]-top_left[0],bottom_right[1]-top_left[1]),0)
		for row in range(self.GRID_ROWS):
			for col in range(self.GRID_COLS):
				if((row+col)%2==0): #if on even diagonal, color cell - produces every-other cell filled
					cell_top_left=self.__RC2XY(row,col)
					cell_bottom_right=self.__RC2XY(row+1,col+1)
					self.rm.pygame.draw.rect(self.rm.screen_2d,self.CELL_COLOR_2,
						(cell_top_left[0],cell_top_left[1],cell_bottom_right[0]-cell_top_left[0],cell_bottom_right[1]-cell_top_left[1]),0)
					
		
	def __drawGUI(self):
		pass
		
	#return the (x,y) touple of the top-left corner of the given cell (row,col)
	def __RC2XY(self,row,col):
		screen_dim=self.rm.getScreenDimensions()
		top_left=(screen_dim[0]/2-self.GRID_COLS*self.GRID_CELL_PX/2,
				  screen_dim[1]/2-self.GRID_ROWS*self.GRID_CELL_PX/2)
		return (int(top_left[0]+col*self.GRID_CELL_PX),
				int(top_left[1]+row*self.GRID_CELL_PX))
		
