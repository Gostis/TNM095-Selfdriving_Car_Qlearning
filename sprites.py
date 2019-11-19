import pygame as pg
from settings import *
from tilemap import *
import numpy as np
vec = pg.math.Vector2

class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.gamer_class
        pg.sprite.Sprite.__init__(self, self.groups)
        self.startPosition = vec(x, y)
        self.startRotation = ROTATE_SPRITE_DEG_PLAYER
        self.game = game
        self.image = game.player_img
        self.rect = self.image.get_rect()
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.rot = self.startRotation
        self.rad = 0
        self.rot_speed = 0
        self.hitWall = False
        self.hitGoal = False
        self.hitReward = False
        self.posToTile = vec(x // TILESIZE, y // TILESIZE)

    def move(self, x=False, y=False):
        if not x:
            pass
        else:
            self.pos.x += x
        if not y:
            pass
        else:
            self.pos.y += y

        if self.pos.x < 0:
            self.pos.x = 0
        elif self.pos.x > WIDTH - 1:
            self.pos.x = WIDTH - 1

        if self.pos.y < 0:
            self.pos.y = 0
        elif self.pos.y > HEIGHT - 1:
            self.pos.y = HEIGHT - 1

    def getPosToTileSize(self):
        if(self.pos.x // TILESIZE > GRIDWIDTH):
            self.posToTile.x = GRIDWIDTH - 1
            #self.pos.x = GRIDWIDTH - 1

        if(self.pos.y // TILESIZE > GRIDHEIGHT):
            self.posToTile.y = GRIDHEIGHT - 1
            #self.pos.y = GRIDHEIGHT - 1

        if(self.pos.x // TILESIZE < GRIDWIDTH or self.pos.y // TILESIZE < GRIDHEIGHT):
            self.posToTile.x = abs(self.pos.x // TILESIZE)
            self.posToTile.y = abs(self.pos.y // TILESIZE)

    def resetPosition(self):
        self.pos = vec(self.startPosition.x, self.startPosition.y)
        self.rot = self.startRotation

        if (self.hitWall):
            self.hitWall = False

        if (self.hitGoal):
            self.hitGoal = False

        if(self.hitReward):
            self.hitReward = False

    def get_keys(self):
        # decrement speed instead
        self.vel = vec(0, 0)
        self.rot_speed = 0
        keys = pg.key.get_pressed()

        tempPosX = self.pos.x
        tempPosY = self.pos.y

        if BLOCKMOVEMENT:
            if keys[pg.K_LEFT] or keys[pg.K_a]:
                self.move(x=-TILESIZE // SCALER, y=0)
                self.image = pg.transform.rotate(self.game.player_img, -180 - OFFSET)
            elif keys[pg.K_RIGHT] or keys[pg.K_d]:
                self.move(x=TILESIZE // SCALER, y=0)
                self.image = pg.transform.rotate(self.game.player_img, 0 - OFFSET)
            elif keys[pg.K_UP] or keys[pg.K_w]:
                self.move(x=0, y=-TILESIZE // SCALER)
                self.image = pg.transform.rotate(self.game.player_img, 90 - OFFSET)
            elif keys[pg.K_DOWN] or keys[pg.K_s]:
                self.move(x=0, y=TILESIZE // SCALER)
                self.image = pg.transform.rotate(self.game.player_img, -90 - OFFSET)
            elif keys[pg.K_q]:
                self.move(x=-TILESIZE * 0.7071 // SCALER,y=-TILESIZE * 0.7071 // SCALER)
                self.image = pg.transform.rotate(self.game.player_img, 45)
            elif keys[pg.K_e]:
                self.move(x=TILESIZE * 0.7071 // SCALER, y=-TILESIZE * 0.7071 // SCALER)
                self.image = pg.transform.rotate(self.game.player_img, -45)
            elif keys[pg.K_c]:
                self.move(x=TILESIZE * 0.7071 // SCALER, y=TILESIZE * 0.7071 // SCALER)
                self.image = pg.transform.rotate(self.game.player_img, -135)
            elif keys[pg.K_z]:
                self.move(x=-TILESIZE * 0.7071 // SCALER, y=TILESIZE * 0.7071 // SCALER)
                self.image = pg.transform.rotate(self.game.player_img, 135)
        else:
            if keys[pg.K_LEFT] or keys[pg.K_a]:
                 self.rot_speed = PLAYER_ROT_SPEED
                 self.rot = (self.rot + self.rot_speed) % 360
                 self.vel = vec(PLAYER_SPEED, 0).rotate(-self.rot + ROTATE_SPRITE_DEG)
            if keys[pg.K_RIGHT] or keys[pg.K_d]:
                 self.rot_speed = -PLAYER_ROT_SPEED
                 self.rot = (self.rot + self.rot_speed) % 360
                 self.vel = vec(PLAYER_SPEED, 0).rotate(-self.rot + ROTATE_SPRITE_DEG)
            if keys[pg.K_UP] or keys[pg.K_w]:
                 self.vel = vec(PLAYER_SPEED, 0).rotate(-self.rot + ROTATE_SPRITE_DEG)
            if keys[pg.K_DOWN] or keys[pg.K_s]:
                self.vel = vec(-PLAYER_SPEED, 0).rotate(-self.rot + ROTATE_SPRITE_DEG)

            self.pos += self.vel


        if (self.game.wallPositions[int(self.pos.x // TILESIZE - 1 )][int(self.pos.y // TILESIZE) - 1] == 1):
            self.pos.x = tempPosX
            self.pos.y = tempPosY

        elif (self.game.wallPositions[int(self.pos.x // TILESIZE)][int(self.pos.y // TILESIZE)] == 1):
            self.pos.x = tempPosX
            self.pos.y = tempPosY
        elif (self.game.wallPositions[int(self.pos.x // TILESIZE)][int(self.pos.y // TILESIZE)] == 2):
            self.pos.x = tempPosX
            self.pos.y = tempPosY



        #positionValue = self.pos + self.vel
        #
        #if (positionValue[0] > WIDTH):
        #    self.pos.x = WIDTH - 1
        #elif (positionValue[0] < 0):
        #    self.pos.x = 1
        #elif (positionValue[1] > HEIGHT):
        #    self.pos.y = HEIGHT - 1
        #elif (positionValue[1] < 0):
        #    self.pos.y = 1

    def collide_with_walls(self):
        self.hits = pg.sprite.spritecollide(
            self, self.game.walls, False, collide_hit_rect)
        if self.hits:
            self.hitWall = True

        goalHit = pg.sprite.spritecollide(
            self, self.game.goals, False, collide_hit_rect)
        if goalHit:
            self.hitGoal = True
        """
        rewardHit = pg.sprite.spritecollide(
            self, self.game.reward, True, collide_hit_rect)
        if rewardHit:
            self.hitReward = True
        """

    def update(self):

        self.get_keys()

        self.rad = -(self.rot * math.pi / 180)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        #self.rect.center = self.hit_rect.center
       

        

class Agent(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.startPosition = vec(x, y)
        self.startRotation = ROTATE_SPRITE_DEG
        self.game = game
        self.image = game.player_img
        self.rect = self.image.get_rect()
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.rot = self.startRotation
        self.rad = 0
        self.rot_speed = 0
        self.hitWall = False
        self.hitGoal = False
        self.hitReward = False
        self.toMuchRotation = False
        self.posToTile = vec(x // TILESIZE, y // TILESIZE)

    def __sub__(self, other):
        return ((self.pos.x - other.x) // TILESIZE, (self.pos.y - other.y) // TILESIZE)

    def move(self, x=False, y=False):
        if not x:
            pass
        else:
            self.pos.x += x
        if not y:
            pass
        else:
            self.pos.y += y

        if self.pos.x < 0:
            self.pos.x = 0
        elif self.pos.x > WIDTH - 1:
            self.pos.x = WIDTH - 1

        if self.pos.y < 0:
            self.pos.y = 0
        elif self.pos.y > HEIGHT - 1:
            self.pos.y = HEIGHT - 1

    def getPosToTileSize(self):
        if(self.pos.x // TILESIZE > GRIDWIDTH):
            self.posToTile.x = GRIDWIDTH - 1
            #self.pos.x = GRIDWIDTH - 1

        if(self.pos.y // TILESIZE > GRIDHEIGHT):
            self.posToTile.y = GRIDHEIGHT - 1
            #self.pos.y = GRIDHEIGHT - 1

        if(self.pos.x // TILESIZE < GRIDWIDTH or self.pos.y // TILESIZE < GRIDHEIGHT):
            self.posToTile.x = abs(self.pos.x // TILESIZE)
            self.posToTile.y = abs(self.pos.y // TILESIZE)

    def resetPosition(self):
        self.pos = vec(self.startPosition.x, self.startPosition.y)
        self.rot = self.startRotation

        if (self.hitWall):
            self.hitWall = False

        if (self.hitGoal):
            self.hitGoal = False

        if(self.hitReward):
            self.hitReward = False

    def action(self, choice):
        self.rot_speed = 0
        self.vel = vec(0, 0)

        if BLOCKMOVEMENT:
            if choice == 0:
                self.move(x=-TILESIZE//SCALERBOT, y=0)
                self.image = pg.transform.rotate(self.game.bot_image, -180 - OFFSET)
            elif choice == 1:
                self.move(x=TILESIZE//SCALERBOT, y=0)
                self.image = pg.transform.rotate(self.game.bot_image, 0 - OFFSET)
            elif choice == 2:
                self.move(x=0, y=-TILESIZE//SCALERBOT)
                self.image = pg.transform.rotate(self.game.bot_image, 90 - OFFSET)
            elif choice == 3:
                self.move(x=0, y=TILESIZE//SCALERBOT)
                self.image = pg.transform.rotate(self.game.bot_image, -90 - OFFSET)
            elif choice == 4:
                self.move(x=-TILESIZE * 0.7071 //SCALERBOT, y=-TILESIZE * 0.7071//SCALERBOT)
                self.image = pg.transform.rotate(self.game.bot_image, 135)
            elif choice == 5:
                self.move(x=TILESIZE * 0.7071 //SCALERBOT, y=-TILESIZE * 0.7071 //SCALERBOT)
                self.image = pg.transform.rotate(self.game.bot_image, -45)
            elif choice == 6:
                self.move(x=TILESIZE * 0.7071 //SCALERBOT, y=TILESIZE * 0.7071 //SCALERBOT)
                self.image = pg.transform.rotate(self.game.bot_image, 135)
            elif choice == 7:
                self.move(x=-TILESIZE * 0.7071 //SCALERBOT, y=TILESIZE * 0.7071 //SCALERBOT)
                self.image = pg.transform.rotate(self.game.bot_image, 45)
        else:
            if choice == 0:
                self.rot_speed = PLAYER_ROT_SPEED
                self.rot = (self.rot + self.rot_speed) % 360
            elif choice == 1:
                self.rot_speed = -PLAYER_ROT_SPEED
                self.rot = (self.rot + self.rot_speed) % 360
            elif choice == 2:
                self.vel = vec(PLAYER_SPEED, 0).rotate(-self.rot + ROTATE_SPRITE_DEG)
            elif choice == 3:
                self.vel = vec(-PLAYER_SPEED, 0).rotate(-self.rot +ROTATE_SPRITE_DEG)

            self.pos += self.vel
        #self.vel = vec(PLAYER_SPEED, 0).rotate(-self.rot + ROTATE_SPRITE_DEG)

        positionValue = self.pos + self.vel

        if (positionValue[0] > WIDTH):
            self.pos.x = WIDTH - 1
        elif (positionValue[0] < 0):
            self.pos.x = 1
        elif (positionValue[1] > HEIGHT):
            self.pos.y = HEIGHT - 1
        elif (positionValue[1] < 0):
            self.pos.y = 1


        self.getPosToTileSize()
        #self.collide_with_walls()

    def collide_with_walls(self):

        self.hits = pg.sprite.spritecollide(
            self, self.game.walls, False, collide_hit_rect)
        if self.hits:
            self.hitWall = True

        goalHit = pg.sprite.spritecollide(
            self, self.game.goals, False, collide_hit_rect)
        if goalHit:
            self.hitGoal = True
        """
        rewardHit = pg.sprite.spritecollide(
            self, self.game.reward, True, collide_hit_rect)
        if rewardHit:
            self.hitReward = True
        """

    def update(self):

        self.rad = -(self.rot * math.pi / 180)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

# Quite working?
class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        # self.image = pg.Surface((TILESIZE, TILESIZE))
        # self.image.fill(RED)
        self.rect = pg.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y


"""
class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

"""


class Goal(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.goals
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def __sub__(self, other):
        return (self.x - other.x, self.y - other.y)


class RewardGate(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.reward
        pg.sprite.Sprite.__init__(self, self.groups)

        self.game = game
        self.image = pg.Surface((TILESIZE, TILESIZE))
        self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE

    def __sub__(self, other):
        return (self.x - other.x, self.y - other.y)


class RayCast():
    def __init__(self, origin, point, angle, obstacles):
        self.currentPos = vec(origin)
        self.target = self.rotate(origin, point, angle)
        self.heading = vec(self.target) - vec(origin)
        self.pointAndDistance = self.collisions(
            self.heading, self.currentPos, obstacles)
        self.collidePoint = self.pointAndDistance[0]
        self.distanceToObstacle = self.pointAndDistance[1]

    def rotate(self, origin, point, angle):
        """
        Rotate a point counterclockwise by a given angle around a given origin.

        The angle should be given in radians.
        """
        ox, oy = origin
        px, py = point

        qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
        qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
        return qx, qy

    def collisions(self, heading, currentPos, obstacles):
        direction = heading.normalize()
        for i in range(int(heading.length())):
            currentPos += direction
            for sprite in obstacles:
                if sprite.rect.collidepoint(currentPos):
                    return currentPos, self.distance(self.target, self.currentPos)
        return currentPos, 0

    def distance(self, collisionPoint, currentPos):
                # Calculates the eucliean distance from the center of the car to the targeted position, i.e distance
                # is wrong by TILESIZE / 2. Subtracting could be redundant
        return RAYCAST_LENGTH - math.sqrt((collisionPoint[0] - currentPos.x) ** 2 + (collisionPoint[1] - currentPos.y) ** 2)
