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
from util.ResourceManager import DIRECTION,DEVICE
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
	MIN_VISIBLE_PELLETS_PER_PLAYER=2 #number of pellets that must be on screen for players to eat (unless they are already at max length)
	GOAL_WIDTH_CELLS=3
	
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
		self.__updateGoals(this_frame_elapsed_seconds)
		
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
				player_length=player.length()
				max_player_length=self.WINNING_PLAYER_LENGTH
				#if the payer is too long, don't give any more pellets
				if(player_pellet_count>=min(max_player_length-player_length,
											self.MIN_VISIBLE_PELLETS_PER_PLAYER)):
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
		#collide players, also check to see if all are dead, and if so, exit the game
		any_alive=False
		for player in self.players:
			for opponent in self.players:
				player.collide(opponent)
			if(player.isAlive()): any_alive=True
		if(not any_alive):
			self.is_done=True
		
	def __updateGoals(self,this_frame_elapsed_seconds):
		rate_hz=1
		self.is_goal_blink=this_frame_elapsed_seconds%rate_hz<(rate_hz/2)
		
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
		#goal_length_total=self.NUMBER_OF_PLAYERS*self.GOAL_WIDTH_CELLS
		#spacing_length_total=self.GRID_COLS-goal_length_total
		#spacing_between_goals=spacing_length_total/self.NUMBER_OF_PLAYERS #1x between players, 2x xhalf on edges
		for player_index in range(len(self.players)):
			player=self.players[player_index]
			if(not player.isAlive()): continue#don't draw goal for dead player
			#goal_start_col=self.GOAL_WIDTH_CELLS*player_index+(0.5+player_index)*spacing_between_goals
			#goal_start_col=int(goal_start_col)
			goal_start_col,goal_last_col=self.getGoalRangeCol(player_index)
			goal_start_xy=self.RC2XY(self.GRID_ROWS,goal_start_col)["absolute"]
			goal_end_xy=self.RC2XY(self.GRID_ROWS+1,goal_start_col+self.GOAL_WIDTH_CELLS)["absolute"]
			rect_background=(goal_start_xy[0],goal_start_xy[1],
							 goal_end_xy[0]-goal_start_xy[0],goal_end_xy[1]-goal_start_xy[1])#x,y,w,h
			player_color=(200,0,0)
			if(player_index==1): player_color=(0,200,0)
			if(player_index==2): player_color=(0,0,200)
			rect_background_color=(player_color[0]/2,player_color[1]/2,player_color[2]/2)
			self.rm.pygame.draw.rect(self.rm.screen_2d,rect_background_color,rect_background,0)
			#now render progress
			ratio=min(self.players[player_index].length(),self.WINNING_PLAYER_LENGTH)/self.WINNING_PLAYER_LENGTH
			rect_progress=(rect_background[0],
						   rect_background[1],
						   rect_background[2]*ratio,
						   rect_background[3])
			self.rm.pygame.draw.rect(self.rm.screen_2d,player_color,rect_progress,0)
			if(self.isGoalActive(self.players[player_index]) and self.is_goal_blink):
				for col in np.arange(goal_start_col,goal_last_col+1):
					triangle_color=(255,255,255)
					self.__drawTriangle(self.GRID_ROWS,col,triangle_color)
		
	#given a player index, return the corresponding DEVICE Enum the controls that Snake
	def deviceForPlayerIndex(self,player_index):
		if(player_index==0): return DEVICE.LASER
		elif(player_index==1): return DEVICE.CAMERA
		elif(player_index==2): return DEVICE.DIRECTION
		raise ValueError("Invalid player_index, controls not implemented: "+str(player_index))
		
	#draw the live states of the GUI controls
	def __drawGUI(self):
		screen_dim=(1920,1080) if self.rm is None else self.rm.getScreenDimensions()
		gui_cell_dim=(50,50)
		edge=(100,100) #x,y offset from edge of screen to draw controls
		for player_index in range(self.NUMBER_OF_PLAYERS):
			player_color=(255,0,0)
			control_center=(edge[0],edge[1]) #settings for player 0
			if(player_index==1):
				player_color=(0,255,0)
				control_center=(screen_dim[0]-edge[0],edge[1])
			elif(player_index==2):
				player_color=(0,0,255)
				control_center=(screen_dim[0]-edge[0],screen_dim[1]-edge[1])
			player_commands=self.rm.getJoystickDirection(self.deviceForPlayerIndex(player_index))	
			for direction in [DIRECTION.NORTH,DIRECTION.WEST,DIRECTION.SOUTH,DIRECTION.EAST]:
				direction_color=(player_color[0]/2,player_color[1]/2,player_color[2]/2) #if not active, dim the input color
				if(direction in player_commands):
					direction_color=player_color #when active, highlight
				if(direction==DIRECTION.NORTH): #switch statement for direction-based offset (top left corner of input cell)
					command_offset=(-gui_cell_dim[0]/2,-gui_cell_dim[1]*3/2)
				elif(direction==DIRECTION.EAST):
					command_offset=(gui_cell_dim[0]/2,-gui_cell_dim[1]/2)
				elif(direction==DIRECTION.SOUTH):
					command_offset=(-gui_cell_dim[0]/2,gui_cell_dim[1]/2)
				elif(direction==DIRECTION.WEST):
					command_offset=(-gui_cell_dim[0]*3/2,-gui_cell_dim[1]/2)
				rect_dims=(control_center[0]+command_offset[0],
						   control_center[1]+command_offset[1],
						   edge[0]/2,
						   edge[1]/2)#x,y,w,h
				self.rm.pygame.draw.rect(self.rm.screen_2d,direction_color,rect_dims,0)
		
			
		
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
	
	#used to determine whether Snake should start exiting the playing field	
	def isGoalActive(self,player):
		return player.length()>=self.WINNING_PLAYER_LENGTH and player.isAlive()

	#determine the extent of the goal, inclusive
	#returns: start_col,last_col
	def getGoalRangeCol(self,player_index):
		goal_length_total=self.NUMBER_OF_PLAYERS*self.GOAL_WIDTH_CELLS
		spacing_length_total=self.GRID_COLS-goal_length_total
		spacing_between_goals=spacing_length_total/self.NUMBER_OF_PLAYERS #1x between players, 2x xhalf on edges
		goal_start_col=self.GOAL_WIDTH_CELLS*player_index+(0.5+player_index)*spacing_between_goals
		goal_start_col=int(goal_start_col)
		return goal_start_col,(goal_start_col+self.GOAL_WIDTH_CELLS-1)

	#draw a downward pointing graphic
	# (directing players to exit the field when the snake is full length)
	def __drawTriangle(self,row,col,color):
		xy=self.RC2XY(row,col)["absolute"]
		triangle=[]
		pad=0.1
		triangle.append([xy[0]+pad*self.GRID_CELL_PX,xy[1]+pad*self.GRID_CELL_PX]) #top left
		triangle.append([xy[0]+(1-pad)*self.GRID_CELL_PX,xy[1]+pad*self.GRID_CELL_PX])
		triangle.append([xy[0]+0.5*self.GRID_CELL_PX,xy[1]+(1-pad)*self.GRID_CELL_PX])
		self.rm.pygame.draw.polygon(self.rm.screen_2d,color,triangle,0)
