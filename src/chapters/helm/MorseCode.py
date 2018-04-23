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
Chapter waits for a command from the Proctor (through the Wall)
before proceeding to the next chapter

Usage:


"""

from util.Chapter import Chapter

class MorseCode(Chapter):
	
	MC_FONT_FNAME = 'CourierPrimeCode.ttf'
	MC_FONT_SIZE = 128
	PROMPT_X = 100
	PROMPT_Y = 300
	PASSWORD = "SPACE"
	MESSAGE = "Congratulations!" #Reward for solving puzzle - currently a placeholder
	
	def __init__(self,this_book):
		super().__init__(this_book)
		
		print("Helm."+self.getTitle()+".init: is_debug: "+str(self.is_debug))
		
		if(self.is_debug):
			print("Helm."+self.getTitle()+": Create Chapter Object")
		
	def clean(self):
		super().clean()
		self.font_path = self.UTIL_ASSET_FOLDER + self.MC_FONT_FNAME
		self.mc_font = self.rm.pygame.font.Font(self.font_path, self.MC_FONT_SIZE)
		self.addDot = False
		self.addDash = False
		self.sequence = ""
		self.elapsed_seconds_last_morse = 0
		self.elapsed_seconds_last_text = 0
		self.decoded_text = ""
		self.valid_seq = True
		self.text_color = (255,255,255)
		self.blank_space = ""
		self.display_error = False
		self.correct_password = False
		
	def dispose(self,is_final_call):
		super().dispose(is_final_call) 
		
	def enterChapter(self,unix_time_seconds):
		super().enterChapter(unix_time_seconds)
		
		if(self.is_debug):
			print("Helm."+self.getTitle()+": enterChapter()")
			
		self.background_color=(0,0,0)
		if(self.is_debug):
			self.background_color=(0,0,255)
			
	def exitChapter(self):
		super().exitChapter()
		self.book.startCountdown() #once Proctor commands book out of Standby, begin timer
		
		if(self.is_debug):
			print("Helm."+self.getTitle()+": exitChapter()")
		
	def update(self,this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds,packets):
		super().update(this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds,packets)
		
		self.seconds_since_last_frame=this_frame_elapsed_seconds-previous_frame_elapsed_seconds
		self.this_frame_number=this_frame_number

		self.__updateCursor(this_frame_elapsed_seconds)
		
		self.__updateSequence(this_frame_elapsed_seconds)
		
		self.__updateText(this_frame_elapsed_seconds)
		
		self.__updateError(this_frame_elapsed_seconds)
		
		self.setDebugStringList([],this_frame_number,this_frame_elapsed_seconds,previous_frame_elapsed_seconds)
		
	def draw(self):
		super().draw()
		
		self.rm.screen_2d.fill(self.background_color)
		
		self.displayDebugStringList()

		if(not self.correct_password):
			self.__displayPrompt()
			self.__drawSequence()
			self.__drawText()
		else: #show reward message if correct password has been entered
			rendered_message = self.mc_font.render(self.MESSAGE,1,(255,255,255))
			self.rm.screen_2d.blit(rendered_message,(self.PROMPT_X,self.PROMPT_Y))
		
		self.rm.pygame.display.flip()

	#cursor blinks
	def __updateCursor(self,this_frame_elapsed_seconds):
		blink_freq = 1
		self.cursor_visible = this_frame_elapsed_seconds % (1/blink_freq) < (0.5/blink_freq)

	#display prompt along with blinking cursor
	def __displayPrompt(self):
		rendered_prompt = self.mc_font.render("PASSWORD:",1,(255,255,255))
		self.rm.screen_2d.blit(rendered_prompt,(self.PROMPT_X,self.PROMPT_Y))

		if(self.cursor_visible):
			rendered_prompt2 = self.mc_font.render(self.blank_space + "_",0,(255,255,255))
			self.rm.screen_2d.blit(rendered_prompt2,(self.PROMPT_X,self.PROMPT_Y+self.MC_FONT_SIZE))
			
	#updates Morse Code sequence
	def __updateSequence(self,this_frame_elapsed_seconds):
		delay = 1 #after 1 second, will try to decode Morse sequence
		is_dot = self.rm.isDotPressed()
		is_dash = self.rm.isDashPressed()
		if(is_dot and is_dash): #no result if both are pressed simultaneously
			self.addDot = False
			self.addDash = False
		elif(is_dot):
			self.addDot = True
		elif(is_dash):
			self.addDash = True
		else: #symbol is added to sequence only after button is released
			if(self.addDot and self.addDash): #just in case
				self.addDot = False
				self.addDash = False
			elif(self.addDot):
				self.sequence = self.sequence + "."
				self.addDot = False
				self.elapsed_seconds_last_morse = this_frame_elapsed_seconds
			elif(self.addDash):
				self.sequence = self.sequence + "-"
				self.addDash = False
				self.elapsed_seconds_last_morse = this_frame_elapsed_seconds
			else: #if no input for 1 second, try to decode sequence
				if(this_frame_elapsed_seconds-self.elapsed_seconds_last_morse > delay and self.sequence != ""):
					self.__decodeSequence()
					self.elapsed_seconds_last_text = this_frame_elapsed_seconds
					self.sequence = ""
					if(self.valid_seq):
						self.blank_space = self.blank_space + " " #leading spaces for cursor/next Morse sequence
							
	#show ! symbol if invalid Morse sequence
	def __updateError(self,this_frame_elapsed_seconds):
		error_time = 1 #amount of time to display error
		if(not self.valid_seq and this_frame_elapsed_seconds-self.elapsed_seconds_last_text < error_time):
			self.display_error = True
		else:
			self.display_error = False

	def __drawSequence(self):
		rendered_seq = self.mc_font.render(self.blank_space+self.sequence,1,(255,255,255))
		self.rm.screen_2d.blit(rendered_seq,(self.PROMPT_X,self.PROMPT_Y+self.MC_FONT_SIZE))

	def __decodeSequence(self):
		if(self.sequence == ".-"):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "A"
		elif(self.sequence == "-..."):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "B"
		elif(self.sequence == "-.-."):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "C"
		elif(self.sequence == "-.."):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "D"
		elif(self.sequence == "."):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "E"
		elif(self.sequence == "..-."):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "F"
		elif(self.sequence == "--."):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "G"
		elif(self.sequence == "...."):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "H"
		elif(self.sequence == ".."):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "I"
		elif(self.sequence == ".---"):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "J"
		elif(self.sequence == "-.-"):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "K"
		elif(self.sequence == ".-.."):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "L"
		elif(self.sequence == "--"):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "M"
		elif(self.sequence == "-."):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "N"
		elif(self.sequence == "---"):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "O"
		elif(self.sequence == ".--."):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "P"
		elif(self.sequence == "--.-"):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "Q"
		elif(self.sequence == ".-."):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "R"
		elif(self.sequence == "..."):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "S"
		elif(self.sequence == "-"):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "T"
		elif(self.sequence == "..-"):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "U"
		elif(self.sequence == "...-"):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "V"
		elif(self.sequence == ".--"):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "W"
		elif(self.sequence == "-..-"):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "X"
		elif(self.sequence == "-.--"):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "Y"
		elif(self.sequence == "--.."):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "Z"
		elif(self.sequence == ".----"):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "1"
		elif(self.sequence == "..---"):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "2"
		elif(self.sequence == "...--"):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "3"
		elif(self.sequence == "....-"):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "4"
		elif(self.sequence == "....."):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "5"
		elif(self.sequence == "-...."):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "6"
		elif(self.sequence == "--..."):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "7"
		elif(self.sequence == "---.."):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "8"
		elif(self.sequence == "----."):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "9"
		elif(self.sequence == "-----"):
			self.valid_seq = True
			self.decoded_text = self.decoded_text + "0"
		else:
			self.valid_seq = False
		
	def __drawText(self):
		rendered_text = self.mc_font.render(self.decoded_text,1,self.text_color)
		self.rm.screen_2d.blit(rendered_text,(self.PROMPT_X,self.PROMPT_Y+self.MC_FONT_SIZE))
		if(self.display_error): #show error symbol if invalid Morse sequence
			rendered_error = self.mc_font.render(self.blank_space+"!",1,(255,0,0))
			self.rm.screen_2d.blit(rendered_error,(self.PROMPT_X,self.PROMPT_Y+self.MC_FONT_SIZE))

	#shows if input password is correct or not (via color)
	def __updateText(self,this_frame_elapsed_seconds):
		delay = 5 #wait this long before checking
		show_color_time = 1 #show result for this many seconds
		if(this_frame_elapsed_seconds-self.elapsed_seconds_last_text > delay and self.decoded_text != ""):
			if(self.decoded_text == self.PASSWORD):
				self.text_color = (0,255,0)
				if(this_frame_elapsed_seconds-self.elapsed_seconds_last_text > delay+show_color_time):
					self.correct_password = True #set flag to show reward message
			else:
				self.text_color = (255,0,0)
				if(this_frame_elapsed_seconds-self.elapsed_seconds_last_text > delay+show_color_time):
					self.decoded_text = "" #start over if incorrect password
					self.blank_space = ""
		else:
			self.text_color = (255,255,255)
