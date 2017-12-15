# Overview

This document details the top level objectives and implementation details of the finale in order to facilitate effective communication among the Escape Room development team.

# Details

## Room

- Requirement: The finale shall follow the narrative
	- Derived Requirement: The wall computer shall play video with sound as dictated by the narrative

- Requirement: The goal of the finale shall be an immersive audio-visual experience that impresses players
	- Implementation: Music will be played during the Snake game, Hyperspace game, and Credits sequence
		- Derived Requirement: Music shall not break the space-themed illusion of the room
			- Implementation: Music will be originally composed that fits the space-theme
		- Derived Requirement: Music shall not be be too loud
			- Implementation: Allow the proctor to adjust volume levels prior to room playthrough
		- Derived Requirement: No other puzzles shall emit sound during the finale
	- Implementation: Sound effects shall be played in response to user inputs in the Hyperspace puzzle, for example thruster and laser-firing sounds

- Requirement: The goal of the finale shall be to encourage team work among the players
	- Implementation: The Snake game will be most easily beaten if the players coordinate so only one onscreen character completes the objective at a time rather than all proceeding at once
	- Implementation: The Hyperspace game controls act as an Ouija board where multiple players need to coordinate their actions to achieve the desired outcome.  Additionally, players will be presented with asymmetric controls and information: a limited number of players will be able to see the map to determine how best to reach the end goal; some obstacles like asteroid rubble must be avoided, while other obstacles like large asteroids cannot be avoided and must be destroyed with the laser

- Requirement: The cameras, proctor computer, wall computer, and console computer shall be all connected together in such a way that near-real-time communication can occur between them, for example through Ethernet communication.

## Light Puzzle

- Requirement: The wall monitor shall display the remaining time to solve the room

- Requirement: The wall monitor shall display the state of the four light puzzle components as each either solved or not

- Requirement: The wall monitor shall display a list of top level objectives for players to complete in order to solve the room
	- Implemention: This will take the form of three bullet points: establish power, stock cargo pod, deliver cargo pod

- Requirement: Once all four light puzzle discretes have changed state, the finale shall automatically advance to the next chapater in the narrative, such as a cut scene video

- Requirement: A monitor shall be installed on the wall that accepts and displays visual input from a Raspberry Pi

## Morse Code

- Requirement: Once the light puzzle is solved, the console computer shall proceed to a blank screen within 1 second in preparation for the map portion of the Hyperspace game
	- Implementation: The book state machine running in the console computer will cease updating the morse code puzzle state and rendering graphics in response to an Ethernet command from the wall or proctor computers

- Requirement: Two buttons shall be installed in the console to represent 'dot' and 'dash' user inputs.  These buttons shall be electrically connected to the console computer so that the state of the buttons can be acquired.

- Requirement: A monitor shall be installed in the console that accepts and displays visual input from a Raspberry Pi

## Snake Game

- Requirement: The Snake Game shall be designed to be completed within 5 minutes, but allow for shorter or longer play times depending on player skill level

- Requirement: The light puzzle shall provide four discrete signals at 3.3V/0V to indicate the status of the puzzle components

- Requirement: Once all three snakes have exited through the goal posts, the fianle shall automatically advance to the next chapter in the narrative, such as the Hyperspace game

- Requirement: The following user inputs shall be installed in the following locations and be electrically connected to either the console or the wall computer:
	- Four buttons in the console.  These buttons will represent up, down, left, and right commands from one seated player

## Hyperspace Game

- Requirement: The Hyperspace Game shall be designed to be completed within 10 minutes, but allow for shorter or longer play times depending on player skill level

- Requirement: Only one or two players can clearly see the map in the console

- Requirement: 

## Proctor

- Requirement: The proctor shall emit signal(s) over Ethernet to pull the wall and console computers out of sleep mode and begin the 60 minute coutdown timer

- Requirement: The proctor shall have the capability to change the remaining time to complete the room

- Requirement: The proctor shall have the capability to independnetly advance from one puzzle to the next

- Requirement: The proctor shall have the ability to view the status of the available puzzles
	- Derived Requirement: The proctor shall have the ability to view the players within the room
		- Derived Requirement: The proctor shall receive no fewer than one snapshot of the room at no less than once per second
	- Implementation: Allow the state of the finale computers to be queried and configured through an Ethernet connection.  The computers will be organized as a two-tiered state machine with a top level 'book' controlling the narrative sequence of 'chapters'.  Each chapter is a game, puzzle, video sequence, or blank screen.

- Requirement: The proctor shall have the ability to pause the countdown timer and puzzle progression
	- Implementation:

## Credits

- Requirement: The goal shall be to run and complete a pre-scripted credits sequence wihtin 60 seconds of the completion of the Hyperspace puzzle

- Requirement: When the puzzle is successfully completed in under 60 minutes, the total time taken to solve the game shall be displayed on screen during the credits sequence

- Implementation: The credits sequence 

## Implementation Details

### Computers

- Requirement: The computers shall be provided with uninterrupted wall power at all times.

- Requirement: When power is applied, computers will boot to a sleep state within 5 minutes

### Wall Computer

- Implementation: Wall book chapters
	- Sleep: The monitor shall display a black screen and emit no sound
	- Opening cut scene: In response to a proctor command, the wall computer will begin playing a cut scene
	- Light puzzle: 
	- Instructions cut scene: 
	- Snake:
	- Hyperspace:
	- Credits:
	- Corporate logo cut scene:
	- Blooper video: When the room is successfully completed in under 60 minutes, a bonus video will play after the credits, otherwise the 

### Console Computer

- Implementation: Console book chapters
	- Sleep: The monitor shall display a black screen
	- Morse Code: The puzzle will accept user input and display information when the proper code is entered
	- Standby: The monitor shall display a black screen
	- Map: The monitor shall display the hyperspace map and the location of the cargo pod
	- Standby: The monitor shall display a black screen

### 





pause considerations?





