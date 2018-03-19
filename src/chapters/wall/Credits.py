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
This credits sequence lists the contributions from each person that
supported the escape room.  If the room is completed successfully, 
artwork of the cargo pod entering an alien plant and being opened are
shown next to peoples' names.  If the game is not completed within the 
time limit, the artwork is replaced with pictures of the escape room
components during assembly and integration. At the end of the
credits sequence, a brief cutscene of the corporate logo is played.

Usage: XX TODO: revise to match code operation
XX expects images in sub folder /images/
This chapter will first look in the PRIMARY_DIRECTORY for:
- a series of images prepended with "WXX_" where "XX" is a numeric from 00 to 99 (00 displays first)
	"W" refers to a win condition, "L" refers to the image displayed when the game room
	is lost (not completed in 60 minutes)
- a coporate_logo.mp4 video file
- a "config.csv" file containing the following columns:
Type, Value.  Type is a tag like HEADER or NAME.  Value is a string.
ex: "HEADER_1, Hyperspace", "HEADER_2, Design & Programming", "NAME, Scott Almond",
"HEADER_2","2D Art", "FINAL, Special Thanks"
HEADER_1, HEADER_2 are similar to work procesor headers that decrease in size
for higher values
NAME is a plain text name
FINAL is text that will appear statically at the end of the scrolling logos
such as special thanks
"""

#if debugging...
#import os
#import sys
#sys.path.insert(0,"/home/pi/Documents/EscapeRoom/src/")
#from util.ResourceManager import ResourceManager

from util.Chapter import Chapter

import os

class Credits(Chapter):
	PRIMARY_DIRECTORY='/home/pi/Documents/corporate_credits/'
	BACKUP_DIRECTORY='/home/pi/Documents/EscapeRoom/src/chapters/wall/assets/credits/'
	MUSIC_PATH='./chapters/wall/assets/credits/escaperoom03_pre02_0.mp3'
	MUSIC_ENABLED=True
	
	def __init__(self,this_book):
		super().__init__(this_book)
	
	def clean(self):
		super().clean()
		
		#locate asset folder
		is_primary_exists=os.path.isdir(self.PRIMARY_DIRECTORY)
		is_backup_exists=os.path.isdir(self.BACKUP_DIRECTORY)
		if(not is_primary_exists and not is_backup_exists):
			raise ValueError("Wall.Credits: Unable to locate credits asset folder: "+str(self.PRIMARY_DIRECTORY))
		self.asset_folder=self.PRIMARY_DIRECTORY if is_primary_exists else self.BACKUP_DIRECTORY
		
		#load/parse config file
		config_path=self.asset_folder+"config.txt"
		config_exists=os.path.exists(config_path)
		if(not config_exists): raise ValueError("Wall.Credits: Unable to locate credits configuration file: "+str(config_path))
		self.slides=self.parseConfig(config_path)
		
		#load images referenced in config file
		for slide_package in self.slides:
			for element in slide_package:
				is_image=element["format"]=="Image"
				if(is_image):
					image_filename=element["package"]
					image_path=self.asset_folder+"images/"+image_filename
					try:
						if(".png" in image_filename):
							element["image"]=self.rm.pygame.image.load(image_path).convert_alpha()
						else:
							element["image"]=self.rm.pygame.image.load(image_path).convert()
					except:
						raise ValueError("Wall.Credits: Unable to load image: "+str(image_path))
		
	def dispose(self,is_final_call):
		super().dispose(is_final_call) 
		
	def enterChapter(self,unix_time_seconds):
		super().enterChapter(unix_time_seconds)
		self.book.endCountdown() #end timer if not already done
		if(self.MUSIC_ENABLED):
			self.rm.pygame.mixer.music.load(self.MUSIC_PATH)
			self.rm.pygame.mixer.music.play()
		self.background_color=(0,0,255)

	def exitChapter(self):
		super().exitChapter()
		if(self.MUSIC_ENABLED):
			self.rm.pygame.mixer.music.stop()

	def update(self,this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds):
		super().update(this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds)
		elapsed_time_seconds=self.book.getCountdownElapsed()
		self.image_list_draw=[] #list of images and locations to be rendered
		self.text_list_draw=[] #list of text strings, fonts, and locations to be rendered
		this_slide_index_ratio=this_frame_elapsed_seconds*len(self.slides)/self.getDurationSeconds()
		this_slide_index=int(this_slide_index_ratio)
		if(this_slide_index>=len(self.slides)):
			self.is_done=True #may want to redefine as after the cororate credits video has played
			return
		else:
			slide_duration_seconds=self.getDurationSeconds()/len(self.slides)
			for slide_index in range(this_slide_index+1):
				slide=self.slides[slide_index]
				for element in slide:
					is_image_element=element["format"]=="Image"
					if(is_image_element):
						element_scope=element["slides"] #number of slides this image is to appear during, ie "2" appears for 2 full slides
						is_in_scope=element_scope<0 or (this_slide_index-slide_index)<element_scope #if current update() is during those 2 slides
						is_visible=element["is_win"] is None or element["is_win"]==self.isWin() #if image is only to appear during a win condition, check that here
						ratio_trajectory=(this_slide_index_ratio-slide_index)/element_scope
						#percent completion of the motion from start to end, [0,1)
						# ie, if image is to appear on slides 3 and 4, and the current slide is 4.7, then ratio is = [4.7-3]/2
						if(is_in_scope and is_visible):
							xy_start=(element["trajectory"][0],element["trajectory"][1])
							if(len(element["trajectory"])==2):
								xy_image=xy_start
							else:
								xy_end=(element["trajectory"][2],element["trajectory"][3])
								xy_image=(xy_start[0]*(1-ratio_trajectory)+xy_end[0]*ratio_trajectory,
										  xy_start[1]*(1-ratio_trajectory)+xy_end[1]*ratio_trajectory)
							self.image_list_draw.append({
								"image":element["image"],
								"xy":xy_image
								})
			
		elapsed_minutes=int(elapsed_time_seconds/60)
		elapsed_seconds=int(elapsed_time_seconds%60)
		debug_strings=["Successful: "+str(self.isWin()),
					   "Elapsed: "+str(elapsed_minutes)+" m "+str(elapsed_seconds)+" s",
					   "Slide: "+str(this_slide_index)+"/"+str(len(self.slides)),
					   "Image count: "+str(len(self.image_list_draw)),
					   "String count: "+str(len(self.text_list_draw))]
		self.setDebugStringList(debug_strings,this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds)

	def draw(self):
		super().draw()
		self.rm.screen_2d.fill(self.background_color)
		for image_definition in self.image_list_draw:
			image_handle=image_definition["image"]
			image_location=image_definition["xy"] #touple
			self.rm.screen_2d.blit(image_handle,image_location)
		for text_definition in self.text_list_draw:
			text_handle=text_definition["package"] #String
			font_handle=text_definition["font"]
			font_color=text_definition["color"] #touple
			text_location=text_definition["xy"] #touple of center location
			rendered_string=font_handle.render(text_handle,False,font_color)
			self.rm.screen_2d.blit(rendered_string,text_location)
		
		self.displayDebugStringList()
		self.rm.pygame.display.flip()

	#gets the duration of the Credits sequence in seconds
	def getDurationSeconds(self):
		return 60
		
	def isWin(self):
		return self.book.isSuccessfulPlaythrough()

	#reads the contents of the config file into a list of list of dictionaries
	#output[0] --> slide 1 list
	#output[0][0] --> {"format":"Image","position",[12,34] ...
	#output[0][0]["type"] --> "Image"
	# each slide is one index of the list
	# each data type is an index within that list
	# each dictionary contains:
	# "format":("Image","Head1","Head2","Head3")
	# "trajectory":([x,y],[x1,y1,x2,y2])
	# "is_win":(True,False,None) #None applies to both win and lose conditions
	# "slides":(1,2,3, ... -1) #Number of slides the data will be displayed over, default is 1 slide, -1 means data is displayed for all slides
	# "package":(image.jpg,Title) #String representing either a filename (for image type) or the text to display (for header type)
	def parseConfig(self,config_path):
		out_slides=[]
		
		config_contents=self.rm.loadTXT(config_path)
		
		#clean file contents, remove comments, trim() spaces, and purge empty lines
		config_contents_clean=[]
		for row in config_contents:
			if("#" in row): row=row.split("#",1)[0] #strip comments
			row=row.strip() #trim whitespace
			if(len(row)>0): config_contents_clean.append(row)
		
		#parse file contents into a construct
		slide_package=None
		for row in config_contents_clean:
			if(row=="Slide"):
				if(not slide_package is None and len(slide_package)>0):
					out_slides.append(slide_package)
				slide_package=[]
			else:
				split_row=row.split(" ",2)
				if(len(split_row)<3):
					raise ValueError("Wall.Credits: Insufficient parameters ("+str(len(split_row))+") for row: "+str(row))
				if("[" in split_row[2]): #[W,2] is an optional parameter in row, if it is present, separate it out and parse it
					split_row=row.split(" ",3)
					if(len(split_row)<4):
						raise ValueError("Wall.Credits: Insufficient parameters ("+str(len(split_row))+") for row: "+str(row))
						
				#parse data type: Image, Head1, etc
				data_type=split_row[0]
				if(data_type not in ["Image","Head1","Head2","Head3"]):
					raise ValueError("Wall.Credits: Invalid data type ("+str(data_type)+") in row: "+str(row))
					
				#parse xy trajectory: (100,200) or (100,200,100,300)
				#first is stationary, second is moving over X frames
				xy_trajectory=split_row[1]
				if("(" in xy_trajectory and ")" in xy_trajectory):
					xy_trajectory=xy_trajectory.replace("(","")
					xy_trajectory=xy_trajectory.replace(")","")
					xy_trajectory_split=xy_trajectory.split(",")
					xy_trajectory_list=[]
					if(len(xy_trajectory_split)==2 or len(xy_trajectory_split)==4):
						for xy_component in xy_trajectory_split:
							try:
								xy_trajectory_list.append(int(xy_component))
							except:
								raise ValueError("Wall.Credits: Unable to parse XY trajectory ("+str(xy_component)+") in row: "+str(row))
					else:
						raise ValueError("Wall.Credits: Invalid number of arguments to XY trajectory ("+str(len(xy_trajectory_split))+") in row: "+str(row))
				else:
					raise ValueError("Wall.Credits: Invalid XY trajectory ("+str(xy_trajectory)+") in row: "+str(row))
				scope=[None,1] #default scope: appear in both win and lose conditions, and appear for only one slide
				if(len(split_row)>3):
					scope_str=split_row[2]
					scope_str=scope_str.replace("[","")
					scope_str=scope_str.replace("]","")
					scope_split=scope_str.split(",")
					if(len(scope_split)>1):
						if(scope_split[0]=="W"):
							scope[0]=True
						elif(scope_split[0]=="L"):
							scope[0]=False
					try:
						scope[1]=int(scope_split[-1])
					except:
						raise ValueError("Wall.Credits: Unable to parse frame count scope definition ("+str(scope_str)+") in row: "+str(row))
				package=split_row[-1]
				slide_package.append({"format":data_type,
									"trajectory":xy_trajectory_list,
									"is_win":scope[0],
									"slides":scope[1],
									"package":package})
				
		#append final slide
		if(not slide_package is None and len(slide_package)>0):
			out_slides.append(slide_package)
		
		return out_slides

if __name__ == "__main__":
	credit=Credits(None)
	print(credit.parseConfig(credit.BACKUP_DIRECTORY+"config.txt"))
