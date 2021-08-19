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

SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 720
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
        self.speed = speed
        self.height = height # indicates the top left corner of player
        self.vvel = vertical_velocity        
        self.g = gravity
        self.sprite = sprite
        self.w = w
        self.h = h

    def update(self):
        self.height = min(600-self.h, self.height-self.vvel)
        # print(self.height)
        # print(self.vvel)
        self.vvel += self.g
        
        if self.height == 600-self.h:
            self.vvel = 0
    
    def jump(self):
        print("Jumped!")
        self.vvel = 20

    def display(self):
        # screen.blit(self.sprite, (int(SCREEN_WIDTH*0.2), self.height))
        pygame.draw.rect(screen, (2, 2, 2), (int(SCREEN_WIDTH*0.2), self.height, self.w, self.h))

class Obstacle:
    def __init__(self, index, posx, posy, sidelen, speed):
        self.index = index
        self.posx = posx
        self.posy = posy
        self.sidelen = sidelen
        self.speed = speed

    def update(self):
        if self.posx == -1:
            return
        self.posx-=self.speed
        if self.posx < 0:
            # del obstacles[self.index]
            self.posx = -1

    def display(self):
        if self.posx == -1:
            return
        pygame.draw.rect(screen, (255, 0, 0), (self.posx, self.posy, self.sidelen, self.sidelen))

# Pygame Functions---------------------------------------------------------------------------------

def display(): # Display game background & floor
    pygame.draw.line(screen, (0, 0, 0), (0, 600), (SCREEN_WIDTH, 600), 10)

def checkCollision(block, player): # Check if player collide with obstacle
    rect1 = pygame.Rect(block.posx, block.posy, block.sidelen, block.sidelen)
    rect2 = pygame.Rect(int(SCREEN_WIDTH*0.2), player.height, player.w, player.h)
    return pygame.Rect.colliderect(rect1, rect2)

def generateObstacle(): # Randomly generate an obstacle
    chance = random.randint(0, 1000)
    length = random.randint(70, 100)
    initH = random.randint(100, 620-length)
    if chance%23 == 0:
        print("Generated! ", chance)
        #obstacles.append(Obstacle(len(obstacles), SCREEN_WIDTH, 30, height, player1.speed))
        obstacles.append(Obstacle(len(obstacles), SCREEN_WIDTH, initH, length, player1.speed))

# OpenCV Function
def checkGrab(finger_tips, frame):
    avg_x = 0
    avg_y = 0
    length = frame.shape[1]
    width = frame.shape[0]

    for points in finger_tips:
        avg_x += points.x
        avg_y += points.y
    
    avg_x = avg_x/5
    avg_y = avg_y/5

    for i in range(0, 5):
        dist = math.sqrt(math.pow(finger_tips[i].x-avg_x, 2) + math.pow(finger_tips[i].y-avg_y, 2));
        if dist >= 0.06:
            return False
    return True

# Player initialization----------------------------------------------------------------------------------------------
# Sprite currently not used due to inconvenience 
# playerImg = pygame.image.load('test.png')
# playerSprite = pygame.transform.scale(playerImg, (int(playerImg.get_width()*0.5), int(playerImg.get_height()*0.5)))

player1 = Player(10, 600-70, 0, -1, playerSprite, 70, 70)

# Main loop
with mp_hands.Hands(min_detection_confidence=0.6, min_tracking_confidence=0.6) as hands:
    while RUNNING and capture.isOpened():
        score+=1
        screen.fill((255,255,255))

        ret, frame = capture.read()
        # frame = cv.resize(frame, (int(frame.shape[1]*1.5), int(frame.shape[0]*1.5)))
        
        img = cv.cvtColor(cv.flip(frame, 1), cv.COLOR_BGR2RGB)
        img.flags.writeable = False;

        results = hands.process(img)
        img = cv.cvtColor(img, cv.COLOR_RGB2BGR)
        frame = cv.flip(frame, 1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: # Closing application
                RUNNING = False
            
            if event.type == pygame.KEYDOWN: # Jump
                # just remove later part of if statement if a flappy-bird effect is desired
                if event.key == pygame.K_UP: #and player1.height == 600-player1.h:
                    player1.jump()

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                finger_tips = []
                finger_tips.append(hand_landmarks.landmark[4])
                finger_tips.append(hand_landmarks.landmark[8])
                finger_tips.append(hand_landmarks.landmark[12])
                finger_tips.append(hand_landmarks.landmark[16])
                finger_tips.append(hand_landmarks.landmark[20])

                if checkGrab(finger_tips, frame):
                    player1.jump()


        generateObstacle()

        for blocks in obstacles:
            blocks.update()
            blocks.display()

        for blocks in obstacles:
            if checkCollision(blocks, player1):
                print("Collision!")
                print("Player: ", player1.height)
                print("Block: ", blocks.posy)
                RUNNING = False


        player1.update()
        player1.display()
        display()
        pygame.display.update()
        mainClock.tick(60)

        # cv.imshow('Video', frame)
        if cv.waitKey(10) & 0xFF == ord('q'):
            break

capture.release()
cv.destroyAllWindows()
