# Overview

This document details the top level objectives, implementation, and interface details of the finale in order to facilitate effective communication among the Escape Room development team.

# Requirements

## Room

- Requirement: The finale shall follow a pre-scripted narrative
	- Derived Requirement: The wall computer shall play video with sound as dictated by the narrative

- Requirement: The goal of the finale shall be an immersive audio-visual experience that impresses players
	- Implementation: Music will be played during the Snake game, Hyperspace game, and Credits sequence
		- Derived Requirement: Music shall not break the space-themed illusion of the room
			- Implementation: Instrumental music will be originally composed that fits the space-theme.  Music will be designed to serve as a background accompanyment to the main player action, as is done to set ambience in Hollywood movies.
		- Derived Requirement: Music shall not be be too loud
			- Implementation: Allow the proctor to adjust volume levels prior to room playthrough
			- Implementation: The volume for music will be independent from the volume for sound effects
		- Derived Requirement: No other puzzles shall emit sound during the finale
	- Implementation: Sound effects shall be played in response to user inputs in the Hyperspace puzzle, for example thruster and laser-firing sounds

- Requirement: The goal of the finale shall be to encourage team work among the players
	- Implementation: The Snake game will be most easily beaten if the players coordinate so only one onscreen character completes the objective at a time (to minimize the risk of players running into one another) rather than all proceeding independnetly at the same time
	- Implementation: The Hyperspace game controls act as an Ouija board where multiple players need to coordinate their actions to achieve the desired outcome.  Additionally, players will be presented with asymmetric controls and information: a limited number of players will be able to see the map to determine how best to reach the end goal; some obstacles like asteroid rubble must be avoided (one set of controls), while other obstacles like large asteroids cannot be avoided and must be destroyed with the laser (joystick in another station)

- Requirement: The cameras, proctor computer, wall computer, and console computer shall all be connected together in such a way that near-real-time communication (latency shall be no greater than 100 ms) can occur between them, for example through Ethernet communication.

## Light Puzzle

- Implementation: Mock up: ![Light Puzzle Mock Up](https://imgur.com/LKqFlft)

- Requirement: The wall monitor shall display the remaining time to solve the room during the light puzzle

- Requirement: The light puzzle shall provide four discrete signals at 3.3V/0V, and the corresponding discrete ground returns (a total of 8 wires), to the wall computer to indicate the status of the puzzle components

- Requirement: The wall monitor shall display the state of the four light puzzle components as each either solved or not

- Requirement: The wall monitor shall display a list of top level objectives for players to complete in order to solve the room
	- Implemention: This will take the form of three bullet points: establish power, stock cargo pod, deliver cargo pod

- Requirement: Once all four light puzzle discretes have changed state, the finale shall automatically advance to the next chapter in the narrative, such as a cut scene video

- Requirement: A monitor that accepts and displays visual input from a Raspberry Pi shall be installed on the wall

## Morse Code

- Requirement: Once the light puzzle is solved, the wall computer will send a trigger signal to the console computer.  In response to this command, the console computer shall proceed to a blank screen within 1 second in preparation for the map portion of the Hyperspace game
	- Implementation: The book state machine running in the console computer will cease updating the morse code puzzle and rendering graphics in response to the relevant Ethernet command from the wall or proctor computers

- Requirement: A monitor that accepts and displays visual input from a Raspberry Pi shall be installed in the console 

- Requirement: Two buttons shall be installed in the console adjacent to the monitor to represent 'dot' and 'dash' user inputs.  These buttons shall be electrically connected to the console computer so that the state of the buttons can be acquired.

## Snake Game

- Requirement: The wall monitor shall display the remaining time to solve the room during the Snake game

- Requirement: The Snake Game shall be designed to be completed within 5 minutes, but allow for shorter or longer play times depending on player skill level

- Requirement: Once all three snakes have exited through the goal posts, the fianle shall automatically advance to the next chapter in the narrative, such as the Hyperspace game

- Requirement: The following user inputs shall be installed in the following locations and be electrically connected to the wall computer:
	- Four buttons in the console.  These buttons will represent up, down, left, and right commands from one seated player.  Each button has a sense and return.  8 wires total.
	- A joystick that can be operated while a player is seated the captain's chair.  Each direction, plus fire, has two wires for sesne plus return.  10 wires total.
	- Four stomp pads arranged as two pairs of two.  One pair of pads represents left and right commands.  The other pair represents up and down control.  The pads are designed to be operated by players while standing.  Each pad contains three wires: power, sense and return.  12 wires total.

- Implementation: 

## Hyperspace Game

- Requirement: The wall monitor shall display the remaining time to solve the room during the Hyperspace game

- Requirement: The Hyperspace Game shall be designed to be completed within 10 minutes, but allow for shorter or longer play times depending on player skill level

- Requirement: Only one or two players can clearly see the map in the console

- Requirement: Upon start of the Hyperspace game, the wall monitor shall emit a trigger signal to the console computer to transition to the map display

## Proctor

- Requirement: The proctor shall emit signal(s) over Ethernet to pull the wall and console computers out of sleep mode and begin the 60 minute coutdown timer

- Requirement: The proctor shall have the capability to change the remaining time to complete the room

- Requirement: The proctor shall have the capability to independently advance from one puzzle to the next

- Requirement: The proctor shall have the ability to view the status of the available puzzles
	- Derived Requirement: The proctor shall have the ability to view the players within the room
		- Derived Requirement: The proctor shall receive no fewer than one snapshot of the room at no less than once per second
	- Implementation: Allow the state of the finale computers to be queried and configured through an Ethernet connection.  The computers will be organized as a two-tiered state machine with a top level 'book' controlling the narrative sequence of 'chapters'.  Each chapter is a game, puzzle, video sequence, or blank screen.

- Requirement: One goal shall be to give the proctor the ability to pause and resume the countdown timer and puzzle progression manually

- Requirement: The proctor shall have the capability to broadcast hints to players without using the finale speakers

## Credits

- Requirement: When the puzzle is successfully completed in under 60 minutes, the total time taken to solve the game shall be displayed on screen during the credits sequence

- Requirement: The wall computer shall automatically play a pre-scripted credits sequence for no longer than 60 seconds following the completion of the Hyperspace puzzle

- Implementation: The credits sequence will be implemented as a slide show.  Following a successful room completion in under 60 minutes, half the screen will display credits for the puzzle builders, artists and support staff.  The other half of the screen will display original static artworks of pod exiting hyperspace, entering a planet's atmosphere, descending under parachute, landing on the surface, and astronauts removing supplies from the pod.  If the room is not completed in under 60 minutes, the artowkr will be replaced with detailed pictures of the puzzles to highlight the assembly and design work.

- Implementation: Following the credits sequence, a brief cut scene showing the corporate logo will play.

- Implementation: If the room was successfully completed in under 60 minutes, a humerous blooper cut scene will play after the corporate logo as a reward to the players for successfully completing the room.

- Implementation: Following either the blooper reel in a successful room compeletion, or the corporate logo in a failed room playthrough, the wall monitor shall proceed to the sleep state

# Implementation

## Computers

- Requirement: The computers shall be provided with uninterrupted wall power at all times.

- Requirement: When power is applied, computers will boot to a standby state within 5 minutes

## Connection Diagram



## Wall Computer

- Implementation: Wall book chapters
	- Standby: The monitor shall display a black screen and emit no sound
	- Opening cut scene: In response to a proctor command, the wall computer will begin playing a cut scene
	- Light puzzle: 
	- Instructions cut scene: 
	- Snake:
	- Hyperspace:
	- Credits:
	- Corporate logo cut scene:
	- Blooper video: When the room is successfully completed in under 60 minutes, a bonus video will play after the credits, otherwise the 
- Implementation: Pinout

### Console Computer

- Implementation: Console book chapters
	- Standby: The monitor shall display a black screen
	- Morse Code: The puzzle will accept user input and display information when the proper code is entered
	- Standby: The monitor shall display a black screen
	- Map: The monitor shall display the hyperspace map and the location of the cargo pod
	- Standby: The monitor shall display a black screen
- Implementation: Pinout

# Schedule

The following list of tasks shows the planned date of completion of significant code elements to acheive the mid-March "95% completion" deadline.  A functional build entails accepting user and proctor input and displaying relevant game state through the monitors.

12/18/17 Architecture Plan
12/31/17 Functional Architecture, IO Handler, Core
1/2/17 Handoff to Morse Code puzzle developer
1/8/17 Video Functional Build
2/5/17 Hyperspace Functional Build
2/19/17 Snake Functional Build
2/26/17 Credits Functional Build
3/12/17 Integration with Morse Code



logic flow file/success criteria state diagram, focus on fail criteria trigger
heat shrink connections
number of inputs, buttoms, stomp pads
look and feel of room, playthrough: goal posts in snake game, pod and rings in hyperspace
links to music samples