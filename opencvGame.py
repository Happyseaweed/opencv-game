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
STATE = 0   # 0 = start menu, 1 = game running, 2 = game over screen;
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
random.seed(5)
obstacles = []
score = 0
hiscore = 0


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

    return pygame.Rect.colliderect(playerRect, topRect) or pygame.Rect.colliderect(playerRect, botRect)

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
            
        ret, frame = capture.read()

        if STATE == 0:
            # Display menu screen
            screen.fill((255, 255, 255))
            
            #Display game menu
            font = pygame.font.SysFont('Corbel', 35)
            font1 = pygame.font.SysFont('Corbel', 60)
            
            text_start = font.render('Start Game', True, (255, 255, 255))
            text_quit = font.render('Quit', True, (255, 255, 255))
            text_msg = font1.render("\"Just Remember, Don't Touch the Red Stuff\"", True, (0, 0, 0))

            text_tut1 = font.render("Here's how to play:", True, (0, 0, 0))
            text_tut2 = font.render("1. Make sure your camera is facing you.", True, (0, 0, 0))
            text_tut3 = font.render("2. Make sure your palm is facing the camera.", True, (0, 0, 0))
            text_tut4 = font.render("3. Make a \"pinch o' salt\" gesture with that hand.", True, (0, 0, 0))
            text_tut5 = font.render("4. No matter what you do, don't touch the red stuff...", True, (0, 0, 0))

            screen.blit(text_msg, (100, 100))
            screen.blit(text_tut1, (50, 450))
            screen.blit(text_tut2, (50, 490))
            screen.blit(text_tut3, (50, 530))
            screen.blit(text_tut4, (50, 570))
            screen.blit(text_tut5, (50, 610))

            pygame.draw.rect(screen, (100, 100, 100), (520, 280, 180, 60))
            pygame.draw.rect(screen, (100, 100, 100), (520, 380, 180, 60))

            screen.blit(text_start, (540, 300))
            screen.blit(text_quit, (540, 400))

            pygame.draw.rect(screen, (0, 0, 0), (800, 600, 300, 300))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:       # Closing application
                    RUNNING = False
                if event.type == pygame.KEYDOWN:    # Pressing 'q' to quit the game.
                    if (event.key == pygame.K_q):
                        RUNNING = False
                        break
                if event.type == pygame.MOUSEBUTTONDOWN:
                    cx, cy = pygame.mouse.get_pos()
                    if cx >= 520 and cx <= 700:
                        if cy <= 440 and cy >= 380:
                            RUNNING = False
                            break
                        if cy <= 340 and cy >= 280:
                            STATE = 1

        elif STATE == 2:
            # Display menu screen
            screen.fill((255, 255, 255))
            
            #Display game menu
            hiscore = max(hiscore, score)
            font = pygame.font.SysFont('Corbel', 35)
            font1 = pygame.font.SysFont('Corbel', 60)
            text_start = font.render('Restart', True, (255, 255, 255))
            text_quit = font.render('Quit', True, (255, 255, 255))
            text_score = font.render("Distance: "+ str(score), True, (255, 255, 255))
            text_hiscore = font.render("High Score : "+ str(hiscore), True, (255, 255, 255))
            text_endmsg = font1.render('Oops, the red stuff is *NOT* your friend!', True, (0, 0, 0))

            screen.blit(text_endmsg, (120, 100))

            pygame.draw.rect(screen, (100, 100, 100), (520, 280, 180, 60))
            pygame.draw.rect(screen, (100, 100, 100), (520, 380, 180, 60))

            screen.blit(text_start, (540, 300))
            screen.blit(text_quit, (540, 400))

            pygame.draw.rect(screen, (100, 100, 100), (180, 280, 220, 60))
            pygame.draw.rect(screen, (100, 100, 100), (180, 380, 220, 60))

            screen.blit(text_hiscore, (200, 300))
            screen.blit(text_score, (200, 400))


            for event in pygame.event.get():
                if event.type == pygame.QUIT:       # Closing application
                    RUNNING = False
                if event.type == pygame.KEYDOWN:    # Pressing 'q' to quit the game.
                    if (event.key == pygame.K_q):
                        RUNNING = False
                        break
                if event.type == pygame.MOUSEBUTTONDOWN:
                    cx, cy = pygame.mouse.get_pos()
                    if cx >= 520 and cx <= 700:
                        if cy <= 440 and cy >= 380:
                            RUNNING = False
                            break
                        if cy <= 340 and cy >= 280:
                            player1 = Player(10, 600-70, 0, -3, None, 70, 70)
                            obstacles.clear()
                            score = 0
                            random.seed(5)
                            obstacles.append(Obstacle(len(obstacles), SCREEN_WIDTH, 200, 50, player1.speed))
                            
                            STATE = 1

        elif STATE == 1:

            score+=1
            screen.fill((255,255,255))

            img = cv.cvtColor(cv.flip(frame, 1), cv.COLOR_BGR2RGB)
            img.flags.writeable = False

            # Results from mediapipe hand recognition.
            results = hands.process(img)
            img = cv.cvtColor(img, cv.COLOR_RGB2BGR)
            frame = cv.flip(frame, 1)

            font = pygame.font.SysFont('Corbel', 35)
            text_score = font.render("Distance: "+str(score), True, (255, 255, 255))
            pygame.draw.rect(screen, (100, 100, 100), (180, 620, 220, 60))
            screen.blit(text_score, (200, 640))

            # Event checking.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:       # Closing application
                    RUNNING = False
                
                if event.type == pygame.KEYDOWN:    # Jump
                    if event.key == pygame.K_UP:
                        player1.jump()

                if event.type == pygame.KEYDOWN:
                    if (event.key == pygame.K_q):
                        RUNNING = False
                        break

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
                    STATE = 2

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