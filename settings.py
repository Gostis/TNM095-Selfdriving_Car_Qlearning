import pygame as pg
import math
# define some colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

# game settings
WIDTH = 1280  # 16 * 64 or 32 * 32 or 64 * 16
HEIGHT = 660  # 16 * 48 or 32 * 24 or 64 * 12


FPS = 60
TITLE = "Tilemap Demo"
BGCOLOR = DARKGREY

# 8 x 8
# 44x81
#TILESIZE = 22
TILESIZE = 16
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE


# Player settings
PLAYER_SPEED = 300
PLAYER_IMG = 'tank_1.png'
SHRINK_FACTOR = 8
PLAYER_ROT_SPEED = 250
ROTATE_SPRITE_DEG = 90
# PLAYER_HIT_RECT = pg.Rect(0, 0, math.floor(
#    443 / SHRINK_FACTOR), math.floor(207 / SHRINK_FACTOR))
PLAYER_HIT_RECT = pg.Rect(0, 0, math.floor(
    32), math.floor(32))

# RAYCAST
RAYCAST_LENGTH = 100