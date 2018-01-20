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
This class reads a mural image, polar projects the image into a sequence of frames
and then compiles those frames together into a video

Usage:
python3 HyperspaceVideoGenerator.py
in the output print out is an ffmpeg command; execute this command 
to consolidate individual frames into a movie

"""

MURAL_PATH='/home/logic/Documents/Projects/EscapeRoom/test05/scale_template_stars.jpg' #full path of the source mural image
#WARNING: all pre-existing jpg files in FRAME_PATH will be deleted by running this program
FRAME_PATH='/home/logic/Documents/Projects/EscapeRoom/test05/frames/' #folder location where intermediate frames are to be stored
VIDEO_PATH='/home/logic/Documents/Projects/EscapeRoom/test05/out_' #full path where output video file is to be stored
FPS=24 #frames per second

#note output resolution is capped at 1920x1080 by rpi hardware https://github.com/huceke/omxplayer/issues/280
OUTPUT_RESOLUTION=[1920,1080] #width, height in pixels to crop the output to.  Use None to disable cropping
POLAR_LOG_RADIUS=250 #fudge factor to adjust how much the edges are stretched vs the center
#affects the apparent speed because the pixels move over the same distane in less time
#lower values increase the apparent hyperspace speed effect
SHORT_MURAL_COPIES=6 #if several short murals are used to form one large mural, copy the short
#mural this many times and then offset each copy vertically by MURAL_HEIGHT_PX/SHORT_MURAL_COPIES
#if copies is 1, this code is effectively ignored

DURATION_SECONDS=10*SHORT_MURAL_COPIES
TOTAL_FRAMES=FPS*DURATION_SECONDS #number of frames used to go through one complete loop cycle of the background

#https://trac.ffmpeg.org/wiki/Limiting%20the%20output%20bitrate
MEGA_BITS_PER_SECOND=50 #bit rate limit of hardware
BUFFER_SIZE_BYTES=50e6#81290 #https://www.raspberrypi.org/forums/viewtopic.php?f=38&t=80020

import cv2
import numpy as np
from pathlib import Path #https://stackoverflow.com/questions/1548704/delete-multiple-files-matching-a-pattern
import time
import subprocess
import math

print("START")

mural=cv2.imread(MURAL_PATH)

#tesselate a short mural by copying it to the right and then vertically shifting it
tesselated_mural=np.empty([mural.shape[0],0,3])
vertically_shifted_mural=mural
for tess in range(SHORT_MURAL_COPIES):
	tesselated_mural=np.concatenate((tesselated_mural,vertically_shifted_mural),axis=1)
	if(SHORT_MURAL_COPIES>1):
		vertically_shifted_mural=np.concatenate((vertically_shifted_mural[math.floor(vertically_shifted_mural.shape[0]/SHORT_MURAL_COPIES):,:],
												 vertically_shifted_mural[:math.floor(vertically_shifted_mural.shape[0]/SHORT_MURAL_COPIES),:]),axis=0)

#print("shape: "+str(tesselated_mural.shape))
#tesselated_mural = cv2.resize(tesselated_mural,None,fx=0.25, fy=1, interpolation = cv2.INTER_LANCZOS4)
#print("shape2: "+str(tesselated_mural.shape))

#cv2.imwrite(FRAME_PATH+'tesselated_mural.jpg',tesselated_mural)
#assert 1==0

#combine two copies of mural to make looping seamless
#x  https://stackoverflow.com/questions/33239669/opencv-how-to-merge-two-images
#https://stackoverflow.com/questions/7589012/combining-two-images-with-opencv
mural_extended=np.concatenate((tesselated_mural,tesselated_mural),axis=1)

for p in Path(FRAME_PATH).glob("*.jpg"):
	p.unlink()

last_print_seconds=0
seconds_between_status=1
frame_index=0
for frame_index in range(TOTAL_FRAMES):
	if((time.time()-last_print_seconds)>seconds_between_status):
		print("Progress: "+str(frame_index)+" of "+str(TOTAL_FRAMES)+" ("+str(100*frame_index/TOTAL_FRAMES)+"%)")
		last_print_seconds=time.time()
		
	frame_width_pixels=mural.shape[1]
	if(not OUTPUT_RESOLUTION is None):#expedite processing by pre-cropping image before polar transform
		frame_width_pixels=OUTPUT_RESOLUTION[0]
	frame_rect=mural_extended[:,math.floor(frame_index*tesselated_mural.shape[1]/TOTAL_FRAMES):math.floor(frame_width_pixels+frame_index*(tesselated_mural.shape[1]/TOTAL_FRAMES))]

	#frame_img = cv2.logPolar(mural, (mural.shape[0]/2, mural.shape[1]/2), 150, cv2.WARP_FILL_OUTLIERS | cv2.WARP_INVERSE_MAP)
	#frame_pol = cv2.logPolar(frame_rect, (frame_rect.shape[0]/2, frame_rect.shape[1]/2), 130, cv2.WARP_FILL_OUTLIERS | cv2.WARP_INVERSE_MAP)# | cv2.INTER_NEAREST)
	frame_pol = cv2.logPolar(frame_rect, (frame_rect.shape[1]/2, frame_rect.shape[0]/2), POLAR_LOG_RADIUS, cv2.WARP_FILL_OUTLIERS | cv2.WARP_INVERSE_MAP | cv2.INTER_NEAREST)
	#cv2.INTER_CUBIC
	#cv2.INTER_LANCZOS4
	#transform flags: https://docs.opencv.org/2.4/modules/imgproc/doc/geometric_transformations.html
	
	if(not OUTPUT_RESOLUTION is None):
		top_px=math.floor(frame_pol.shape[0]/2-OUTPUT_RESOLUTION[1]/2) #row
		left_px=math.floor(frame_pol.shape[1]/2-OUTPUT_RESOLUTION[0]/2) #col
		frame_pol=frame_pol[top_px:(top_px+OUTPUT_RESOLUTION[1]),left_px:(left_px+OUTPUT_RESOLUTION[0])]#use central portion as crop area
	
	cv2.imwrite(FRAME_PATH+str(TOTAL_FRAMES-frame_index-1)+'.jpg',frame_pol)

#http://hamelot.io/visualization/using-ffmpeg-to-convert-a-set-of-images-into-a-video/
#subprocess.call('ffmpeg -r '+str(FPS)+' -s '+str(mural.shape[1])+'x'+str(str(mural.shape[0]))+' -i "'+FRAME_PATH+'%d.jpg" -vcodec libx264 -crf 25  -pix_fmt yuv420p out.mp4')
#ffmpeg -r 30 -s 1920x1080 -i /home/logic/Documents/Projects/EscapeRoom/test05/frames/%d.jpg -vcodec libx264 -crf 25  -pix_fmt yuv420p /home/logic/Documents/Projects/EscapeRoom/test05/out_M110.mp4
#ffmpeg -r 30 -s 3840x2160 -i /home/logic/Documents/Projects/EscapeRoom/test05/frames/%d.jpg -vcodec libx264 -crf 25  -pix_fmt yuv420p /home/logic/Documents/Projects/EscapeRoom/test05/out_M170_fullres.mp4
#ffmpeg -r 30 -s 3840x2160 -i /home/logic/Documents/Projects/EscapeRoom/test05/frames/%d.jpg -vcodec libx264  -pix_fmt yuv420p /home/logic/Documents/Projects/EscapeRoom/test05/out_M170_fullres.mp4

print("Command:")
#codec appears to make no difference in output file size
#print("ffmpeg -r "+str(FPS)+" -s "+str(OUTPUT_RESOLUTION[0])+"x"+str(OUTPUT_RESOLUTION[1])+" -i "+FRAME_PATH+"%d.jpg -vcodec libx264 -b:v "+str(MEGA_BITS_PER_SECOND)+"M -bufsize "+str(BUFFER_SIZE_BYES)+" -pix_fmt yuv420p "+VIDEO_PATH+"M"+str(POLAR_LOG_RADIUS)+"_b"+str(MEGA_BITS_PER_SECOND)+"_FPS"+str(FPS)+"_SEC"+str(DURATION_SECONDS)+".mp4")
print("ffmpeg -r "+str(FPS)+" -s "+str(OUTPUT_RESOLUTION[0])+"x"+str(OUTPUT_RESOLUTION[1])+" -i "+FRAME_PATH+"%d.jpg -preset veryslow -b:v "+str(MEGA_BITS_PER_SECOND)+"M -bufsize "+str(BUFFER_SIZE_BYTES)+" -pix_fmt yuv420p "+VIDEO_PATH+"M"+str(POLAR_LOG_RADIUS)+"_b"+str(MEGA_BITS_PER_SECOND)+"_FPS"+str(FPS)+"_SEC"+str(DURATION_SECONDS)+".mp4")
#tuning presets and decode speed https://trac.ffmpeg.org/wiki/Encode/H.264

print("DONE")
