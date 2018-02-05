# Overview

This project contains six interactive sequences, including video games and puzzles, which form a portion of a multi-player [Escape Room](https://en.wikipedia.org/wiki/Escape_room).  These sequences are written in Python3 and run on two Raspberry Pi 3's.  A Proctor oversees players and provides manual oversight via a third Raspberry Pi 3 connected to the other computers via an Ethernet switch.

TODO: video of deployed build

# Details

## Room
The escape room is themed after a Star Trek command bridge and is designed to build team work among a group of 5 employees.  Teams are given one hour to re-establish power to the ship, stock a cargo pod, then navigate the pod to stranded crew members.

TODO: Wide angle image of room

## Initialization
The proctor will send an initial command signal to begin the 60-minute timer on the Wall computer.  However, the Wall monitor will display only static noise while the Helm computer will begin the first puzzle.

## Chapter 1: Morse Code Puzzle
The Helm monitor displays a password prompt.  The player can provide two inputs: a dot and a dash by pressing the corresponding labeled concave buttons.  The correct password is acquired by solving puzzles elsewhere in the room.  Entering the correct password unlocks the screen to provide information needed to access other puzzles in the room.

TODO: 20-30 demo video

## Chapter 2: Light Puzzle
The main monitor displays static noise to convey a lack of power to run the ship's electronics.  The finale computer system monitors the electrical state of prerequisite puzzles and reports this information to the proctor.  Once all the preceding puzzle elements have been completed, the monitor exits the static noise display and automatically advances to the next chapter.

## Chapter 3: User Controls Tutorial
The main monitor displays the state of the player controls as inactive.  When a joystick or button is moved or pressed, the corresponding input is illuminated and remains active.  When all user inputs spread across five stations have been activated, the tutorial is considered complete and the display advances to the next chapter.

TODO: 10-20 demo video

## Chapter 4: Snake Game
The main monitor shows a Snake game where there are three sprites.  The sprites need to navigate around the 2D playing field to collect randomly appearing resources.  As resources are collected, the trail behind each sprite becomes longer.  If any sprite hits the tail of itself or another sprite, the tail is removed.  When the tail of a sprite gets long enough, an exit gate is presented for that sprite; entering this gate removes the sprite from the field.  Exiting all three sprites from the field constitutes completion of the Snake game.

The first two sprites are controlled via two different joysticks, one in the Captain's chair and one in the Helm.  The third sprite is controlled using two single-axis joysticks in the Wing stations.

TODO: 20-30 second demo video

## Chapter 5: Hyperspace Game
A cut scene is played showing the cargo pod exiting from the space ship, followed by entering a hyperspace tunnel.  The game play pulls inspiration from a boss battle in [Crash Bandicoot](https://youtu.be/Er0AzrrjrJI?t=14m47s).  The hyperspace tunnel consists of a long series of rings.  The hyper-lane is primarily straight with occasional branches leading to shorter or longer paths to the finish point.  The Helm monitor displays a map of the full maze that only one player can see.  Players must avoid hitting asteroids while traveling through the rings either by navigating the cargo pod around them or blowing them up with a laser.

TODO: 20-30 second demo video

## Chapter 6: Credits
Upon completion of the hyperspace puzzle, a credits sequence is played.  Half the screen is used to list the puzzle contributors one-puzzle-at-a-time.  When the room is completed within the allotted time, the other half shows images of the pod exiting hyperspace, landing on the planet, and the crew collecting supplies from the pod.  If the room is not completed in the allotted time, the artwork is replaced with images depicting the construction and integration of each puzzle.  Finally, a full-screen corporate logo is displayed.

TODO: 10-20 second demo video

# Dependencies

## Hardware
- Qty: 2, [Raspberry Pi 3](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/), each one drives a monitor
	- Qty: 2, [SanDisk 32GB microSDHC Card Mobile Ultra Class 10](https://www.newegg.com/Product/Product.aspx?Item=9SIA12K0N93630), holds operating system and project files
	- Qty: 1, [MicroUSB 5V 2.5A power supply](https://www.newegg.com/Product/Product.aspx?Item=9SIA7PR5WA8871), used to power the Raspberry Pi connected to the Helm monitor
	- Qty: 1, [MC33866 Motor Driver Shield](http://www.robotshop.com/en/mc33886-raspberry-pi-motor-driver-board-raspberry-pi.html), used to supply enough current to drive several strips of LEDs
		- Qty: 1, [2.1mm 12VDC 5A Power Supply](https://www.newegg.com/Product/Product.aspx?Item=9SIA27C6J20741), supply used to power both LEDs and main monitor Raspberry Pi
	- Qty: 1, [High-Precision AD/DA Expansion Board](http://www.robotshop.com/en/raspberry-pi-high-precision-ad-da-expansion-board.html), reads analog voltages from human load cells, also detects changes in room light levels to trigger start of 1-hour window
	- Qty: 1, [Prototyping Pi Board](http://www.robotshop.com/en/prototyping-pi-board-raspberry-pi.html), soldering shield to hold quick-disconnect headers for buttons and joystick
		- Qty: 4, [2x5 Pin Shrouded Header](), quick disconnect header.  2x for button pairs, 1x for joystick, 1x for UART connection between Raspberry Pis
		- Qty: 2, [IDC 2x5 cable](www.robotshop.com/en/20cm-idc-2x5-cable.html), Cable used to mate with 2x5 header
- Qty: 1, [TODO TV](), primary monitor
	- Qty: 2, [6' HDMI Cable](https://www.newegg.com/Product/Product.aspx?Item=N82E16882021128), one for each monitor
	- Qty: 2, [HDMI-DVI adapter](https://www.newegg.com/Product/Product.aspx?Item=9SIAD4R5J10076), one for each monitor, as needed
	- Qty: 2, [HMDI-VGA adapter](https://www.newegg.com/Product/Product.aspx?Item=9SIA3521V29198), one for each monitor, as needed
- Qty: 1, [TODO Monitor](), Helm monitor
- Qty: 1, [Arcade Joystick](https://www.sparkfun.com/products/9136), 4-axis bang-bang actuation with fire button
- Qty: 4, [Concave Button](https://www.sparkfun.com/products/9337), bang-bang actuation
- Qty: 1, [Z533 Logitech Sound System](https://www.logitech.com/en-us/product/z533-multimedia-speaker-system)
- Qty: 4, [5m 5050 SMD Supernight RGB LED strip](https://www.newegg.com/Product/Product.aspx?Item=9SIA3W31A14276)
- Qty: 4, [Human load cell](https://www.newegg.com/Product/Product.aspx?Item=9SIADMZ5Z97241), each cell contains two resistors in series, one is a fixed X (TODO) ohms, the other is a strain gauge that increases (TODO) by Y (TODO) ohms when 50 lbs is applied

## Software
- Raspberry Pi Operating System
	- TODO: SD Card writer
	- [Noobs v2.4.5](https://www.raspberrypi.org/downloads/noobs/)
		- Burn operating system to the microSD card then insert into Raspberry Pi and apply power
		- On first boot, check only Raspbian from the menu (press space) then proceed with the install (press i)
	- Change Monitor Resolution
		- Start >> Preferences >> Raspberry Pi Configuration >> System >> Resolution >> Set Resolution ... >> DMT mode 82 1920x1080 16:9
	- Command: sudo reboot
		- Enable new monitor settings to take effect
	- Configure Keyboard
		- Start >> Preferences >> Mouse and Keyboard Settings >> Keyboard >> Keyboard Layout... >> United States >> English (US)
	- Command: _sudo apt-get update_
		- Connect to the internet then enter command into a terminal shell
	- Command: _sudo apt-get upgrade_
		- Type 'y' at the prompt
- Git
	- Command: _cd /home/pi/Documents/_
		- Parent folder where the project files will be stored
	- Command: _git init_
		- Initialize a Git repository in the current location
	- Command: _git config user.email "USERNAME@EMAIL.COM"_
		- Set the Git parameters for the current user and folder
	- Command: _git config user.name "USERNAME"_
	- Command: _git config credential.helper 'cache --timeout=900'_
		- 900 is the default number of seconds before a session times out and the Git username/password must be reentered to push code changes
	- Command: _git clone https://github.com/scottalmond/EscapeRoom.git_
		- Creates a new folder at the following location:
		- /home/pi/Documents/EscapeRoom/
- Wiring Library
	- Command: _sudo pip3 install wiringpi_
		- Used to read from and write to discrete inputs like buttons, joystick and LEDs
	- Start >> Preferences >> Raspberry Pi Configuration >> Interfaces
		- Set SPI to Enabled
		- Set I2C to Enabled
		- Set Serial to Enabled
		- Set Remote GPIO to Enabled
- [Pi3D](https://github.com/tipam/pi3d) ([FAQ](https://pi3d.github.io/html/FAQ.html))
	- Command: _sudo pip3 install pi3d_
		- Used for 3D graphics
	- Command: _sudo raspi-config_
		- 7 Advanced Operations >> A3 Memory Split >> 256
		- To allow greater utilization of the GPU, a larger memory allocation is needed [source](http://pi3d.github.io/html/ReadMe.html#setup-on-the-raspberry-pi)
- Sound
	- Command: _amixer cset numid=3 1_
		- Change the audio to come out over the headphone jack [source](https://www.raspberrypi.org/documentation/configuration/audio-config.md)
- Sockets
	- Command: _sudo apt-get install socket_
		- allow communication ebtween raspberry pi's
		- https://www.youtube.com/watch?v=l0p-NvmoeUA
		- https://www.raspberrypi.org/forums/viewtopic.php?f=36&t=81505
	- Command: _sudo apt-get install nmap_
	- Command: _pip3 install python-nmap_
		- Python3 wrapper for nmap command
		- https://pypi.python.org/pypi/python-nmap
	- xxx
		- https://www.modmypi.com/blog/how-to-give-your-raspberry-pi-a-static-ip-address-update
		- Used to set the static IP address of the raspberry pi
			- PROCTOR: 192.168.0.170
			- WALL: 192.168.0.160
			- HELM: 192.168.0.150
- Reboot
	- Command: _sudo reboot_
		- Clean all installs and settings changes
- Functional Test
	- Command: _cd /home/pi/Documents/EscapeRoom/_
	- Command: TODO
		- Run a functional test of all library dependencies

xxx TODO sudo apt-get install vlc --> omxplayer
xxx TODO sudo pip3 install omxplayer-wrapper



### Development Tools

- Markdown editor for editing design documents
	- Download the latest .deb from: [Remarkable](https://remarkableapp.github.io/linux/download.html)
	- Command: _sudo apt install /home/linaro/Downloads/remarkable_1.87_all.deb_

- opencv for rpi: https://www.pyimagesearch.com/2017/09/04/raspbian-stretch-install-opencv-3-python-on-your-raspberry-pi/
	- CMake:
		- command: sudo apt-get install build-essential cmake pkg-config
	- Image I/O Packages:
		- command: sudo apt-get install libjpeg-dev libtiff5-dev libjasper-dev libpng12-dev
			- Type 'y' at the prompt
	- Video I/O Packages:
		- command: sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
		- command: sudo apt-get install libxvidcore-dev libx264-dev
	- GTK Development Library:
		- command: sudo apt-get install libgtk2.0-dev libgtk-3-dev
	- OpenCV Optimizations:
		- command: sudo apt-get install libatlas-base-dev gfortran
	- OpenCV Source Code:
		- command: cd ~
		- command: wget -O opencv.zip https://github.com/Itseez/opencv/archive/3.3.0.zip
		- command: unzip opencv.zip
		- command: wget -O opencv_contrib.zip https://github.com/Itseez/opencv_contrib/archive/3.3.0.zip
		- command: unzip opencv_contrib.zip
	- Compile OpenCV:
		- command: cd ~/opencv-3.3.0/
		- command: mkdir build
		- command: cd build
		- command: cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D INSTALL_PYTHON_EXAMPLES=ON -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib-3.3.0/modules \-D BUILD_EXAMPLES=ON ..
	- Increase Swap Space Size:
		- command: sudo nano /etc/dphys-swapfile
			- Change CONF_SWAPSIZE=100 to CONF_SWAPSIZE=1024
			- Ctrl + X, Y, Enter
	- Restart swap service:
		- Command: sudo /etc/init.d/dphys-swapfile stop
		- Command: sudo /etc/init.d/dphys-swapfile start
	- Compile OpenCV
		- command: cd ~/opencv-3.3.0/build/
		- command: make -j4
			- This will take ~90 minutes
			- Note: This may freeze the system and require a reboot.  To resume the compile from the latest checkpoint, re-run the above cd and make commands after power cycling the raspberry pi
	- Install OpenCV
		- command: cd ~/opencv-3.3.0/build/
		- Command: sudo make install
		- Command: sudo ldconfig
		- Command: cd /usr/local/lib/python3.5/dist-packages/
		- Command: sudo mv cv2.cpython-35m-arm-linux-gnueabihf.so cv2.so
			- Done in order to rename OpenCV to shorter name
	- Install verification
		- Command: python3
		- Command: import cv2
		- Command: cv2.__version__
			- Returns '3.3.0'
		- Command: quit()
	- Return Swap Space to Original Size:
		- command: sudo nano /etc/dphys-swapfile
			- Change CONF_SWAPSIZE=1024 to CONF_SWAPSIZE=100
			- Ctrl + X, Y, Enter
	- Restart swap service:
		- Command: sudo /etc/init.d/dphys-swapfile stop
		- Command: sudo /etc/init.d/dphys-swapfile start
- Gimp, 2D image processing
	- command: sudo apt-get install gimp
- Blender, 3D model processing
	- command: sudo apt-get install blender
- Mini Mic
	- command: arecord --device=plughw:1,0 --format S16_LE --rate 44100 -c1 test.wav -d 5

A home computer running Ubuntu 16 was used to polar-project a mural into a sequence of frames that were stitched together to form the background video of the Hyperspace game.
- ffmpeg for ubuntu
	- command: sudo apt-get install ffmpeg
	- command: sudo apt autoremove
- opencv for ubuntu: https://www.pyimagesearch.com/2016/10/24/ubuntu-16-04-how-to-install-opencv/
	- command: sudo apt-get install build-essential cmake pkg-config
	- command: sudo apt-get install libjpeg8-dev libtiff5-dev libjasper-dev libpng12-dev
	- command: sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev libv4l-dev
	- command: sudo apt-get install libxvidcore-dev libx264-dev
	- command: sudo apt-get install libgtk-3-dev
	- command: sudo apt-get install libatlas-base-dev gfortran
	- command: sudo apt-get install python3.5-dev
	- command: cd ~
	- command: wget -O opencv.zip https://github.com/Itseez/opencv/archive/3.4.0.zip
	- command: unzip opencv.zip
	- command: wget -O opencv_contrib.zip https://github.com/Itseez/opencv_contrib/archive/3.4.0.zip
	- command: unzip opencv_contrib.zip
	- command: cd ~
	- command: wget https://bootstrap.pypa.io/get-pip.py
	- command: sudo python get-pip.py
	- command: pip3 install numpy
	- command: cd ~/opencv-3.4.0/
	- command: mkdir build
	- command: cd build
	- command: cmake -D CMAKE_BUILD_TYPE=RELEASE  -D CMAKE_INSTALL_PREFIX=/usr/local  -D INSTALL_PYTHON_EXAMPLES=ON  -D INSTALL_C_EXAMPLES=OFF  -D OPENCV_EXTRA_MODULES_PATH=~/opencv_contrib-3.4.0/modules  -D PYTHON3_EXECUTABLE=/usr/bin/python3  -D PYTHON_INCLUDE_DIR=/usr/include/python3.5m  PYTHON_LIBRARY=/usr/lib/x86_64-linux-gnu/libpython3.5m  -D BUILD_EXAMPLES=ON ..
	- command: make -j4
	- command: make clean
	- command: make
	- command: sudo make install
	- command: sudo ldconfig
	- command: cd /usr/local/lib/python3.5/dist-packages/
	- command: ls -l
		- Should show cv2.cpython-35m-x86_64-linux-gnu.so in th ouput list
	- command: sudo mv cv2.cpython-35m-x86_64-linux-gnu.so cv2.so
	- command: python3
	- command: import cv2
	- command: cv2.__version__
		- Should print '3.4.0'
	- command: quit()
	- command: rm -rf opencv-3.4.0 opencv_contrib-3.4.0 opencv.zip opencv_contrib.zip

	


sudo apt-get install geany

git pull origin master

git add . && git commit -am "comment"

git push origin master

# About

Our local site president visited an escape room during his travels and found it was a useful activity for building team work.  He subsequently provided hardware funds for an engineering group to pursue building our own escape room on site.  Over a dozen engineers joined and contributed directly to this project.  Scott Almond is one of those engineers and my role is to supply the finale for the escape room.  I developed the finale plan and code.  I also reached out to multiple artists to commission 2D art, 3D art, and musical assets.

# Licensing

## Code

The Python 3 code used within this project was developed by Scott Almond and released under the following license.  These files contain "Licensed under the Apache License, Version 2.0" in the code header.

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Visual Art Assets

2D and 3D art assets were commissioned from Chilly Prins for this project and released under the following license.  These files are postpended with "by_chilly_prins" in the filenames.

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

## Audio Assets

Music was commissioned from Juan Goncebat for this project and released under the following license.  These files are postpended with "by_juan_goncebat" in the filenames.

[![License: CC BY 4.0](https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)

Sound effects were acquired from [Freesound](https://freesound.org/).

