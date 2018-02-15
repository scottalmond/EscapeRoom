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

Usage:
This chapter will first look in the PRIMARY_DIRECTORY for:
- a series of images prepended with "XXW_" where "XX" is a numeric from 00 to 99 (00 displays first)
	"W" refers to a win condition, "L" refers to the image displayed when the game room
	is lost (not completed in 60 minutes)
- a coporate_logo.mp4 video file
- a CSV file containing the following columns:
Type, Value.  Type is a tag like HEADER or NAME.  Value is a string.
ex: "HEADER_1, Hyperspace", "HEADER_2, Design & Programming", "NAME, Scott Almond",
"HEADER_2","2D Art", "FINAL, Special Thanks"
HEADER_1, HEADER_2 are similar to work procesor headers that decrease in size
for higher values
NAME is a plain text name
FINAL is text that will appear statically at the end of the scrolling logos
such as special thanks
"""

from util.Chapter import Chapter

class Credits(Chapter):
	PRIMARY_DIRECTOR='/home/pi/Documents/corporate_credits/'
	BACKUP_DIRECTORY='/home/pi/Documents/EscapeRoom/src/chapters/wall/assets/credits/'
	MUSIC_PATH='./chapters/wall/assets/credits/escaperoom01_pre01_0.mp3'
	MUSIC_ENABLED=False
	
	def __init__(self,this_book):
		super().__init__(this_book)

	
	def clean(self):
		super().clean()
		self.images_win=[]
		self.images_lose=[]

	def dispose(self,is_final_call):
		super().dispose(is_final_call) 
		

	def enterChapter(self,unix_time_seconds):
		super().enterChapter(unix_time_seconds)
		self.book.endCountdown() #end timer if not already done
		if(self.MUSIC_ENABLED):
			self.rm.pygame.mixer.music.load(MUSIC_PATH)
			self.rm.pygame.mixer.music.play()
		self.background_color=(0,0,255)

	def exitChapter(self):
		super().exitChapter()
		if(self.MUSIC_ENABLED):
			self.rm.pygame.mixer.music.stop()

	def update(self,this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds):
		super().update(this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds)
		elapsed_time_seconds=self.book.getCountdownElapsed()
		elapsed_minutes=int(elapsed_time_seconds/60)
		elapsed_seconds=int(elapsed_time_seconds%60)
		debug_strings=["Successful: "+str(self.book.isSuccessfulPlaythrough()),
					   "Elapsed: "+str(elapsed_minutes)+" m "+str(elapsed_seconds)+" s"]
		self.setDebugStringList(debug_strings,this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds)

	def draw(self):
		super().draw()
		self.rm.screen_2d.fill(self.background_color)
		self.displayDebugStringList()
		self.rm.pygame.display.flip()
