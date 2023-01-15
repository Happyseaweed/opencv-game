# opencv-game
A ~~flappy bird style~~ "Don't touch the red stuff" game where you can play with your hands! Without touching the keyboard! Or your mouse! It is kind of hardware demanding at the moment, so be cautious
when you try it out. I will not be taking any responsibility for exploding laptops ;)

![Screenshot1](/media/screenshot1.png "Start Page")
![Screenshot2](/media/screenshot2.png "Gameplay")
![Screenshot3](/media/screenshot3.png "End Page")

## How to play
Make sure you have: pygame, opencv, mediapipe. To install these:
```
pip3 install pygame
```
For OpenCV: Visit the documentation for details on how to install: https://pypi.org/project/opencv-python/

For MacOS Silicon, install the sillicon version: https://github.com/google/mediapipe/issues/3277

For MacOS Intel, follow the documentation: https://google.github.io/mediapipe/getting_started/install.html

For Windows, follow the documentation: https://google.github.io/mediapipe/getting_started/install.html

Then, clone the repository and navigate to the folder and run:
```
python3 opencvGame.py
```
Launch the game. Make sure your camera is facing you or your hand. Close all 5 fingers together to flap.

## About
OpenCV, MediaPipe and Pygame are required to run this program, you can probably find how to download them on the internet.
Or, if you are already very cool, you probably have these libraries already installed.

This game appears to be very poorly optimized (as indicated by the horrendous frame rate when playing). I am still learning and searching for a solution to that problem.
This is also still a very early prototype. I will be adding more UI and sprites as I keep working.

The random obstacle generator can and should also be improved. Currently I am using a very simple function to do it, and it does not result in ideal obstacle positioning, but hey, it gets the idea down atleast.

Any advice would be appreciated :D

## Things to work on
1. A more efficient system for storing obstacles, possibly a linked list?
2. How to increase frame rate? I think mediapipe is pretty demanding at the moment.
3. Start/End screen

## Fluff
Please be advised, the code is also very poorly formatted and just be mindful of your own sanity as you read through my code :D
