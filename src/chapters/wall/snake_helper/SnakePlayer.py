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

import copy
from util.ResourceManager import DIRECTION,DEVICE

#note: to allow clean transitions over the edge of the map, snake elements
# can have locations beyond the edge of map and will be alised back into
# the playing field when considering directions, interactions, etc

class SnakePlayer:
	SECONDS_PER_CELL=0.2 #rate of travel of a snake, higher is slower movement
	
	def __init__(self,snake_game,player_index):
		self.player_index=player_index #defines color of the given snake
		self.snake_game=snake_game #pointer back to parent game
		self.partial_step=0
		self.tail_list=[]
		self.last_valid_command=[] #last command received from player
		self.is_exiting=False #is the player exiting the playing field?
		if(player_index==0):
			self.tail_list.append([5,10,0])
			self.tail_list.append([5,9,0])
		elif(player_index==1):
			self.tail_list.append([10,19,0])
			self.tail_list.append([10,20,0])
		elif(player_index==2):
			self.tail_list.append([14,20,0])
			self.tail_list.append([15,20,0])
		else:
			raise ValueError("Player number "+str(player_index)+" not implemented in SnakePlayer")
		
	def update(self,this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds):
		next_direction,previous_direction=self.__getValidCommand()
		if(len(next_direction)>0): self.last_valid_command=next_direction
		self.partial_step=self.partial_step+(this_frame_elapsed_seconds-previous_frame_elapsed_seconds)/self.SECONDS_PER_CELL
		while(self.partial_step>=1):
			self.partial_step=self.partial_step-1
			self.__step()
		
	def draw(self):
		#draw partial image:
		# https://stackoverflow.com/questions/6239769/how-can-i-crop-an-image-with-pygame
		if(self.player_index==0):
			player_color=(255,0,0)
		elif(self.player_index==1):
			player_color=(0,255,0)
		elif(self.player_index==2):
			player_color=(0,0,255)
		for node_index in range(len(self.tail_list)-1):
			this_node=self.tail_list[node_index+1]
			next_node=self.tail_list[node_index]
			partial_node=[this_node[0]*(1-self.partial_step)+next_node[0]*self.partial_step,
						  this_node[1]*(1-self.partial_step)+next_node[1]*self.partial_step]
			node_loc_full=self.snake_game.RC2XY(partial_node[0],partial_node[1])
			node_loc_aliases=node_loc_full["alias"]
			for node_loc in node_loc_aliases:
			#this_node_loc=self.snake_game.RC2XY(this_node[0],this_node[1])
			#next_node_loc=self.snake_game.RC2XY(next_node[0],next_node[1])
			#node_loc=[next_node_loc[0]*self.partial_step+this_node_loc[0]*(1-self.partial_step),
			#		  next_node_loc[1]*self.partial_step+this_node_loc[1]*(1-self.partial_step)]
				this_rect=(node_loc[0],node_loc[1],self.snake_game.GRID_CELL_PX,self.snake_game.GRID_CELL_PX)#x,y,width,height
				self.snake_game.rm.pygame.draw.rect(self.snake_game.rm.screen_2d,player_color,this_rect,0)
		
	#return the current direction the snake head is headed
	#also return the direction the tail is from the head (opposite of heading direction)
	def getHeadDirection(self):
		#determine current path direction
		previous_direction=[]
		if(self.tail_list[0][1]<self.tail_list[1][1]): #head.col < tail.col
			previous_direction=DIRECTION.WEST
			previous_direction_opposite=DIRECTION.EAST
		elif(self.tail_list[0][1]>self.tail_list[1][1]): #head.col > tail.col
			previous_direction=DIRECTION.EAST
			previous_direction_opposite=DIRECTION.WEST
		elif(self.tail_list[0][0]<self.tail_list[1][0]): #head.row < tail.row
			previous_direction=DIRECTION.NORTH
			previous_direction_opposite=DIRECTION.SOUTH
		else:
			previous_direction=DIRECTION.SOUTH
			previous_direction_opposite=DIRECTION.NORTH
		return previous_direction,previous_direction_opposite
		
	#if a valid direction command is received, return it
	#super method will store this command until the next juncture point
	#has been reached and the command can be processed
	#will be a list between 0 and 2 DIRECTION elements
	def __getValidCommand(self):
		#determine current path direction
		previous_direction,previous_direction_opposite=self.getHeadDirection()
		
		#get commanded direction
		if(self.player_index==0): joystick_id=DEVICE.LASER
		elif(self.player_index==1): joystick_id=DEVICE.CAMERA
		elif(self.player_index==2): joystick_id=DEVICE.DIRECTION
		next_direction=self.snake_game.rm.getJoystickDirection(joystick_id)
		
		#remove ability to go backwards (ignore command to do so)
		if(previous_direction_opposite in next_direction):
			next_direction.remove(previous_direction_opposite)
			
		return next_direction,previous_direction
		
	#move the snake forward one cell
	#eat pellet if present
	def __step(self):
		#determine commanded direction (may be many)
		next_direction,previous_direction=self.__getValidCommand()
		next_direction=self.last_valid_command
		
		#prevent players from selecting multiple directions to move
		if(len(next_direction)==0):
			next_direction=[previous_direction]
		next_direction=next_direction[0] 
		
		next_cell=copy.deepcopy(self.tail_list[0])
		next_cell[2]=0 #new snake cell type is empty
		if(next_direction==DIRECTION.WEST):
			next_cell[1]=next_cell[1]-1 #col--
		elif(next_direction==DIRECTION.EAST):
			next_cell[1]=next_cell[1]+1 #col++
		elif(next_direction==DIRECTION.NORTH):
			next_cell[0]=next_cell[0]-1 #row--
		else:
			next_cell[0]=next_cell[0]+1 #row++
		
		self.tail_list.insert(0,next_cell)
		
		#move snake forward by moving all types one cell forward
		for tail_index in range(len(self.tail_list)-1):
			self.tail_list[tail_index][2]=self.tail_list[tail_index+1][2]
		
		#if pellet in head, then update last tail node with pellet type
		#else, delete last node
		# -- TO DO --
		if(False):
			pass
		else:
			self.tail_list=self.tail_list[:-1] #delete last node
		
		self.last_valid_command=[]
