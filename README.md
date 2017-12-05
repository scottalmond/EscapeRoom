# Overview

This project contains four interactive puzzles which form a portion of an [Escape Room](https://en.wikipedia.org/wiki/Escape_room).  Puzzles are written in Python3 and run on two Raspberry Pi 3's.

TODO: video of deployed build

# Details

## Room
The escape room is themed after a Star Trek command bridge and is designed to build team work among a group of 4-6 employees.  Teams are given one hour to re-establish power to the ship, stock a cargo pod, then navigate the pod to stranded crew members.

TODO: Wideangle image of room

## Introduction
When the lights in the room are turned on, the primary Raspberry Pi detects a change in light levels and begins a 60-minute timer.  An introduction video clip is played to welcome players to the escape room and outline the objectives.  Following the end of the introduction video, the primary monitor transitions to the Light Puzzle and the auxilary monitor transitions to the Morse Code puzzle.

## Puzzle 1: Morse Code
The auxilary monitor displays a password prompt.  The player can provide two inputs: a dot and a dash by pressing the corresponding labelled concave buttons.  The correct password is acquired by solving puzzles elsewhere in the room.  Entering the correct password unlocks the screen to provide information needed to access other puzzles in the room.

TODO: 20-30 demo video

## Puzzle 2: Light Puzzle
The main monitor displays a one-hour countdown timer and the status of the power in the command bridge.  Power status is represented by four disabled power icons.  Four colored LED strips visually connect the main monitor to other puzzles in the room.  When a light puzzle is solved, the corresponding LED strip transistions from blinking erratically to smoothly pulsing, and the icon on the screen updates to show power is enabled.  Once all four light puzzles are solved, a cutscene video is played, and then the next puzzle begins.

TODO: 20-30 demo video

## Puzzle 3: Snake Game
The main monitor shows a Snake game where there are three sprites.  The sprites need to navigate around the 2D playing field to collect randomly appearing resources.  As resources are collected, the trail behind each sprite becomes longer.  If any sprite hits the tail of itself or another sprite, the tail is removed.  When the tail of a sprite gets long enough, an exit gate is presented for that sprite; entering this gate removes the sprite from the field.  Exiting all three sprites from the field constitutes completion of the Snake game.

The first sprite is controlled via the joystick.  The second sprite is controlled by four buttons.  In the 5- and 6-player room configurations, pairs of buttons are placed in two separate stations.  In the 4-player room, one player has access to all four buttons.  The third sprite is controlled using four stomp pads.  Two stations exist in the front of the room with two stomp pads each.

TODO: 20-30 second demo video

## Puzzle 4: Hyperspace Game
A cutscene is played showing the cargo pod exiting from the space ship, followed by entering a hyperspace tunnel.  The gameplay pulls inspiration from a boss battle in [Crash Bandicoot](https://youtu.be/Er0AzrrjrJI?t=14m47s).  The hyperspace tunnel consists of a long series of rings.  The hyperlane is primarily straight with occassional branches leading to shorter or longer paths to the finish point.  The auxilary monitor displays a map of the full maze that only one player can see.  Players must avoid hitting asteroids while travelling through the rings either by navigating the cargo pod around them or blowing them up with a laser.

TODO: 20-30 second demo video

## Credits
Upon completion of the hyperspace puzzle, a credit sequence is played.  Half the screen is used to list the puzzle contributors one-puzzle-at-a-time.  The other half shows images of the pod exiting hyperspace, landing on the planet, and the crew collecting supplies from the pod.  Finally a full-screen corporate logo is displayed.

## Conclusion
Upon completion of the hyperspace puzzle, a credit sequence is played.  Half the screen is used to list the puzzle contributors one-puzzle-at-a-time.  The other half shows still frames of the pod exiting hyperspace, landing on the planet, and the crew collecting supplies from the pod.  Finally a full-screen corporate logo is displayed.

TODO: 20-30 second demo video

# Dependencies

## Hardware
- Qty: 2, [Raspberry Pi 3](https://www.raspberrypi.org/products/raspberry-pi-3-model-b/), each one drives a monitor
	- Qty: 2, [SanDisk 32GB microSDHC Card Mobile Ultra Class 10](https://www.newegg.com/Product/Product.aspx?Item=9SIA12K0N93630), holds operating system and project files
	- Qty: 1, [MicroUSB 5V 2.5A power supply](https://www.newegg.com/Product/Product.aspx?Item=9SIA7PR5WA8871), used to power the Raspberry Pi connected to the auxilary monitor
	- Qty: 1, [MC33866 Motor Driver Shield](http://www.robotshop.com/en/mc33886-raspberry-pi-motor-driver-board-raspberry-pi.html), used to supply enough current to drive several strips of LEDs
		- Qty: 1, [2.1mm 12VDC 5A Power Supply](https://www.newegg.com/Product/Product.aspx?Item=9SIA27C6J20741), supply used to power both LEDs and main monitor Raspberry Pi
	- Qty: 1, [High-Precision AD/DA Expansion Board](http://www.robotshop.com/en/raspberry-pi-high-precision-ad-da-expansion-board.html), reads analog voltages from human load cells, also detects changes in room light levels to trigger start of 1-hour window
	- Qty: 1, [Prototyping Pi Board](http://www.robotshop.com/en/prototyping-pi-board-raspberry-pi.html), soldering shield to hold quick-disconnect headers for buttons and joystick
		- Qty: 4, [2x5 Pin Shrouded Header](), quick disconnect header.  2x for button pairs, 1x for joystick, 1x for UART connection between Rapsberry Pis
		- Qty: 2, [IDC 2x5 cable](www.robotshop.com/en/20cm-idc-2x5-cable.html), Cable used to mate with 2x5 header
- Qty: 1, [TODO TV](), primary monitor
	- Qty: 2, [6' HDMI Cable](https://www.newegg.com/Product/Product.aspx?Item=N82E16882021128), one for each monitor
	- Qty: 2, [HDMI-DVI adapter](https://www.newegg.com/Product/Product.aspx?Item=9SIAD4R5J10076), one for each monitor, as needed
	- Qty: 2, [HMDI-VGA adapter](https://www.newegg.com/Product/Product.aspx?Item=9SIA3521V29198), one for each monitor, as needed
- Qty: 1, [TODO Monitor](), auxilary monitor
- Qty: 1, [Arcade Joystick](https://www.sparkfun.com/products/9136), 4-axis bang-bang actuation with fire button
- Qty: 4, [Concave Button](https://www.sparkfun.com/products/9337), bang-bang actuation
- Qty: 1, [Z533 Logitech Sound System](https://www.logitech.com/en-us/product/z533-multimedia-speaker-system)
- Qty: 4, [5m 5050 SMD Supernight RGB LED strip](https://www.newegg.com/Product/Product.aspx?Item=9SIA3W31A14276)
- Qty: 4, [Human load cell](https://www.newegg.com/Product/Product.aspx?Item=9SIADMZ5Z97241), each cell contains two resistors in series, one is a fixed X (TODO) ohms, the other is a strain gauge that increases (TODO) by Y (TODO) ohms when 50 lbs is applied

## Software
- Raspberry Pi Operating System
	- [Noobs v2.4.4](https://www.raspberrypi.org/downloads/noobs/)
		- Burn operating system to the microSD card then insert into Raspberry Pi
	- Command: _sudo apt-get update_
		- Connect to the internet then enter command into a terminal shell
	- Command: _sudo apt-get upgrade_
- Git
	- Command: _sudo apt-get install git_
		- To allow download of the code repository
	- Command: _cd /home/pi/Documents/_
		- Parent folder where the project files will be stored
	- Command: _git config user.email "USERNAME@EMAIL.COM"_
		- Set the Git parameters for the current user and folder
	- Command: _git config user.name "USERNAME"_
	- Command: _git config credential.helper 'cache --timeout=900'_
		- 900 is the default number of seconds before a session times out and the Git username/password must be reentered to push code changes
	- Command: _git clone https://github.com/scottalmond/EscapeRoom.git_
		- Creates a new folder
- Wiring Library
	- Command: _sudo pip3 install wiringpi_
		- Used to read from and write to discrete inputs like buttons, joystick and LEDs
	- Start >> Preferences >> Raspberry Pi Configuration >> Interfaces
		- Set SPI to Enabled
		- Set I2C to Enabled
		- Set Serial to Enabled
		- Set Remote GPIO to Enabled
- Numpy
	- Command: 
- PyGame
	- Command: _sudo apt-get install python-pygame_
		- Used for 2D graphics
- [Pi3D](https://github.com/tipam/pi3d) ([FAQ](https://pi3d.github.io/html/FAQ.html))
	- Command: _sudo pip3 install pi3d_
		- Used for 3D graphics
	- Command: _sudo raspi-config_
		- To allow greater utilization of the GPU, a larger memory allocation is needed, refer to the [ReadMe](http://pi3d.github.io/html/ReadMe.html#setup-on-the-raspberry-pi) to set the allocation to 256 MB
- Sound
	- Command: _amixer cset numid=3 1_
		Change the audio to come out over the headphone jack [source](https://www.raspberrypi.org/documentation/configuration/audio-config.md)

# Connection Diagram

## Room



## Pinout

### Main Monitor


### Auxilary Monitor

# About


