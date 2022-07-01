import cv2 as cv
import mediapipe as mp
import pygame
import math
import time
import random

# Pygame Declarations 
pygame.init()
pygame.font.init()
mainClock = pygame.time.Clock()

# Game properties
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720
OBSTACLE_HEIGHT = 220
RUNNING = True
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
random.seed(5)
obstacles = []
score = 0

# Open CV Declarations
mp_hands = mp.solutions.hands
capture = cv.VideoCapture(0)

# Player Class
class Player:
    def __init__(self, speed, height, vertical_velocity, gravity, sprite, w, h):
        self.speed = speed              # Speed of player
        self.height = height            # Indicates the y-pos of top left corner of player
        self.vvel = vertical_velocity   
        self.g = gravity                # How fast the bird comes down, negative value
        self.sprite = sprite            # Sprite if something other than a square is desired.
        self.w = w                      # Dimensions: Width of player
        self.h = h                      # Dimensions: Height of player

    def update(self):
        self.height = min(600-self.h, self.height-self.vvel)    # TO ensure player does not fall below platform
        self.vvel += self.g     # Falling down
        
        if self.height == 600-self.h:   # Set falling speed to 0 if on platform.
            self.vvel = 0
    
    def jump(self):                 
        # print("Jumped!")      # Used for debugging purposes, can be removed        
        self.vvel = 20

    def display(self):
        pygame.draw.rect(
            screen,         # Canvas
            (2, 2, 2),      # Color
            (               # Position & Dimensions.
                int(SCREEN_WIDTH*0.2),  
                self.height, 
                self.w, 
                self.h
            )
        )

class Obstacle:
    def __init__(self, index, posx, posy, sidelen, speed):
        self.index = index          # Index with obstacle list
        self.posx = posx            
        self.posy = posy
        self.sidelen = sidelen      # Width of obstacle
        self.speed = speed
        self.flag = False           # False: Haven't been used to create new obstacle

    def update(self):               # Moving the obstacle left
        if self.posx == -1:
            return
        self.posx-=self.speed
        if self.posx < 0:
            self.posx = -1

    def display(self):
        if self.posx == -1:
            return

        pygame.draw.rect(
            screen,             # Canvas
            (255, 0, 0),        # Color
            (                   # Position & Dimensions
                self.posx, 
                0, 
                self.sidelen, 
                self.posy
            )
        )

        pygame.draw.rect(
            screen,             # Canvas
            (255, 0, 0),        # Color
            (                   # Position & Dimensions
                self.posx, 
                self.posy+OBSTACLE_HEIGHT, 
                self.sidelen, 
                600-self.posy-OBSTACLE_HEIGHT
            )
        )

# Pygame Functions---------------------------------------------------------------------------------

def display(): # Display game background & floor
    pygame.draw.line(
        screen, 
        (0, 0, 0), 
        (0, 600), 
        (SCREEN_WIDTH, 600), 
        10
    )

def checkCollision(block, player): # Check if player collide with obstacle (Sort of like hit boxes(?))

    topRect = pygame.Rect(      # Top section of obstacle
        block.posx, 
        0, 
        block.sidelen, 
        block.posy
    )

    botRect = pygame.Rect(      # Bottom section of obstacle
        block.posx, 
        block.posy + OBSTACLE_HEIGHT, 
        block.sidelen, 
        600-block.posy-OBSTACLE_HEIGHT
    )

    playerRect = pygame.Rect(   # Player box
        int(SCREEN_WIDTH*0.2), 
        player.height, 
        player.w, 
        player.h
    )

    return pygame.Rect.colliderect(playerRect, topRect) or pygame.Rect.colliderect(playerRect, topRect)

def generateObstacle(): # Randomly generate an obstacle
    random.seed(time.gmtime())                                  # Seed
    obstacle_xpos = 1080                                        # Default starting x-pos
    obstacle_ypos = random.randint(100, 600-OBSTACLE_HEIGHT)    # Random position for opening

    obstacles.append(
        Obstacle(len(obstacles), 
        obstacle_xpos, 
        obstacle_ypos, 
        50, 
        player1.speed)
    )

# OpenCV Function
def checkGrab(finger_tips, frame):
    """
        Args: 
            finger_tips (location of finger tips)
            frame       (Not used at the moment, might come in handy later on, can be removed)
        Return: 
            True: If grabbing gesture is detected.

        This 'algorithm' works by finding the average points of the five fingers
        and then checking to see if every finger is within 6% (relative to screen size) 
        distance to the average.

        Not perfect, usually breaks when palm is not facing towards camera.
    """

    avg_x = 0
    avg_y = 0

    # Calculating average position of fingertips.
    for points in finger_tips:      
        avg_x += points.x
        avg_y += points.y
    avg_x = avg_x/5
    avg_y = avg_y/5

    # Checking if finger tips are within 6% of average point.
    for i in range(0, 5):
        dist = math.sqrt(math.pow(finger_tips[i].x-avg_x, 2) + math.pow(finger_tips[i].y-avg_y, 2))
        if dist >= 0.06:
            return False
    return True

# Player initialization----------------------------------------------------------------------------------------------

# Creating player object and first obstacle.
player1 = Player(10, 600-70, 0, -3, None, 70, 70)
obstacles.append(Obstacle(len(obstacles), SCREEN_WIDTH, 200, 50, player1.speed))

# Main loop
with mp_hands.Hands(min_detection_confidence=0.6, min_tracking_confidence=0.6) as hands:
    while RUNNING and capture.isOpened():
        score+=1
        screen.fill((255,255,255))
        
        ret, frame = capture.read()
        
        # Screen resizing, can be used depending on preference.
        # SCALE_FACTOR = 1.5
        # frame = cv.resize(frame, (int(frame.shape[1] * SCALE_FACTOR), int(frame.shape[0] * SCALE_FACTOR)))
        
        img = cv.cvtColor(cv.flip(frame, 1), cv.COLOR_BGR2RGB)
        img.flags.writeable = False;

        # Results from mediapipe hand recognition.
        results = hands.process(img)
        img = cv.cvtColor(img, cv.COLOR_RGB2BGR)
        frame = cv.flip(frame, 1)

        # Event checking.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:       # Closing application
                RUNNING = False
            
            if event.type == pygame.KEYDOWN:    # Jump
                if event.key == pygame.K_UP:
                    player1.jump()

        # Mediapipe looping through hand landmarks and finding finger tips.
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Creating list of finger tip locations
                finger_tips = []
                finger_tips.append(hand_landmarks.landmark[4])
                finger_tips.append(hand_landmarks.landmark[8])
                finger_tips.append(hand_landmarks.landmark[12])
                finger_tips.append(hand_landmarks.landmark[16])
                finger_tips.append(hand_landmarks.landmark[20])

                # Check if user is performing the grabbing motion.
                if checkGrab(finger_tips, frame):
                    player1.jump()

        # Generating new obstacles
        for cur_obs in obstacles:
            # Flag is false if current obstacle has not passed 1/3 of screen from right.
            if cur_obs.flag == False:
                if cur_obs.posx < 2*SCREEN_WIDTH/3:
                    generateObstacle()
                    cur_obs.flag = True
                    break

        # Updating obstacles
        for blocks in obstacles:
            blocks.update()
            blocks.display()

        # Checking collision between each obstacle and the player, can definitely be optimized!
        for blocks in obstacles:
            if checkCollision(blocks, player1):
                print("Collision!")
                print("Player: ", player1.height)
                print("Block: ", blocks.posy)
                RUNNING = False

        # Updating and displaying
        player1.update()
        player1.display()
        display()
        pygame.display.update()
        mainClock.tick(120)

        # If you wish to see yourself playing the game.
        # cv.imshow('Video', frame)

        # Quit statement, press 'q' to quit, can be changed.
        if cv.waitKey(10) & 0xFF == ord('q'):
            break

capture.release()
cv.destroyAllWindows()