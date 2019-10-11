import pygame as pg
import math
# define some colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
LIGHTGREEN = (50, 190, 100)
TEAL = (40, 180, 250)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# game settings
WIDTH = 320 #1280  # 16 * 64 or 32 * 32 or 64 * 16      #320
HEIGHT = 320 #512  # 16 * 48 or 32 * 24 or 64 * 12      #320

FPS = 60
TITLE = "Tilemap Demo"
BGCOLOR = DARKGREY

# 8 x 8
# 44x81
#TILESIZE = 22
TILESIZE = 16
GRIDWIDTH = WIDTH // TILESIZE
GRIDHEIGHT = HEIGHT // TILESIZE


# Player settings
PLAYER_SPEED = 10
PLAYER_IMG = 'tank_1.png'
SHRINK_FACTOR = 8
PLAYER_ROT_SPEED = 40
ROTATE_SPRITE_DEG = 90
# PLAYER_HIT_RECT = pg.Rect(0, 0, math.floor(
#    443 / SHRINK_FACTOR), math.floor(207 / SHRINK_FACTOR))
PLAYER_HIT_RECT = pg.Rect(0, 0, math.floor(
    32), math.floor(32))

# RAYCAST
RAYCAST_LENGTH = 100
NUMBER_OF_RAYCASTS = 4


# Machine Learning
LEARNING = False
ITERATIONS = 2000
HM_EPISODES = 100000
MOVE_PENALTY = 1
DEATH_PENALTY = ITERATIONS
FOOD_REWARD = ITERATIONS
EPS_DECAY = 0.998
SHOW_EVERY = 1000

LEARNING_RATE = 0.01 #0.8
DISCOUNT = 0.90    #0.95

NUMBER_OF_ACTIONS = 3