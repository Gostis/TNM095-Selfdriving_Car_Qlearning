import pygame as pg
from settings import *
from tilemap import *
import math
vec = pg.math.Vector2


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.startPosition = vec(x, y)
        self.startRotation = 0

        self.game = game
        self.image = game.player_img
        self.rect = self.image.get_rect()
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.rot = 0
        self.rad = 0
        self.rot_speed = 0
        self.hitWall = False
        self.hitGoal = False

    def __sub__(self, other):
        return ((self.pos.x - other.x ) // TILESIZE, (self.pos.y - other.y)// TILESIZE)

    def action(self, choice):
        self.rot_speed = 0
        if choice == 0:
            #self.move(x=1, y=0)
            self.rot_speed = PLAYER_ROT_SPEED
        elif choice == 1:
            #self.move(x=-1, y=0)
            self.rot_speed = -PLAYER_ROT_SPEED


    def get_keys(self):
        # decrement speed instead
        self.vel = vec(0, 0)
        #self.rot_speed = 0
        keys = pg.key.get_pressed()

        #if keys[pg.K_LEFT] or keys[pg.K_a]:
        #    self.rot_speed = PLAYER_ROT_SPEED
        #if keys[pg.K_RIGHT] or keys[pg.K_d]:
        #    self.rot_speed = -PLAYER_ROT_SPEED
        if ~keys[pg.K_UP] or keys[pg.K_w]:
            # Trigonometri ~ woop woop
            self.vel = vec(PLAYER_SPEED, 0).rotate(-self.rot +
                                                   ROTATE_SPRITE_DEG)
        #if keys[pg.K_DOWN] or keys[pg.K_s]:
        #   # Backa?
        #    self.vel = vec(-PLAYER_SPEED / 2,
        #                   0).rotate(-self.rot + ROTATE_SPRITE_DEG)

    def collide_with_walls(self):

        self.hits = pg.sprite.spritecollide(
            self, self.game.walls, False, collide_hit_rect)
        if self.hits:
            self.hitWall = True

        goalHit = pg.sprite.spritecollide(
            self, self.game.goals, False, collide_hit_rect)
        if goalHit:
            self.hitGoal = True
            print('GOAL!!!!')

    def update(self):
        self.get_keys()
        #print(f"Pos 1: {self.pos.x}, {self.pos.y}")
        self.pos += self.vel #* self.game.dt
        #print(f"Pos 2: {self.pos.x}, {self.pos.y}")
        # %360 only between 0 - 360
        self.rot = (self.rot + self.rot_speed * self.game.dt) % 360
        self.rad = -(self.rot * math.pi / 180)
        self.image = pg.transform.rotate(self.game.player_img, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

        # collision check
        self.hit_rect.centerx = self.pos.x
        self.hit_rect.centery = self.pos.y
        self.collide_with_walls()


        self.rect.center = self.hit_rect.center

        if(self.hitWall):
            self.hitWall = False
            self.pos = vec(self.startPosition.x, self.startPosition.y)
            self.rot = self.startRotation

        if(self.hitGoal):
            self.hitGoal = False
            self.pos = vec(self.startPosition.x, self.startPosition.y)
            self.rot = self.startRotation

"""" NOT WORKING
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
                    return currentPos , self.distance(self.target, self.currentPos)
        return currentPos, 0

    def distance(self, collisionPoint, currentPos):
                # Calculates the eucliean distance from the center of the car to the targeted position, i.e distance
                # is wrong by TILESIZE / 2. Subtracting could be redundant
        return RAYCAST_LENGTH - math.sqrt((collisionPoint[0] - currentPos.x) ** 2 + (collisionPoint[1] - currentPos.y) ** 2)




