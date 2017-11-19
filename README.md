<b>Overview</b>

This project contains four interactive puzzles which form a portion of an escape room.
<a href="https://en.wikipedia.org/wiki/Escape_room">Wikipedia: Escape Room</a>
TODO: video of deployed build

<b>Details</b>

<u>Room</u>
The escape room is themed after a Star Trek command bridge and is designed to build team work among a team of 4-6 employees.  Teams are given one hour to re-establish power to the ship, stock a cargo pod, then navigate the pod to stranded crew members.

<u>Puzzle 1: Morse Code</u>
The auxilary monitor displays a password prompt.  The player can provide two inputs: a dot and a dash by pressing labelled concave buttons.  The password is acquired by solving puzzles elsewhere in the room.  Entering the correct password unlocks the screen to provide information needed to access other puzzles in the room.

<u>Puzzle 2: Light Puzzle Splash Screen</u>
The main monitor displays a 1-hour countdown timer and the status of the power in the command bridge.  Power status is represented by four disabled power icons.  Four colored LED strips connect the main monitor to puzzles in other areas of the room.  When a light puzzle is solved, the corresponding LED strip transistions from blinking erratically to smoothly pulsing, and the icon on the screen updates to show power is enabled.  Once all four light puzzles are solved, a cutscene video is played, and then Puzzle 3 begins.

<u>Puzzle 3: Snake Game</u>
The main monitor shows a Snake game where there are three sprites.  The sprites need to navigate around the 2D playing field to collect randomly appearing resources.  As resources are collected, the trail behind each sprite becomes longer.  If any sprite hits the tail of itself or another sprite, the tail is removed.  When the tail of a sprite gets long enough, an exit gate is presented for that sprite; entering this gate removes the sprite from the field.  Exiting all three sprites from the field constitutes completion of the Snake game.

The first sprite is controlled via the joystick.  The second sprite is controlled by four buttons.  In the 5- and 6-player room configurations, pairs of buttons are placed in two separate stations.  In the 4-player room, one player has access to all four buttons.  The third sprite is controlled using four stomp pads.  Two stations exist in the front of the room with two stomp pads each.

<u>Puzzle 4: Hyperspace Game</u>
A cutscene is played showing the cargo pod exiting from the space ship, follwed by entering a hyperspace tunnel.  


<b>Dependencies</b>

The following resources were used in this project.

<u>Hardware</u>
* Qty: 2, <a href="https://www.raspberrypi.org/products/raspberry-pi-3-model-b/">Raspberry Pi 3</a>, each drives one monitor
	* Qty: 2, <a href="https://www.newegg.com/Product/Product.aspx?Item=9SIA12K0N93630">SanDisk 32GB microSD microSDHC Card Mobile Ultra Class 10 with USB Card Reader</a>, holds operating system and project files
	* Qty: 1, <a href=""><a/>
	* Qty: 1, <a href=""><a/>
* Qty: 1, <a href="https://www.sparkfun.com/products/9136">Arcade Joystick</a>, 4-axis bang-bang control with fire button
* Qty: 4, <a href="https://www.sparkfun.com/products/9337">Button</a>, bang-bang control

<u>Software</u>
OS: Noobs v2.4.4
Pi3D: 
ADC:



<b>Connection Diagram</b>



<b>About</b>


