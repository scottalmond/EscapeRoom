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
The game displays three Snake characters on screen.  Between one and two
players control each Snake.  Snakes are displayed on a grid and can move
in one of four cardinal directions.  Pellets appear randomly on the playing
field;  running over the correctly-colored pellet with a Snake lengthens
the Snake.  When a Snake is long enough, goal posts will appear at the
bottom of the playing field, allowing the Snake to exit.  Running two
Snake into one another removes the tail collected so far.

Usage:


"""

from util.Chapter import Chapter
from chapters.wall.snake_helper.SnakePlayer import SnakePlayer
import numpy as np
import math
from random import randint

class Snake(Chapter):
	NUMBER_OF_PLAYERS=3
	WINNING_PLAYER_LENGTH=8 #number of blocks behind snake, including head, needed to have a full-length snake
	GRID_ROWS=10
	GRID_COLS=21
	GRID_CELL_PX=80 #number of pixels on a side of a grid cell
	CELL_COLOR_1=(255,255,255) #white
	CELL_COLOR_2=(162,152,138) #brown
	MIN_VISIBLE_PELLETS_PER_PLAYER=2 #number of pellets that must be on screen for players to eat
	
	def __init__(self,this_book):
		super().__init__(this_book)
		
		if(self.is_debug):
			print("Wall."+self.getTitle()+": Create Chapter Object")
		self.players=[]
		for player_index in range(self.NUMBER_OF_PLAYERS):
			self.players.append(SnakePlayer(self,player_index))
			
	def clean(self):
		super().clean()
		self.pellets=[] #pellets (row,col,graphic_id,player_index)
		for player_index in range(len(self.players)):
			self.players[player_index]=SnakePlayer(self,player_index)
		self.__updatePellets() #populate playing field with pellets to eat
		
	def dispose(self,is_final_call):
		super().dispose(is_final_call)
		
	def enterChapter(self,unix_time_seconds):
		super().enterChapter(unix_time_seconds)
		self.background_color=(0,0,0)
		if(self.is_debug):
			print("Wall."+self.getTitle()+": set debug background color")
			self.background_color=(0,93,170)
			
		self.font=self.rm.pygame.font.SysFont('Comic Sans MS',100)
		self.font_color=(0,255,0)
		self.font_line_height_px=self.font.get_height()
		
	def exitChapter(self):
		super().exitChapter()
		
	def update(self,this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds):
		super().update(this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds)
		
		self.__updatePlayers(this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds)
		self.__updatePellets() #if pellet eaten, add another
		
		if(this_frame_number==0 and self.is_debug):
			top_left=self.RC2XY(0,0)["absolute"]
			bottom_right=self.RC2XY(self.GRID_ROWS,self.GRID_COLS)["absolute"]
			#print("top left: "+str(top_left[0])+","+str(top_left[1]))
			#print("bottom right: "+str(bottom_right[0])+","+str(bottom_right[1]))
			
		#debug info
		self.seconds_since_last_frame=this_frame_elapsed_seconds-previous_frame_elapsed_seconds
		self.this_frame_number=this_frame_number
		self.debug_strings=[self._book.getTitle()+"."+self.getTitle(),
							'FPS: '+str(math.floor(1/np.max((0.00001,self.seconds_since_last_frame)))),
							'Frame: '+str(self.this_frame_number)]
		
	def draw(self):
		super().draw()
		self.__drawBackground()
		self.__drawGrid()
		self.__drawPellets()
		self.__drawPlayers()
		self.__drawGoals()
		self.__drawGUI()
		self.__drawDebug()
		
		self.rm.pygame.display.flip()
		
	#initalize new pellets as needed
	def __updatePellets(self):
		#for each player type, ensure there are two pellets on screen
		for player_index in range(len(self.players)):
			player=self.players[player_index]
			player_pellet_count=0
			while(True): #no do-while in Python... so use infinite while and break
				for pellet in self.pellets:
					if(pellet[3]==player_index):
						player_pellet_count=player_pellet_count+1
				if(player_pellet_count>=self.MIN_VISIBLE_PELLETS_PER_PLAYER):
					break
				#insufficient visible pellets, so attempt to add one
				min_graphic_ID=player.graphicID("pellet")[0]
				max_graphic_ID=player.graphicID("pellet")[1]
				candidate_pellet=[randint(0,self.GRID_ROWS-1),
								  randint(0,self.GRID_COLS-1),
								  randint(min_graphic_ID,max_graphic_ID-1),
								  player_index]
				viable_pellet=True
				for blocking_player in self.players:
					if(blocking_player.intersects(candidate_pellet[0],
												  candidate_pellet[1])):
						viable_pellet=False #cannot place pellet on top of players
						break
				for existing_pellet in self.pellets:
					if(existing_pellet[0]==candidate_pellet[0] and
					   existing_pellet[1]==candidate_pellet[1]):
						viable_pellet=False #cannot place pellet on top of other pellet
						break
				if(viable_pellet):
					self.pellets.append(candidate_pellet)
					
	#destroy pellets when collect
	#destroy player tail when collided
	#use player input to select new direction of head
	def __updatePlayers(self,this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds):
		for player in self.players:
			player.update(this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds)
		for player in self.players:
			for opponent in self.players:
				player.collide(opponent)
		
	def __drawBackground(self):
		self.rm.screen_2d.fill(self.background_color)
		
	#draw background grid in the center of the screen
	#note: draw several rectangles appears to use a significnat amount of
	# pygame resources (20 FPS rather than 40 FPS when no grid is drawn)
	def __drawGrid(self):
		top_left=self.RC2XY(0,0)["absolute"]
		#top-left corner of cell just outside playing area is bottom
		# right pixel of last cell within playing area
		bottom_right=self.RC2XY(self.GRID_ROWS,self.GRID_COLS)["absolute"]
		#fill background of playing area
		self.rm.pygame.draw.rect(self.rm.screen_2d,self.CELL_COLOR_1,
			(top_left[0],top_left[1],bottom_right[0]-top_left[0],bottom_right[1]-top_left[1]),0)
		for row in range(self.GRID_ROWS):
			for col in range(self.GRID_COLS):
				if((row+col)%2==0): #if on even diagonal, color cell - produces every-other cell filled
					cell_top_left=self.RC2XY(row,col)["absolute"]
					cell_bottom_right=self.RC2XY(row+1,col+1)["absolute"]
					self.rm.pygame.draw.rect(self.rm.screen_2d,self.CELL_COLOR_2,
						(cell_top_left[0],cell_top_left[1],cell_bottom_right[0]-cell_top_left[0],cell_bottom_right[1]-cell_top_left[1]),0)
		
	def __drawPellets(self):
		for pellet in self.pellets:
			player_color=(255,0,0)
			player_index=pellet[3]
			if(player_index==1): player_color=(0,255,0)
			if(player_index==2): player_color=(0,0,255)
			pellet_xy=self.RC2XY(pellet[0],pellet[1])["absolute"]
			self.rm.pygame.draw.ellipse(self.rm.screen_2d,player_color,
				(pellet_xy[0],pellet_xy[1],self.GRID_CELL_PX,self.GRID_CELL_PX),0)
		
	def __drawPlayers(self):
		for player in self.players:
			player.draw()
		
	def __drawGoals(self):
		pass
		
	def __drawGUI(self):
		pass
		
	def __drawDebug(self):
		if(self.is_debug): #display debug text
			for this_string_index in range(len(self.debug_strings)):
				this_string=self.debug_strings[this_string_index]
				this_y_px=this_string_index*self.font_line_height_px #vertically offset each line of text
				rendered_string=self.font.render(this_string,False,self.font_color)
				self.rm.screen_2d.blit(rendered_string,(0,this_y_px))
		
		
	#if there is a pellet at the specified (row,col)
	# and it matches the current player color
	# then remove it from the pellet fabric and return it
	def eatPellet(self,row,col,player_index):
		for pellet in self.pellets:
			#print("Snake.eatPellet(): IN: "+str([row,col,player_index]))
			#print("Snake.eatPellet(): HIT: "+str(pellet))
			if(pellet[0]==row and pellet[1]==col and pellet[3]==player_index):
				self.pellets.remove(pellet)
				return pellet
		return None
		
	#return the absolute (x,y) touple of the top-left corner of the given cell (row,col)
	# in a dictionary under key "absolute"
	#also return alises of the current location explictly limited within
	# the current play field as touple list under the key "alias"
	#accepts fractional row,col inputs
	def RC2XY(self,row,col):
		troubleshoot=False#self.is_debug
		screen_dim=(1920,1080) if self.rm is None else self.rm.getScreenDimensions()
		play_field_x_px=self.GRID_CELL_PX*self.GRID_COLS
		play_field_y_px=self.GRID_CELL_PX*self.GRID_ROWS
		if(troubleshoot):
			print("play_field_x_px: "+str(play_field_x_px))
			print("play_field_y_px: "+str(play_field_y_px))
		unaliased_rc=[row%self.GRID_ROWS,col%self.GRID_COLS]
		if(unaliased_rc[0]<0): unaliased_rc[0]+self.GRID_COLS
		if(unaliased_rc[1]<0): unaliased_rc[1]+self.GRID_ROWS
		if(troubleshoot):
			print("unaliased_rc[0]: "+str(unaliased_rc[0]))
			print("unaliased_rc[1]: "+str(unaliased_rc[1]))
		top_left=(screen_dim[0]/2.0-play_field_x_px/2.0,
				  screen_dim[1]/2.0-play_field_y_px/2.0)
		if(troubleshoot):
			print("top_left[0]: "+str(top_left[0]))
			print("top_left[1]: "+str(top_left[1]))
		absolute=(top_left[0]+col*self.GRID_CELL_PX,
				  top_left[1]+row*self.GRID_CELL_PX)
		if(troubleshoot):
			print("debug_1: "+str(top_left[1]))
			print("debug_2: "+str(row))
			print("debug_3: "+str(self.GRID_CELL_PX))
			print("debug_4: "+str(row*self.GRID_CELL_PX))
			print("debug_5: "+str(top_left[1]+row*self.GRID_CELL_PX))
			print("absolute[0]: "+str(absolute[0]))
			print("absolute[1]: "+str(absolute[1]))
		playable=(((absolute[0]-top_left[0])%play_field_x_px)+top_left[0],
				  ((absolute[1]-top_left[1])%play_field_y_px)+top_left[1])
		if(troubleshoot):
			print("playable[0]: "+str(playable[0]))
			print("playable[1]: "+str(playable[1]))
		alias=[]
		alias.append(playable)
		if(troubleshoot):
			print(str(self.GRID_ROWS-1)+" < "+str(unaliased_rc[0])+" < "+str(self.GRID_ROWS))
			print(str(self.GRID_COLS-1)+" < "+str(unaliased_rc[1])+" < "+str(self.GRID_COLS))
		if((self.GRID_ROWS-1) < unaliased_rc[0] < self.GRID_ROWS): #if heading off the bottom screen edge
			alias.append((playable[0],playable[1]-play_field_y_px))
		if((self.GRID_COLS-1) < unaliased_rc[1] < self.GRID_COLS): #if heading off the right screen edge
			alias.append((playable[0]-play_field_x_px,playable[1]))
		return {"absolute":absolute,
				"alias":alias,
				"unaliased_row_col":unaliased_rc}
		
