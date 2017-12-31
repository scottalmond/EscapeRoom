# Overview

This document details the top level objectives, implementation, and interface details of the finale in order to facilitate effective communication among the Escape Room development team.

# Definitions

- Implementation: A design element that does not require multiple parties to concur to change

- Requirement: A design element that requires two or more parties to agree to enact a change

- [TIER 1]: These are fundamental stipulations that must be true when the finale is delivered

- [TIER 2]: Following an agile development process, these are strongly desired stipulations, or stipulations that are difficult to define precisely, that must be attempted to be met before changes are to be considered

- [TIER 3]: These are nice-to-have stipulations and may be de-scoped or modified as needed to meet the dictated schedule

- [Hardware]: These are elements that refer to the team building the physical set the players will interact with

- [Software]: These are virtual elements that exist on the computer

- [Management]: These are elements that affect multiple puzzles in the room or how the overall escape room is presented

# Requirements

## Room

- Requirement [TIER 1] [Software] [Management]: The finale shall follow a pre-scripted narrative.
	- Implementation [Software]: The Wall computer will play video with sound as dictated by the narrative.

Attempting to design reconfigurable puzzles that target a variable number of players has proven challenging.  To limit scope, a finite number of players was chosen.
- Requirement [TIER 1] [Software] [Management]: The finale shall be designed to be operated by five players.

- Implementation [TIER 2] [Software]: The goal of the finale shall be an immerse audio-visual experience that impresses players.
	- Implementation [Software]: Escape rooms are typically designed around the setting of graphic adventure puzzle video games common in the 1980's and into the 1990's.  Typically this is accomplished through the use of physical puzzles that require a subset of the team to solve.  However, this room is focused heavily on the team work aspect and instead requires the full team to coordinate to solve a series of interactive games.
	- Implementation [TIER 3] [Software]: Music will be played during the Snake game, Hyperspace game, and Credits sequences.
		- Requirement [TIER 2] [Software] [Management]: Finale sounds shall support the space-themed illusion of the room.
			- Implementation [TIER 3] [Software]: Instrumental music will be originally composed that fits the space-theme.  Music will be designed to serve as a background accompaniment to the main player action, as is done to set ambiance in Hollywood movies.
		- Requirement [TIER 2] [Software] [Management]: Music shall be played at a moderate volume.
			- Implementation [TIER 3] [Software]: Allow the Proctor computer to issue commands to adjust volume levels prior to and during room play-through.
			- Implementation [TIER 3] [Software]: The volume for music will be independent from the volume for sound effects.
		- Requirement [TIER 2] [Software] [Management]: After the Light Puzzle is completed, no other puzzles shall emit sounds that conflict with the finale.

- Requirement [TIER 1] [Software] [Management]: The goal of the finale shall be to encourage team work among the players.
	- Implementation [TIER 3] [Software]: The Snake game will be most easily beaten if the players coordinate so only one on-screen character completes the objective at a time (to minimize the risk of players running into one another) rather than all proceeding independently at the same time.
	- Implementation [TIER 3] [Software]: The Hyperspace game controls each control one dimension of the on-screen character's movement.  Multiple players need to coordinate their actions to achieve the desired outcome.  Players will be presented with asymmetric abilities and information: a limited number of players will be able to see the map to determine how best to reach the end goal; some obstacles like asteroid rubble must be avoided (one set of controls), while other obstacles like large asteroids cannot be avoided and must be destroyed with the laser (joystick in another station).

- Requirement [TIER 2] [Software] [Management] [Hardware]: The cameras, Proctor computer, Wall computer, and Helm computer shall all be connected together in such a way that near-real-time communication (latency shall be no greater than 100 ms) can occur between them, for example through Ethernet communication.

- Requirement [TIER 1] [Hardware] [Management]: The goal shall be to design the finale stations to be operated without hardware or electrical failures.  In the case of failures, an easily accessible recovery option shall be available to the proctor.
	- Implementation [TIER 2] [Hardware]: Electrical joints such as in joysticks and buttons will use heat shrink to strain relief the custom connections and reduce the risk of inadvertent electrical contact.
	- Implementation [TIER 3] [Hardware]: A manually-accessible power switch(es) shall be available for the Proctor, Wall and Helm computers, but not readily apparent to players.  This may take the form of a power strip that is only accessible from below a table or behind a wall.
	- Implementation [TIER 2] [Hardware]: A thematic shroud shall enclose the speakers to protect them from players and hide them from view without degrading audio output.

- Requirement [TIER 1] [Software] [Hardware] [Management]: The Wall, Helm and Proctor _computers_ shall be supplied with 120 VAC, 60 Hz power except in extenuating circumstances.
	- Implementation [TIER 3] [Software]: The computers are architected to return to a standby state after a completed play-through and wait for Proctor computer input.

- Requirement [TIER 1] [Software] [Hardware] [Management]: The Wall, Helm and Proctor _monitors_ shall be supplied with 120 VAC, 60 Hz power except in extenuating circumstances.

- Requirement [TIER 1] [Software] [Hardware] [Management]: The finale shall be resettable within 5 minutes by a single operator.  This supports a 15 minute total reset time for the room.
	- Requirement [TIER 2] [Software] [Management]: When power is applied, the Wall, Helm and Proctor computers shall boot to a standby state in no more than 5 minutes.

- Implementation [TIER 3] [Software]: The Proctor computer will act as MASTER to the SLAVE Wall computer.  The Wall computer will act as MASTER to the SLAVE Helm computer.
	- Changing the Helm computer state directly through a command from the Proctor computer could lead to an undefined state existing between the Wall and Helm computers.

- Requirement [TIER 2] [Software] [Management]: Following the completion of the Light Puzzle, Snake game, Hyperspace game, Credits, or any cut scenes, the Wall computer shall automatically progress to the next chapter and update the Helm computer state as dictated by the narrative.

- Requirement [TIER 2] [Software] [Management]: Following either a successful or failed attempt to play through the room, the total time taken shall be displayed on the Wall monitor until the end of the credits.

- Requirement [TIER 2] [Software] [Hardware] [Management]: The computers, players and proctor shall be laid out as shown in the following.

![Top Level Room Layout](https://raw.githubusercontent.com/scottalmond/EscapeRoom/master/resources/computer_layout.png)

## Light Puzzle

- Requirement [TIER 1] [Software] [Management]: Following a start command from the Proctor computer, the finale will begin the first chapter.

- Requirement [TIER 2] [Software] [Hardware] [Management]: The light puzzle shall provide no fewer than one and no more than four discrete signals at 3.3V/0V, and the corresponding discrete ground returns (a total of 8 wires), to the Wall computer to indicate the status of the puzzle component(s).

- Requirement [TIER 2] [Software] [Management]: The Proctor computer shall have the ability to override the state of some or all of the light puzzle components by sending a command to the Wall computer.

- Requirement [TIER 2] [Software] [Management]: When queried by the Proctor computer during the light puzzle, the Wall computer shall report the state of the four light puzzle components as each either solved or not.

- Requirement [TIER 1] [Software] [Management]: Once all light puzzle discreets have changed state, the light puzzle shall be considered finished.
	- Implementation [TIER 2] [Software]: The Wall computer will then automatically transition to the next chapter, such as a cut scene.

- Requirement [TIER 1] [Software] [Hardware] [Management]: A TV or monitor that accepts and displays visual input from a Raspberry Pi shall be installed on the wall.

- Implementation [TIER 2] [Software]: The Wall computer shall be configured to run at 1920x1080 60 Hz (16:9, DMT mode 82) resolution.

- Requirement [TIER 3] [Software] [Management]: A tutorial shall play after the completion of the light puzzle to convey the location and operation of the controls for the Snake and Hyperspace games.
	- Implementation [TIER 3] [Software]: The Wall monitor will display the state of all finale controls as inactive.  When players use the controls, the state will transition to active.  Once all controls have been activated, the chapter will be considered complete and will transition automatically to the next chapter such as the Snake game.
	
- Requirement [TIER 3] [Software] [Management]: The Wall monitor shall display static noise on screen during the light puzzle.

## Morse Code

- Requirement [TIER 2] [Software] [Management]: Once the light puzzle is solved, the Wall computer shall send a trigger signal to the Helm computer.  In response to this command, the Helm computer shall stop the Morse Code puzzle and proceed to a blank screen within 1 second in preparation for the map portion of the Hyperspace game.
	- Implementation [TIER 3] [Software]: The book state machine running in the Helm computer will cease updating the state and rendering graphics for the Morse code puzzle in response to the relevant Ethernet command from the wall or proctor computers.

- Requirement [TIER 2] [Software] [Hardware]: A monitor that accepts and displays visual input from a Raspberry Pi shall be installed in the Helm.
	- Implementation [TIER 2] [Hardware]: The monitor will be situated in the Helm such that two players or fewer can clearly see the screen.  This facilitates the design goal of asymmetric information presented to the players.
	- Implementation [TIER 3] [Hardware]: An HP L2045W monitor is the current design baseline.

- Requirement [TIER 2] [Software] [Hardware]: Two buttons shall be installed in the Helm adjacent to the monitor to represent 'dot' and 'dash' user inputs.  These buttons shall be electrically connected to the Helm computer so that the state of the buttons can be acquired.

- Implementation [TIER 2] [Hardware]: The 'dot' and 'dash' buttons will be situated such that a seated player can view the Helm monitor while pressing the buttons.

- Implementation [TIER 2] [Software]: The Helm computer shall be configured to run at 1680x1050 60 Hz (16:10, DMT mode 58) resolution.

## Snake Game

- Implementation [TIER 2] [Software]: Three snakes are shown on screen.  One is controlled by the joystick in the captain's chair.  One is controlled by the joystick in the Helm.  One is controlled by the two single-axis joysticks in the wing stations.  The corners of the screen provide visual user feedback of user inputs.

![Snake Game Mock Up](https://i.imgur.com/bh3N98u.jpg)

- Implementation [TIER 3] [Software]: The music for this section will be inspired by the following reference songs:
	- [Bejeweled 2 Soundtrack](https://www.youtube.com/watch?v=4GLkrW9kluo)
	- [End of Line - Daft Punk](https://www.youtube.com/watch?v=AHGvaQMClEo)
	- [Lost Years - Lightbringers](https://www.youtube.com/watch?v=k6jjoE5Qt_s)
	- [Heavy Light - Animusic](https://www.youtube.com/watch?v=DKUTYxJEB44)
	- [Area Music Loop - Tomorrowland](https://www.youtube.com/watch?v=wHiAnXroGbw)

- Requirement [TIER 1] [Software] [Management]: The Tutorial and Snake game shall be designed to be completed within 5 minutes, but allow for shorter or longer play times depending on player skill level.

- Requirement [TIER 2] [Software] [Hardware]: The following user inputs shall be installed in the following locations and be electrically connected to the Wall computer:
	- Four-direction joystick in the Helm.  This will represent up, down, left, and right commands from one seated player.  Each direction has a sense and return.  8 wires total.  These buttons serve as the 'blue' user input and the goal shall be to use this theme color when designing the mounting structure in the Helm.
	- A joystick that can be operated while a player is seated the captain's chair.  Each direction, plus fire, has two wires for sense plus return.  10 wires total.  This joystick serves as the 'red' user input and the goal shall be to use this theme color when designing the mounting structure in the captain's chair.
	- Two single-axis joysticks, one for each of the two wing stations.  One joystick represents left and right commands.  The other joystick represents up and down control.  The joysticks will contain motion limiters that prevent user inputs in the unused directions.  Each direction has a sense and return.  8 wires total for the two stations.  These controls represent the 'green' user input and the goal shall be to use this theme color when designing the wing stations.

- Implementation [TIER 3] [Software]: When one snake hits the tail of another snake, the damaged portion of the tail is deleted.  Once a snake has grown a long enough tail, the Snake will be eligible to exit through goal posts.  The Helm player with the Morse code inputs will need to enter the appropriate code to enable the goal posts for the Snake to exit through.  Navigating the correctly colored snake through the goal posts represents completion of one third of the puzzle.  Navigating all three Snakes through the goal posts represents completion of the game.  Specially-colored pellets will appear randomly on screen for the snakes to collect.  A snake that exits the edge of the screen will reappear on the opposing side of the screen in a wrap-around style.

- Implementation [TIER 2] [Software]: The Snake game shall be considered complete once all three snakes have exited through the goal posts.
	- Implementation [TIER 2] [Software]: The Wall computer will then proceed to the following chapter such as the Hyperspace game.

## Hyperspace Game

- Implementation [TIER 2] [Software]: The player character is a single cargo pod with thrusters and a laser.

- Implementation [TIER 3] [Software]: The Hyperspace game will start with a cut scene depicting the pod descending from the space craft and entering hyperspace.  This cut scene will only be played once during a normal Hyperspace game play-through, regardless of the number of player failures.

![Hyperspace Cut Scene](https://i.imgur.com/nDOovDA.jpg)

- Implementation [TIER 2] [Software]: The Hyperspace game will consist of a cargo pod navigating through a series of hyperspace rings.

![Hyperspace Game Mock Up](https://i.imgur.com/oHnaBpF.jpg)

- Implementation [TIER 2] [Software]: The Helm monitor will display a map of the hyperspace maze.

![Hyperspace Map Mock Up](https://raw.githubusercontent.com/scottalmond/EscapeRoom/master/resources/map_mockup_pencils.jpg)

- Implementation [TIER 3] [Software]: The music for this section will be inspired by the following reference songs:
	- [Bejeweled 2 Soundtrack](https://www.youtube.com/watch?v=4GLkrW9kluo)
	- [End of Line - Daft Punk](https://www.youtube.com/watch?v=AHGvaQMClEo)
	- [Lost Years - Lightbringers](https://www.youtube.com/watch?v=k6jjoE5Qt_s)
	- [Heavy Light - Animusic](https://www.youtube.com/watch?v=DKUTYxJEB44)
	- [Area Music Loop - Tomorrowland](https://www.youtube.com/watch?v=wHiAnXroGbw)

- Implementation [TIER 3] [Software]: Sound effects will be played in response to user inputs in the Hyperspace puzzle, for example thruster and laser-firing sounds.

- Requirement [TIER 1] [Software] [Management]: The Hyperspace Intro and Game shall be designed to be completed in no more than 10 minutes, but allow for shorter or longer play times depending on player skill level.

- Implementation [TIER 2] [Software]: Upon start of the Hyperspace game, the Wall monitor shall emit a trigger signal to the Helm computer to transition to the map display.

![Cargo Pod](https://i.imgur.com/5g2vbFS.png)

- Implementation [TIER 3] [Software]: The playing field consists of a branching hyperspace path filled with asteroid obstacles.  The map depicts the full Hyperspace maze.  The Hyperspace path is formed from a linear series of rings with occasional forks where players need to navigate to either the left or right side of the screen to select a branch.  These moving rings will appear to the players in a manner such as the following:
	- [Space Boss Battle - Crash Bandicoot](https://youtu.be/Er0AzrrjrJI?t=14m47s)
	- [Fiber Optical Loop - Beeple](https://www.youtube.com/watch?v=FUUw3zNTXH8)

![Hyperspace Ring](https://i.imgur.com/96dxxqV.png)

![Hyperspace Fork](https://i.imgur.com/cCaWGny.png)

- Implementation [TIER 3] [Software]: The baseline speed will replicate the [Crash Bandicoot](https://youtu.be/Er0AzrrjrJI?t=14m47s) envionment.  One ring (or branch node) will pass by the player every 2 seconds.
	- In a 10-minute average playthrough this will account for ~290 straight rings and ~10 branch nodes

- Implementation [TIER 3] [Software]: Nominally 60% of the rings will contain asteroids or other obstacles.

- Implementation [TIER 3] [Software]: The cargo pod will be presented with a fork in the hyperspace lane nominally every 40-60 seconds.

- Implementation [TIER 3] [Software]: The hyperspace lane will consist of straight sections broken up by rounded corners.  Not all corners will appear on the map. 70% of straight sections will consist of 2-3 ring stretches, while the rest of the straight sections will be 4-5 rings.

- Implementation [TIER 3] [Software]: The asteroids consist of three sizes: small, medium, and large.  The medium asteroid can either be shot with the laser or avoided by moving the pod out of a collision course.  The large asteroid has no room to maneuver around and must be shot with the laser.  The small asteroid (a debris cloud) cannot be shot with the laser and must be avoided.

![Medium Asteroid](https://i.imgur.com/qjFWaUX.png)

- Implementation [TIER 3] [Software]: The joystick in the captain's chair controls the laser cross hairs.  When the fire button is pressed, a laser fires.  If the laser hits a medium or large asteroid the asteroid will be destroyed.  Targeting a small asteroid debris field with the laser does nothing.

- Implementation [TIER 3] [Software]: The up-down and left-right joysticks in the wing stations control the location of the pod within the playing field.

- Implementation [TIER 3] [Software]: The four-direction joystick in the Helm controls the attitude of the camera viewing the pod.  If the camera attitude is not changed after rounding Hyperspace corners, players will be unable to see and respond to upcoming obstacles.

- Implementation [TIER 3] [Software]: Hitting an asteroid degrades player health in three stages.  On the first hit, the edges of the Wall monitor screen glow red then fade.  On the second hit, the edge of the screen turns and remains red; the Helm monitor replaces the map with static.  The third hit triggers player death.  Upon player death the pod is reverted back to the start of the hyperspace map and briefly flashes to indicate a new life.  On a new life the Helm computer is reverted back to a map display.
	- Implementation [TIER 3] [Software]: Upon the player returning to the starting point, the map will revert to the initial conditions.  This includes asteroid placement and obstacle pods that move during play.

- Implementation [TIER 3] [Software]: If the game proves too easy, the pod will travel through hyperspace faster (~20%) when near the goal.

- Implementation [TIER 3] [Software]: If the game proves too difficult, the pod will trigger checkpoints during play and will restart from these points, rather than the start, upon player death.

### Hyperspace Background

Several stress tests were run to determine the most suitable method for generating a moving hyperspace background.  The default method of using an EnvironmentSphere in Pi3D proved to be a notable frame rate limiter (~15 FPS) when rendered together with foreground objects (vs 25 FPS when background rendering was excluded from the baseline) and only provided a short loop of a few seconds (the background texture was slid along the sphere to simulate motion).

Sliding a texture along the inside of an EnvironmentSphere appears very similar to a polar image projection.  However, using two methods (one with, and one without, Open Computer Vision 2 in Python 3) to polar project a sizable image, the frame rate did not exceed 5 FPS.

The only other option appears to be to use a looping pre-rendered background video, and reposition it on the screen in response to player motions to simulate changes in the direction of view.  Using this technique improved the frame rate to the point the foreground object rending was the limiting factor (~25 FPS).

- Implementation [TIER 3] [Software]: The background will consist of a ~60 second looping video (in a 10 minute average play through, the video will loop 10 times).  This video will depict a hyperspace effect emanating from the center to simulate motion of the pod moving foward.

- Implementation [TIER 3] [Software]: The Background will be built up using the following steps in pre-production:
	- Generating a large rectangular hyperspace background that tessellates with itself
	- Polar projecting the image such that the focal point is in the middle of the canvas
	- Creating video frames by sliding the image offset in the polar projection
	- Stiching the frames together produces a video with a moving star field moving from the center of the canvas to the edges

A mock up was coded to aid in determining nominal rates for background motion.  The demo ran at 17 FPS and cycled through a looping background image every 40 frames.  The background image was 1,300 pixels in the direction of motion.  Using this baseline yields a rate of motion of 560 pixels/second.  The max dimension of a Photoshop drawing is 30,000 pixels on a side [source](https://helpx.adobe.com/photoshop-elements/kb/maximum-image-size-limits-photoshop.html).  Imagining a mural that was 30,000 pixels in the long axis and was moved at 560 pixels/second along a polar transform would produce a 53 second video.

- Implementation [TIER 3] [Software]: Using a direct approach, a long (30,000 pixel) hyperspace mural could be composed as shown below.  In pre-processing, sections of the mural would be extracted, subjected to a polar transform, and then cropped to the screen resolution to form each frame.  Using a 1,920 x 1,080 pixel resolution as the baseline, the radius of the polar transform would be 1,100 pixels, which would be the length of the window moving along the mural (gray, light green, light blue). Assuming a design goal of a 1:1 pixel resolution match between the mural height and the polar projection image circumference (light blue), then the height of the mural would be 6,900 pixels.

![Hyperspace Background Frame Synthesis](https://raw.githubusercontent.com/scottalmond/EscapeRoom/master/resources/hyperspace_frame_synthesis.png)

- Implementation [TIER 3] [Software]: Designing to a 30,000 x 6,900 pixel mural may pose processing limitations in Photoshop.  One design redution that may be pursued is to divide the mural into an even number of segments and repeat those segments.  To avoid clear repetition, the small murals may be desgiend to fit together only when shifted.  This produces a pattern that should be more difficult to discern since the repeated portions will appear to the player to occur on different locations on the screen during play.  The example below shows what such a technique may look like if the long mural were broken into 6 small murals.

![Hyperspace Background Tessellation](https://raw.githubusercontent.com/scottalmond/EscapeRoom/master/resources/hyperspace_mural_length.png)

- Implementation [TIER 3] [Software]: One player will have control over the camera.  This navigator will be able to adjust the pitch and yaw within limits.  This player will naturally try to keep the camera pointed at the center so the other players can most clearly see up coming obstacles and address them.  When rounding corners, the camera will remain pointed in the previous direction, so the navigator will need to adjust the direction of view.
	- Implementation [TIER 3] [Software]: To achieve this simulated yaw and pitch of the camera, the foreground 3D assets will be rendered from the new view point, and the background video will be shifted on screen.

For example, if the cargo pod (green) were to the left of the center of the playing field, and if the navigator pointed the camera dead center, the players would be presented with a view like the following.  The light blue hyperspace rings follow a hyperspace lane that arcs to the right and down.
	
![Hyperspace Demo View Straight](https://raw.githubusercontent.com/scottalmond/EscapeRoom/master/resources/hyperspace_background_demo1.png)

If the navigator pushed the control stick left to view to the left of the pod, the background would be shifted right, and the rings would be drawn from the right side:
	
![Hyperspace Demo View Left](https://raw.githubusercontent.com/scottalmond/EscapeRoom/master/resources/hyperspace_background_demo2.png)

If the navigator pushed the control stick up and right (to look down right), the background would move up and left; the rings would be rendered from the left side.

![Hyperspace Demo View Right Down](https://raw.githubusercontent.com/scottalmond/EscapeRoom/master/resources/hyperspace_background_demo3.png)

- Implementation [TIER 3] [Software]: To accomplish this simulated background motion requires a video that is larger than the screen.  In testing, a 2x by 2x upscale worked well since the center of the video (focal point of the hyperspace tunnel) appeared directly on the edge of the screen.  Limiting the navigator field of view to this limit would help ensure that players still see at least one ring approaching even when the view port is very much askew.
	- Implementation [TIER 3] [Software]: This upscale could be accomplished by neglecting the 1:1 aspect ratio design goal for elements outside the center of the video (which will be moving past the players faster than the center portion), and by using a longer window when creating frames from the mural (1,550 pixels long rather than 1,100 pixels)

![Hyperspace Background Demo Video](https://raw.githubusercontent.com/scottalmond/EscapeRoom/master/resources/hyperspace_background_demo4.png)

### Hyperspace Map

- Implementation [TIER 3] [Software]: The Hyperspace map will be laid out like a subway map with thick monochromatic lines mapped to a rectilinear coordinate system representing the Hyperspace lanes.

- Implementation [TIER 3] [Software]: The start and end points are represented by squares.  The character is represented by a triangle that moves as the pod progresses through the map.

- Implementation [TIER 3] [Software]: Branch nodes are represented by circles.  The left branch node is represented by a brief blue strip down the center of the lane line.  The right branch node will have an orange line down the center.  The color code lines up with the branch Hyperspace ring on the screen which will have a faint inner glow of blue for the left branch and a faint inner glow of orange for the right path.

- Implementation [TIER 3] [Software]: The navigator will only have a view of the map and will be responsible for conveying to the team which branches to take.  The rest of the team will have access to the pod controls and will be responsible for navigating the pod around obstacles and toward the proper branches.

- Implementation [TIER 3] [Software]: Non-playable pods, that act as obstacles moving against the flow, are represented by upside down triangles that appear out of instant-death nodes and disappear into instant-death nodes.  These pods will appear on the main monitor as pods moving in the opposite direction to the player, risking a head-on collision.

To address questions and coding considerations about how NPC pods will get around large obstacles, there won't be any.  This is thematically appropriate for paths that may see more hyperspace traffic.
- Implementation [TIER 3] [Software]: In sections of the map that will have non-playable pods traveling along them, no large asteroids will appear.

- Implementation [TIER 3] [Software]: Wormholes are represented by a termination of a Hyperspace line with a 'T'.  When entering a 'T', the pod will be transported to the 'T' of the same color with a triangle pointing to it.  There may be multiple entry wormhole entrances, but only one exit wormhole.

- Implementation [TIER 3] [Software]: Dead ends are represented by instant death nodes.  On the map these appear as 'X's.  When approaching an instant death node the Wall monitor will display *TBD* to indicate player death.  During play testing a "Pod Destroyed" message will appear briefly on screen before returning the player to the start point.

- Implementation [TIER 3] [Software]: A short cut will be available for players who recognize the wormhole dynamic and also surmise that it is possible to travel backward along the same stretch of map.  Using a series of nodes connected in a circle it is possible for the pod to travel down a Hyperspace lane in the opposite direction and access lanes otherwise not accessible.

- Implementation [TIER 3] [Software]: An infinite loop will be available for players to travel down.  Entering the same wormhole multiple times does not change the outcome. This map element also serves as map clutter to obfuscate a clear path to the finish.

- Implementation [TIER 3] [Software]: There is the opportunity to add background elements to the map.  In typical subway maps these typically flag large bodies of water or rivers.  In a Hyperspace map this may be more thematically represented by rectilinear galaxies.

## Proctor Computer

- Requirement [TIER 1] [Software] [Management]: The Proctor computer shall emit signal(s) over Ethernet to prompt the Wall and Helm computers out of idle standby and begin the countdown timer.

- Requirement [TIER 1] [Software] [Management]: The time to complete the room shall be adjustable and have a nominal value of 65 minutes.

- Requirement [TIER 2] [Software] [Management]: The Proctor computer shall have the capability to change the remaining time to complete the room.

- Requirement [TIER 2] [Software] [Management]: The Proctor computer shall have the capability to manually advance from one puzzle to the next in the narrative.

- Requirement [TIER 1] [Hardware] [Management]: The Proctor computer shall be able to determine the status of the active puzzles.
	- Requirement [TIER 2] [Software] [Hardware] [Management]: The Proctor computer shall have the ability to view the players within the room.
		- Requirement [TIER 2] [Software] [Management]: The Proctor computer shall receive and display no fewer than one snapshot of the room at no less than once per second.
	- Requirement [TIER 2] [Software] [Management]: When queried by the Proctor computer, the Wall computer shall respond with the current state of the finale.
		- Implementation [TIER 2] [Software]: Allow the state of the finale computers to be queried and configured through an Ethernet connection.  The computers will be organized as a two-tiered state machine with a top level 'book' controlling the narrative sequence of 'chapters'.  Each chapter is a game, puzzle, video sequence, or blank screen.

- Requirement [TIER 2] [Hardware] [Management]: The Proctor shall have the capability to broadcast verbal hints to players without using the finale speakers.

## Credits

- Implementation [TIER 2] [Software]: The credits sequence will be implemented as a slide show.  Following a successful room completion in under 60 minutes, half the screen will display credits for the puzzle builders, artists and support staff.  The other half of the screen will display original stationary artworks of the pod exiting hyperspace, entering a planet's atmosphere, descending under parachute, landing on the surface, and astronauts removing supplies from the pod.  If the room is not completed in under 60 minutes, the artwork will be replaced with detailed pictures of the puzzles to highlight the assembly and design work.

- Implementation [TIER 3] [Software]: The music for this section will be inspired by the following reference songs:
	- [Firewatch - Camp Approach](https://www.youtube.com/watch?v=US-Eqtr3x08)
	- [Incredible Machine 3 - Unplugged](https://www.youtube.com/watch?v=WToAEdHbH7A)

- Requirement [TIER 2] [Software] [Management]: The total time taken to solve the game shall be displayed on screen during the credits sequence.

- Requirement [TIER 1] [Software] [Management]: The Wall computer shall play a pre-scripted credits sequence for no longer than 60 seconds following the completion of the Hyperspace puzzle.

- Implementation [TIER 2] [Software]: Following the credits sequence, a brief cut scene showing the corporate logo will play.

# Detailed Implementation

## Connection Diagram

![Connection Diagram](https://raw.githubusercontent.com/scottalmond/EscapeRoom/master/resources/system_layout.png)

## Wall Computer

- Requirement [TIER 2] [Software] [Management]: The Wall computer shall automatically proceed through these chapters in the listed order as players play the finale.  The chapters shall also also be manually progressed through when the Proctor computer send commands to the Wall computer.
	- Idle Standby: The monitor will display a black screen and emit no sound.  This chapter will complete when the Wall computer is sent a 'start' command from the Proctor computer
	- Light puzzle: Display static on the Wall monitor.  Report the status of the light puzzle components to the Proctor computer.
	- Controls Tutorial: An on-screen prompt on the Wall monitor will display the status of all the finale user inputs.  Actuating all user inputs at least once constitutes completion of this chapter.
	- Snake: A 5-person video game where 1-2 players each control an on-screen character.  The game is complete when all snakes are long enough and have exited the playing field.
	- Hyperspace: A 5-person video game where players work together to navigate a cargo pod through hyperspace, while avoiding and blasting obstacles.  Reaching the end of the hyperspace maze constitutes completion of the game.
	- Credits: A pre-scripted sequence highlighing the efforts of the escape room development team.
	- Corporate logo cut scene: The corporate logo animation will play for a few seconds.
- Unaccessible Chapters: the following chapters will exist and can only be reached via commands from the Proctor computer.
	- Debug: Display the state of user inputs to aid in troubleshooting.
	- Pause: Hold count down timer, display a pause icon on the screen.
- Implementation: Pinout

![Raspberry Pi 3 Pinout](https://i.pinimg.com/originals/84/46/ec/8446eca5728ebbfa85882e8e16af8507.png)

**TODO UPDATE**

![Project Box Pinout](https://raw.githubusercontent.com/scottalmond/EscapeRoom/master/resources/project_box_pinout.png)

### Helm Computer

- Requirement [TIER 2] [Software] [Management]: The Helm computer shall have references to the following chapters but will only enter/exit chapters in response to external (Wall computer) commanding
	- Idle Standby: The monitor will display a black screen.
	- Morse Code: The puzzle will accept user input via 'dot' and 'dash' buttons and display information on the screen when the proper passcode is entered.
	- Snake Game Standby: The monitor will display a series of Morse code sequences that need to be entered to activate the goal posts for the snakes to exit through.
	- Map: The monitor will display the hyperspace map and the location of the cargo pod.
	- Credits Standby: The monitor will display a black screen.
- Unaccessible Chapters: the following chapters will exist and can only be reached through Proctor computer commands
	- Debug: Display the state of user inputs to aid in troubleshooting.
	- Pause: Hold count down timer, display a pause icon on the screen.
- Implementation: Pinout

**TODO CREATE**

## State Flow Diagram

The Proctor computer is treated as MASTER to the SLAVE Wall computer.  The Wall computer is treated as MASTER to the SLAVE Helm computer.

- Implementation [TIER 3] [Software]: The following is a state transition diagram that will have nominally-identical copies running on both the Wall and Helm computers.
- Book
	- **Boot:** The Raspberry Pi will perform a Linux boot sequence followed by execution of the main Python program
	- **Create All Chapters:** The object-oriented chapters are created, but not executed here.   Execution of time-intensive processes such as loading video codecs and 3D graphics will also occur here.  Following Chapter creation, the chapter's clean method will be called to configure the chapter constants to default values.
	- **Start TCP:** A separate thread is launched to listen for TCP commands from the Proctor computer.  The TCP Listener is created after the constants have been defined to avoid the potential for the proctor to access constants before they exist.
	- **Next Chapter Exists:** Fetches the next chapter queued in the book state space.  For example if the current puzzle is "Snake", the next chapter will be "Hyperspace".
	- **Queue Chapter:** If the computer this code is running in is the Wall (MASTER), then the "next chapter" is immediately defined.
		- For example in the Wall computer, if the upcoming chapter is "Hyperspace" the queued chapter will be "Credits".  Queuing the following chapter immediately upon entering the current chapter allows the proctor to configure the next chapter at any time.  For example, the proctor could set "Snake" as the next chapter while "Hyperspace" is running.  Following a "next chapter" command by a "chapter done" command will transition the state machine to that commanded chapter.
		- If the computer is the Helm, the next chapter is not updated.  The Helm is run as a SLAVE to the Wall.
	- **Enter Chapter:** After fetching the chapter to run, a chapter configuration sequence is run.
	- **Is alive?** If the Proctor computer has sent a "dispose" command, the is_alive state will be False, prompting the Wall computer to send a command to the Helm to die, followed by disposing of the Wall's own chapters and book.  This ensures a clean exit to the desktop when commanded by the proctor.
	- **Update Chapter:** The Book calls the Chapter update loop at nominally 30 Hz.  This loop updates the Chapter state machine and renders graphics on the screen.
- TCP Listener
	- **Is alive, TCP Command Received?** The TCP listener listens for new commands in an infinite loop at nominally 30 Hz.
	- **Is Book Command?** If the Proctor command is formatted as a book command, it is processed.  This includes the "dispose" command which will stop both the TCP Listener and the Book threads.  "set next chapter" is another book command that the proctor can send.
	- **Is Chapter Command?** If the Proctor command is formated as a chapter command, it is processed.  This includes the "done" command which stops the execution of the current chapter and prompts the Book state machine to proceed to the next chapter.
- Chapter
	- **Enter Chapter:** Every time the chapter is run, the first method call is a dedicated initialization sequence.  For the Wall computer, an important step here is to send the TCP commands to ensure the Helm is in the proper state.
	- **Update Chapter:** Some chapters like Hyperspace or the Light Puzzle need to stop operations if the 60 minute window expires.  This update step checks whether the 60 minutes has expired and if so, exits the chapter.  Other chapters like the Credits will always play, so this check is ignored.  The game state is incremented and a graphical frame is displayed.
	- **Clean:** This method will always be called prior to exiting any chapter.  Configuring the constants on exit in preparation for the next run, rather than on initialization immediately before running chapter, allows the proctor time to configure constants while running other puzzles.  This ensures a clean entry into the chapter in whatever state the proctor desires.  This avoids the design limitation of requiring the proctor to change the chapter state only after entering the puzzle, which may break the illusion for players as graphics and game state rapidly change on screen.  This clean step is also where resource deallocations will occur such as stopping playback of video.

![State Transition Diagram](https://raw.githubusercontent.com/scottalmond/EscapeRoom/master/resources/state_transition_diagram.png)

# Schedule

- Requirement [TIER 1] [Software] [Management]: The software development shall be "95% complete" by mid-March to facilitate an end-to-end play-through of the room.
	- Implementation [TIER 2] [Software]: The following list of tasks shows the planned date of completion of significant code elements.  A functional build entails displaying relevant content on the monitors in response to user and proctor inputs.

- Dec 18, 2017 Architecture Plan
- Dec 31, 2017 Functional Architecture, IO Handler, Core
- Jan 2, 2018 Hand-off to Morse Code puzzle developer
- Jan 8, 2018 Video Functional Build
- Feb 5, 2018 Hyperspace Functional Build
- Feb 19, 2018 Snake Functional Build
- Feb 26, 2018 Credits Functional Build
- Mar 12, 2018 Integration with Morse Code

