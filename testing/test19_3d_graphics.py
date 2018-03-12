import time

class Test19:
	ASSET_FOLDER='chapters/wall/assets/hyperspace/'
	POD_3D_MODEL='Pod.obj'
	OVERSAMPLE_RATIO_3D=4
	
	def __init__(self):
		import sys
		sys.path.insert(1, '/home/pi/pi3d')
		import pi3d
		self.pi3d=pi3d
		
		self.display_3d = self.pi3d.Display.create(samples=self.OVERSAMPLE_RATIO_3D)
		self.display_3d.set_background(0,0,0,0)#transparent background

		self.camera_3d = self.pi3d.Camera(is_3d=True)
		self.camera_3d_overlay = self.pi3d.Camera(is_3d=False) #2d graphics overlay for GUI

		self.shader_3d = self.pi3d.Shader("uv_light") #grr, pi3d has an assertion that shaders need to be created in the same thread that pi3d was loaded in
		self.shader_3d_overlay = self.pi3d.Shader("uv_flat")

		print("ResourceManager.__create3dgraphics: complete")
		
		self.mykeys = pi3d.Keyboard()
		
		self.camera_3d.position((0,0,-10))
		
		self.sphere=self.pi3d.Sphere(radius=0.4, slices=16, sides=16)
		self.sphere.set_shader(self.shader_3d)

	def draw(self):
		while(self.display_3d.loop_running()):
			self.sphere.draw()
			k = self.mykeys.read()
			if k >-1:
				if k==27:
					mykeys.close()
					self.display_3d.stop()
				break

Test19().draw()


##display rings, allow free camera movement, display FPS, display GUI

##notes on backgrounds:
##using Pi3D rendering into a ellipsoid with texture on the inside (and rendering foreground objects): 17 FPS
##using code to polar transform a 2k x 2k image (and nothing else): ~2FPS
##using OpenCV to polar transform a 2k x 2k image (and nothing else): ~5 FPS
##playing a video using omxplayer-wrapper behind pi3d (and rendering foreground objects): 25 FPS

#import sys
#sys.path.insert(1, '/home/pi/pi3d')
#import pi3d
##from rotatingCamera import RotatingCamera
#import time
#import os
#import pygame
#import math
#import numpy as np
#import wiringpi as wp

#display = pi3d.Display.create(samples=4)
#background_rgba=(0.0,0.0,0.0,0.0) #transparent
#display.set_background(background_rgba[0],background_rgba[1],background_rgba[2],background_rgba[3])


#HWIDTH, HHEIGHT = display.width / 2.0, display.height / 2.0
#QWIDTH = HWIDTH/2 # quarter width
#QHEIGHT = HHEIGHT/2 # quarter height

#mykeys = pi3d.Keyboard()

#cam = pi3d.Camera(is_3d=True) #RotatingCamera(10,mymouse)#pi3d.Camera(is_3d=True)#
#cam.position((0,0,-10))
#cam2d = pi3d.Camera(is_3d=False)

#shader = pi3d.Shader("uv_light")
#shader2d = pi3d.Shader("uv_flat")

#number_sprite_list=[]
#number_sprite_id=0;
#for rep in range(0,10):
	#number_texture=pi3d.Texture("textures/transparent_text_"+str(rep)+".png",True,mipmap=False)#mipmap is turning off the re-scaling
	#number_handle=pi3d.ImageSprite(camera=cam2d,texture=number_texture,shader=shader2d,w=200,h=200,x=-250,y=0,z=2)
	#number_sprite_list.append(number_handle)

#sprite3_texture = pi3d.Texture("textures/cloud5.png",True)

#sprite3_handle = pi3d.ImageSprite(texture=sprite3_texture,shader=shader2d, w=5.0, h=5.0, z=-3.0)#,w=1024,h=1024 #camera=cam2d,

#font=pi3d.Font("fonts/NotoSerif-Regular.ttf",(128,255,128,255))

#font_colour = (255, 255, 255, 255)
#working_directory = os.path.dirname(os.path.realpath(__file__))
#font_path = os.path.abspath(os.path.join(working_directory, 'fonts', 'NotoSans-Regular.ttf'))
#pointFont = pi3d.Font(font_path, font_colour, codepoints=list(range(32,128)))
#text = pi3d.PointText(pointFont, cam2d, max_chars=200, point_size=32)
#newtxt = pi3d.TextBlock(-HWIDTH+30, HHEIGHT-30, 0.1, 0.0, 40, #text_format="Static str",
          #size=0.99, spacing="F", space=0.05, colour=(1.0, 0.0, 1.0, 1.0))
#text.add_text_block(newtxt)

#model_filename=["ring007.obj","Pod.obj"]#,"space001.obj"],"pod001.obj"
#model_list=[]
#background_filename="space002.obj";

#TFOG = ((background_rgba[0], background_rgba[1], background_rgba[2], 0.01), 25.0)

#for rep in range(len(model_filename)):
	#this_filename=model_filename[rep]
	#model = pi3d.Model(camera=cam, file_string="models/"+this_filename, x=0.0, y=0.0, z=3*rep,rx=90.0*("ring" in this_filename),ry=0.0,rz=0.0)
	#model.set_shader(shader)
	#model_list.append(model)
#background_mult=15.0#0.05

#t=0
#start_time=time.time()
#clock = pygame.time.Clock()

#screen_cap_id=0;

#screencap_prefix=str(time.time())

#u1=0.0
#v1=0.0

##GPIO section

#GPIO_OUT_NUMBERS=[24,7,21,5,6,27];
#GPIO_OUT_NAMES=["BTN_1","FIRE","JOY_1","JOY_2","JOY_3","JOY_4"];

#GPIO_IN_NUMBERS=[25,26,28,29,22];
#GPIO_IN_NAMES=["PWMA_ENABLE","PWMB_ENABLE","M1_RED","M2_GREEN","M3_BLUE"];

#wp.wiringPiSetup()
#for this_pin in GPIO_OUT_NUMBERS:
	#wp.pinMode(this_pin,wp.GPIO.INPUT)
	#wp.pullUpDnControl(this_pin,wp.GPIO.PUD_UP)

#for this_pin in GPIO_IN_NUMBERS:
	#wp.pinMode(this_pin,wp.GPIO.OUTPUT)
	#wp.digitalWrite(this_pin,1)
	
#frame_id=1;
#led_toggle_state=1;
#led_toggle_index=0;
#LED_STATE=[[0,0,0],[1,0,0],[0,1,0],[0,0,1],[1,1,0],[1,0,1],[0,1,1],[1,1,1]]
#joy_state=[0,0,0,0,0]#index zero is fire, 1-4 are {right,up,left,down}

#cross_hairs=[0,0]
#cross_hair_step=30.0;

#keys_pressed=[]

#import os
#import subprocess
#from omxplayer.player import OMXPlayer
#play_video=False
#video_file='/home/pi/Documents/aux/star_tours_intro.mp4'
#video_file2='/home/pi/Documents/aux/corporate_logo.mp4'
#video_file3='/home/pi/Documents/aux/FIBER OPTICAL (loop).mp4'
#play_audio=True
#audio_file='/home/pi/Documents/aux/Daft Punk - End of Line HQ.mp3'
#pygame.mixer.init()
#pygame.mixer.music.load(audio_file)
##vid2=OMXPlayer(video_file2,args=['--no-osd'])
##vid2.pause()
#play_background_video=False
#if(play_background_video):
	##vid_back=OMXPlayer(video_file3,args=['--no-osd','-o','local'])
	#vid_back=OMXPlayer(video_file3,args=['--no-osd','-o','local','--layer','-100'])
	#time.sleep(2)
	#vid_back.pause()
	#vid_back.set_aspect_mode('stretch')
	#vid_back_width=1920*2
	#vid_back_height=1080*2
	#vid_back.set_video_pos(-vid_back_width/2+HWIDTH,-vid_back_height/2+HHEIGHT,vid_back_width/2+HWIDTH, vid_back_height/2+HHEIGHT)
	#vid_back.play()

#while display.loop_running():
	##GPIO section:
	##print("FRAME: %d" % frame_id);
	#frame_id=frame_id+1;
	#for pin_id in range(len(GPIO_OUT_NUMBERS)):
		#gpio_state=wp.digitalRead(GPIO_OUT_NUMBERS[pin_id]);
		##print(GPIO_OUT_NAMES[pin_id]+(": %d" % gpio_state))
		#if(pin_id>=1): joy_state[pin_id-1]=1-gpio_state#if joystick moved, update state
	##print("JOY STATE: ",joy_state)
	#this_led_toggle=wp.digitalRead(GPIO_OUT_NUMBERS[0]);#read BTN_1
	##print("DEBUG 1: %d" % (led_toggle_state==0))
	##print("DEBUG 2: %d" % (this_led_toggle>0))
	##print("DEBUG 3: %d" % (led_toggle_state==0 and this_led_toggle>0))
	#if(led_toggle_state==0 and this_led_toggle>0):#if button was OPEN and is now THRU, toggle led state
		#led_toggle_index=led_toggle_index+1
		#if(led_toggle_index>=len(LED_STATE)): led_toggle_index=0
		##print("DEBUG 4: %d" % led_toggle_index)
		#this_led_truple=LED_STATE[led_toggle_index]
		##print("DEBUG 5: %d" % len(this_led_truple))
		#for this_led in range(len(this_led_truple)):
			#wp.digitalWrite(GPIO_IN_NUMBERS[2+this_led],1-this_led_truple[this_led])
		#if(play_video and led_toggle_index==1):
                    #vid1=OMXPlayer(video_file,args=['--no-osd','-o','local'])
                    #vid1.pause()
                    ##vid1.set_alpha(200)
		#if(play_video and led_toggle_index==2):
                    ##vid1.set_alpha(255)
                    #vid1.play()
                    ##os.system('mkfifo t cat t | omxplayer --no-osd -b '+video_file+' &')
                    ##myprocess=subprocess.Popen(['omxplayer','-b',video_file],stdin=subprocess.PIPE)
                    ##sleep(10)
                    ##myprocess.stdin.write('q')
		#if(play_video and led_toggle_index==3):
                    #vid1.quit()
                    ##vid1.pause()
		#if(play_video and led_toggle_index==4):
                    ##vid2=OMXPlayer(video_file2)
                    ##vid2=OMXPlayer(video_file2)
                    #vid2=OMXPlayer(video_file2,args=['--no-osd'])
                    #vid2.play()
                    ##os.system('echo p > t rm t')
                    ##myprocess.stdin.write('q')
		#if(play_video and led_toggle_index==5):
                    #vid2.quit()
		#if(play_audio and led_toggle_index==6):
                    #pygame.mixer.music.play(loops=-1,start=0.0)
		#if(play_video and led_toggle_index==7):
                    #vid3=OMXPlayer(video_file3,args=['--no-osd','--loop'])
                    #vid3.mute()
		#if(play_video and led_toggle_index==0):
                    #vid3.quit()
		#if(play_audio and led_toggle_index==0):
                    #pygame.mixer.music.stop()
                    #pygame.mixer.music.rewind()
	#led_toggle_state=this_led_toggle
	##print("LED_STATE: %d" % led_toggle_index)
	
	#joystick_moved=False
	##update cross hairs
	#if(joy_state[3]):#left, -x
		#cross_hairs[0]=cross_hairs[0]-cross_hair_step
		#joystick_moved=True
	#elif(joy_state[1]):#right, +x
		#cross_hairs[0]=cross_hairs[0]+cross_hair_step
		#joystick_moved=True
	#if(joy_state[2]):#up, +y
		#cross_hairs[1]=cross_hairs[1]+cross_hair_step
		#joystick_moved=True
	#elif(joy_state[4]):#down, -y
		#cross_hairs[1]=cross_hairs[1]-cross_hair_step
		#joystick_moved=True
		
	#cross_hairs[0]=np.clip(cross_hairs[0],-450,450)#x limit
	#cross_hairs[1]=np.clip(cross_hairs[1],-350,350)#y limit
	
	##tx=-display.width/2+150;
	##ty=display.height/2-50;
	##text = pi3d.String(font=font,string=time.strftime('%H:%M:%S',time.gmtime()),camera=cam.CAMERA,x=tx,y=ty,z=1.0,is_3d=False)
	##text.set_shader(shader);
	
	##newtxt.set_text('FPS: '+str(t))
	##time_elapsed=(time.time()-start_time)
	#this_str='FPS: %6.1f' % clock.get_fps()#WHY CANNOT I do time.time()-start_time?  returns {:s}
	##this_str='FPS: %6.1f %d' % (clock.get_fps(),len(model_list))
	##this_str=this_str+("(%d,%d,%d),(%d,%d,%d)" % (u1,u2,u3,v1,v2,v3))
	#clock.tick()
	#newtxt.set_text(this_str)
	
	##text.regen()
	##text.draw()
	
	##sprite.draw()
  
	##cam.update(mymouse)
	#background_mult=background_mult+0.005
	##background_model.scale(background_mult,background_mult,background_mult)
	##background_model.draw()
	
	##stars2.update(number_sprite_id)
	##stars2.draw()
	
	##stars.update(number_sprite_id)
	##if(joy_state[0]): stars.draw()
	
	#u1=0#((number_sprite_id/10)%40)/40.0
	#v1=(number_sprite_id%40)/40.0
	
	##background_sphere.set_offset((u1,v1))
	#if(play_background_video):
		#if(joystick_moved):
			##vid_back.set_video_pos(cross_hairs[0]+400, cross_hairs[1]+400, cross_hairs[0]+200+400, cross_hairs[1]+200+400)
			#vid_back.set_video_pos(-vid_back_width/2+cross_hairs[0]*2+HWIDTH,
								   #-vid_back_height/2-cross_hairs[1]*2+HHEIGHT,
								   #vid_back_width/2+cross_hairs[0]*2+HWIDTH,
								   #vid_back_height/2-cross_hairs[1]*2+HHEIGHT)
	#else:
		#pass
		##background_sphere.draw(shader,[sphere_texture])
	##background_sphere.scale(background_mult,background_mult*4,background_mult)
	
	#for model in model_list:
		#model.draw()
	
	#sprite3_handle.draw()
	##sprite2_handle.draw()
	#frames_per_number=40
	#number_sprite_list[math.floor(number_sprite_id/frames_per_number)].position(cross_hairs[0],cross_hairs[1],2.0)
	#number_sprite_list[math.floor(number_sprite_id/frames_per_number)].draw()
	#number_sprite_id=number_sprite_id+1
	#if(number_sprite_id>=(frames_per_number*10)):
		#number_sprite_id=0
		
	#text.regen()
	#text.draw()
	#k=mykeys.read()
	#t+=1.0
	#if k==97: #'a'
		#pi3d.screenshot('/home/pi/Documents/EscapeRoom/screencaps/'+screencap_prefix+'_'+str(screen_cap_id)+'.jpg')
		#screen_cap_id=screen_cap_id+1
	##if k>=0:
	##	keys_pressed.append(k)
	#if k==27:#esc
		#break
	
#mykeys.close()
#display.destroy()
##logger.info('''DESTROY DONE''')
##logger.info('FPS: %6.2f',t/(time.time()-start_time))
#for k in keys_pressed:
	##logger.info('KEY: %d',k)
	#pass
##logger.info('''DONE''')
