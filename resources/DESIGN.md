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

- Requirement: The goal of the finale shall be to encourage team work among the players
	- Implementation: The Snake game will be most easily beaten if the players coordinate so only one onscreen character completes the objective at a time (to minimize the risk of players running into one another) rather than all proceeding independnetly at the same time
	- Implementation: The Hyperspace game controls act as an Ouija board where multiple players need to coordinate their actions to achieve the desired outcome.  Additionally, players will be presented with asymmetric controls and information: a limited number of players will be able to see the map to determine how best to reach the end goal; some obstacles like asteroid rubble must be avoided (one set of controls), while other obstacles like large asteroids cannot be avoided and must be destroyed with the laser (joystick in another station)

- Requirement: The cameras, proctor computer, wall computer, and console computer shall all be connected together in such a way that near-real-time communication (latency shall be no greater than 100 ms) can occur between them, for example through Ethernet communication.

- Requirement: Custom eletrical connections such as with the joystick and buttons will use heat shrink to strain relief the connections and reduce the risk of inadvertant eletrical contact

- Requirement: The wall, console and proctor computers shall be connected to uninterrupted wall power at all times.

- Requirement: The wall, console and proctor monitors shall be connected to uninterrupted wall power at all times.

- Requirement: When power is applied, the wall, console and proctor computers shall boot to a standby state in no longer than 5 minutes

- Implementation: The Wall PC will act as MASTER to the SLAVE Console.  The Proctor will act as MASTER to the SLAVE Wall.
	- Requirement: The Proctor shall not send commands to the Console.

## Light Puzzle

- Implementation: Mock up:
![Light Puzzle Mock Up](https://i.imgur.com/LKqFlft.jpg)

- Requirement: The wall monitor shall display the remaining time to solve the room during the light puzzle

- Requirement: The light puzzle shall provide four discrete signals at 3.3V/0V, and the corresponding discrete ground returns (a total of 8 wires), to the wall computer to indicate the status of the puzzle components

- Requirement: The wall monitor shall display the state of the four light puzzle components as each either solved or not

- Requirement: The wall monitor shall display a list of top level objectives for players to complete in order to solve the room
	- Implemention: This will take the form of three bullet points: establish power, stock cargo pod, deliver cargo pod

- Requirement: Once all four light puzzle discretes have changed state, the finale shall automatically advance to the next chapter in the narrative, such as a cut scene video

- Requirement: A monitor that accepts and displays visual input from a Raspberry Pi shall be installed on the wall

- Requirement: The wall computer shall be configured to run at TODO resolution

## Morse Code

- Requirement: Once the light puzzle is solved, the wall computer shall send a trigger signal to the console computer.  In response to this command, the console computer shall proceed to a blank screen within 1 second in preparation for the map portion of the Hyperspace game
	- Implementation: The book state machine running in the console computer will cease updating the morse code puzzle and rendering graphics in response to the relevant Ethernet command from the wall or proctor computers

- Requirement: A monitor that accepts and displays visual input from a Raspberry Pi shall be installed in the console 

- Requirement: Two buttons shall be installed in the console adjacent to the monitor to represent 'dot' and 'dash' user inputs.  These buttons shall be electrically connected to the console computer so that the state of the buttons can be acquired.

- Requirement: The console computer shall be configured to run at TODO resolution

## Snake Game

- Implementation: Three snakes are shown on screen.  One is controlled by the joystick in the captain's chair.  One is controlled by the four buttons in the console.  One is controlled by the four stomp pads.  The corners of the screen provide user feedback of user inputs
![Snake Game Mock Up](https://i.imgur.com/bh3N98u.jpg)

- Implementation: The music for this section will be inspired by the following reference songs:
	- [Epic Mountain - Quantum Computers](https://www.youtube.com/watch?v=hUsoHSa4QXI)
	- [Software Inc - Trailer](https://youtu.be/6M2jonWFHwQ?t=6s)
	- [Traktion - Mission ASCII](https://www.youtube.com/watch?v=mTbdaC3JsMc&feature=youtu.be&t=22s)

- Requirement: The wall monitor shall display the remaining time to solve the room during the Snake game

- Requirement: The Snake Game shall be designed to be completed within 5 minutes, but allow for shorter or longer play times depending on player skill level

- Requirement: Once all three snakes have exited through the goal posts, the fianle shall automatically advance to the next chapter in the narrative, such as the Hyperspace game

- Requirement: The following user inputs shall be installed in the following locations and be electrically connected to the wall computer:
	- Four buttons in the console.  These buttons will represent up, down, left, and right commands from one seated player.  Each button has a sense and return.  8 wires total.  These buttons serve as the 'blue' user input and the goal shall be to use this theme color when designing the mounting structure in the console
	- A joystick that can be operated while a player is seated the captain's chair.  Each direction, plus fire, has two wires for sesne plus return.  10 wires total.  This joystick serves as the 'red' user input and the goal shall be to use this theme color when designing the mounting structure in the captain's chair
	- Four stomp pads arranged as two pairs of two.  One pair of pads represents left and right commands.  The other pair represents up and down control.  The pads are designed to be operated by players while standing.  Each pad contains three wires: power, sense and return.  12 wires total.  These four pads represent the 'green' user input and the goal shall be to use theis theme color when designing the stomp pads.

- Implementation: When one snake hits the tail of another snake, the damanged portion of the tail is deleted.  Once a snake has grown a long enough tail, goal posts will appear at the bottom of the screen.  Navigating the correctly colored snake through the goal posts represents completion of one third of the puzzle.  Navigating all three Snakes through the goal posts represents completion of the game.  Specificly-colored pellets will appear randomly on screen for the snakes to collect.  A snake that exits the edge of the screen will reappear on the opposing side of the screen in a wrap-around style.

## Hyperspace Game

- Implementation: The Hyperspace game will start with a cutscene depicting the pod descending from the space craft and entering hyperspace.  This cut scene will only be played once.
![Hyperspace Cut Scene](https://i.imgur.com/nDOovDA.jpg)

- Implementation: The Hyperspace game will consist of a cargo pod navigating through a series of hyperspace rings
![Hyperspace Game Mock Up](https://i.imgur.com/oHnaBpF.jpg)

- Implementation: The console monitor will display a map of the hyperspace maze
![Hyperspace Map Mock Up](https://i.imgur.com/IudjHqh.jpg)

- Implementation: The music for this section will be inspired by the following reference songs:
	- [Zabutom - Final Blast](https://www.youtube.com/watch?v=uwlijEs81mI)
	- [Them's Fightin' Herds - Title Theme](https://www.youtube.com/watch?v=hHCtGhXCKYI)
	- [Riggsmeister - To The Future](https://youtu.be/JtFy3IusYY8?t=26s)

- Implementation: Sound effects will be played in response to user inputs in the Hyperspace puzzle, for example thruster and laser-firing sounds

- Requirement: The wall monitor shall display the remaining time to solve the room during the Hyperspace game

- Requirement: The Hyperspace Game shall be designed to be completed within 10 minutes, but allow for shorter or longer play times depending on player skill level

- Requirement: No more than two players shall clearly see the map in the console

- Requirement: Upon start of the Hyperspace game, the wall monitor shall emit a trigger signal to the console computer to transition to the map display

- Implementation: The player character is a single cargo pod with thrusers and a laser.
![Cargo Pod](https://i.imgur.com/5g2vbFS.png)

- Implementation: The playing field consists of a branching hyperspace path filled with asteroid obstacles.  The map depicts the full Hyperspace maze.  The Hyperspace path is indicated via linear series of rings and occasional forks where players need to navigate to either the left or right side of the screen to select a branch
![Hyperspace Ring](https://i.imgur.com/96dxxqV.png)
![Hyperspace Fork](https://i.imgur.com/cCaWGny.png)

- Implementation: The asteroids consist of three sizes: small, medium, and large.  The medium asteroid can either be shot with the laser or avoided by moving the pod out of a collision course.  The large asteroid has no room to maneuver around and must be shot with the laser.  The small asteroid (a debris cloud) cannot be shot with the laser and must be avoided.
![Medium Asteroid](https://i.imgur.com/qjFWaUX.png)

- Implementation: The four buttons in the console and four stomp pads act an Ouija board for controlling the position of the pod.  If only the only user input was the right button in the console, the pod would move at one-third speed to the right.  If the only user input were the right stomp pad, the pod would again move at one-thrid speed to the right.  When both the right pad and right button are activated syncronously, the pod moves at full speed to the right.  The logic for the remaining three cardinal directions act in the same combinational manner.
The joystick in the captain's chair controls the laser cross hairs.  When the fire button is pressed, a laser fires.  If the laser hits a medium or large asteroid the asteroid will be destroyed.  Targeting a small astroid debris field with the laser does nothing.

- Implementation: Hitting an asteroid triggers a player death.  The pod is reverted back to the start of the hyperspace map and briefly flashes to indicate a new life.

## Proctor

- Requirement: The proctor shall emit signal(s) over Ethernet to prompt the wall and console computers out of sleep mode and begin the 60 minute countdown timer

- Requirement: The proctor shall have the capability to change the remaining time to complete the room

- Requirement: The proctor shall have the capability to independently advance from one puzzle to the next

- Requirement: The proctor shall have the ability to view the status of the available puzzles
	- Derived Requirement: The proctor shall have the ability to view the players within the room
		- Derived Requirement: The proctor shall receive no fewer than one snapshot of the room at no less than once per second
	- Implementation: Allow the state of the finale computers to be queried and configured through an Ethernet connection.  The computers will be organized as a two-tiered state machine with a top level 'book' controlling the narrative sequence of 'chapters'.  Each chapter is a game, puzzle, video sequence, or blank screen.

- Requirement: The goal shall be to give the proctor the ability to pause and resume the countdown timer and puzzle progression manually

- Requirement: The proctor shall have the capability to broadcast hints to players without using the finale speakers

## Credits

- Implementation: The credits sequence will be implemented as a slide show.  Following a successful room completion in under 60 minutes, half the screen will display credits for the puzzle builders, artists and support staff.  The other half of the screen will display original static artworks of pod exiting hyperspace, entering a planet's atmosphere, descending under parachute, landing on the surface, and astronauts removing supplies from the pod.  If the room is not completed in under 60 minutes, the artowkr will be replaced with detailed pictures of the puzzles to highlight the assembly and design work.

- Implementation: The music for this section will be inspired by the following reference songs:
	- [Incredible Machine 3 - Unplugged](https://www.youtube.com/watch?v=WToAEdHbH7A)
	- [Firewatch - Camp Approach](https://www.youtube.com/watch?v=US-Eqtr3x08)

- Requirement: When the puzzle is successfully completed in under 60 minutes, the total time taken to solve the game shall be displayed on screen during the credits sequence

- Requirement: The wall computer shall automatically play a pre-scripted credits sequence for no longer than 60 seconds following the completion of the Hyperspace puzzle

- Implementation: Following the credits sequence, a brief cut scene showing the corporate logo will play.

- Implementation: If the room was successfully completed in under 60 minutes, a humerous blooper cut scene will play after the corporate logo as a reward to the players for successfully completing the room.

- Implementation: Following either the blooper reel in a successful room compeletion, or the corporate logo in a failed room playthrough, the wall monitor shall proceed to the sleep state

# Detailed Implementation

## Connection Diagram

![Connection Diagram](https://raw.githubusercontent.com/scottalmond/EscapeRoom/master/resources/system_layout.png)

## Wall Computer

- Implementation: Wall book chapters
	- Idle Standby: The monitor shall display a black screen and emit no sound
	- Opening cut scene: In response to a proctor command, the wall computer will begin playing a cut scene
	- Light puzzle: Display light puzzle component status change in response to discrete inputs.  Update countdown timer
	- Instructions cut scene: 
	- Snake:
	- Hyperspace:
	- Credits:
	- Corporate logo cut scene: The corporate logo animation will play for a few seconds
	- Blooper video: When the room is successfully completed in under 60 minutes, a bonus video will play after the credits, otherwise this chapter is skipped
- Implementation: Pinout

![Raspberry Pi 3 Pinout](https://i.pinimg.com/originals/84/46/ec/8446eca5728ebbfa85882e8e16af8507.png)

TODO

### Console Computer

- Implementation: Console book chapters
	- Idle Standby: The monitor shall display a black screen
	- Light Puzzle Standby: The monitor shall display a black screen
	- Morse Code: The puzzle will accept user input and display information when the proper code is entered
	- Snake Game Standby: The monitor shall display a black screen
	- Map: The monitor shall display the hyperspace map and the location of the cargo pod
	- Credits Standby: The monitor shall display a black screen
- Implementation: Pinout

TODO

## State Flowchart

The Wall computer is treated as a MASTER to the SLAVE Console.
The Proctor computer is treated as a MASTER to the SLAVE Wall.

The following is a state transition diagram that will live on both the Wall and Console computers.
- Book
	- **Boot:** A boot up sequence entails creating, but not running, the object-oriented chapters.
	- **Start TCP:** A separeate thread is launched to listen for TCP commands from the proctor console.  The TCP Listener is created after the constants have been defined to avoid the potential for the proctor to access constants before they exist
	- **Next Chapter Exists:** Fetches the next chapter queued in the book state space.  For example if the current puzzle is "Snake", the next chapter will be "Hyperspace".
	- **Queue Chapter:** If the PC this code is running in is the Wall (MASTER), then the "next chapter" is immediately defined.
		- For example in the Wal computer, if the upcoming chapter is "Hyperspace" the queued chapter will be "Credits".  Queuing the following chapter immediately upon entering the current chapter allows the proctor to configure the next chapter at any time.  For example, the proctor could set "Snake" as the next chapter while "Hyperspace" is running.  Following a "next chapter" command by a "chapter done" command will transition the state machine to that commanded chapter.
		- If the PC is the Console, the next chapter is not updated.  The Console is run as a SLAVE to the Wall.
	- **Enter Chapter:** After fetching the chapter to run, a chapter configuration sequence is run.
	- **Is alive?:** If the proctor has sent a "dispose" command, the is_alive state will be False, prompting the Wall PC to send a command to the Console to die, followed by disposing of the Wall's own chapters and book.  This ensures a clean exit to the desktop whan commanded by the proctor
	- **Update Chapter:** The Book calls the Chapter update loop at nominally 30 Hz.  This loop updates the Chapter state machine and renders graphics on the screen.
- TCP Listener
	- **Is alive, TCP Command Received?** The TCP listener listens for new commands in an infinite loop at nominally 30 Hz.
	- **Is Book Command?** If the proctor command is formatted as a book command, it is processed.  This includes the "dispose" command which will stop both the TCP Listener and the Book threads.  "set next chapter" is another book command that the proctor can send.
	- **Is Chapter Command?** If the proctor command is formmated as a chapter command, it is processed.  This includes the "done" command which stops the execution of the current chapter and prompts the Book state machine to proceed to the next chapter.
- Chapter
	- **Enter Chapter:** Every time the chapter is run, the first command is a special boot up sequnce.  

clean should be nearly idential to initialize.  used for shutting down autonomous processes cleanly like video players

![State Transition Diagram](https://raw.githubusercontent.com/scottalmond/EscapeRoom/master/resources/state_transition_diagram.png)

# Schedule

The following list of tasks shows the planned date of completion of significant code elements to acheive the mid-March "95% completion" deadline.  A functional build entails displaying relevant content on the monitors in response to user and proctor inputs to facilitate an end-to-end playthroguh of the room.

- Dec 18, 2017 Architecture Plan
- Dec 31, 2017 Functional Architecture, IO Handler, Core
- Jan 2, 2018 Handoff to Morse Code puzzle developer
- Jan 8, 2018 Video Functional Build
- Feb 5, 2018 Hyperspace Functional Build
- Feb 19, 2018 Snake Functional Build
- Feb 26, 2018 Credits Functional Build
- Mar 12, 2018 Integration with Morse Code



logic flow file/success criteria state diagram, focus on fail criteria trigger, hyperspace death
number of inputs, buttoms, stomp pads
look and feel of room, playthrough: goal posts in snake game, pod and rings in hyperspace
links to music samples

make housing for speakers to protect them
