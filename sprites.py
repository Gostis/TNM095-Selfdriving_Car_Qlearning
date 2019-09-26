import pygame as pg
from settings import *
from tilemap import *

vec = pg.math.Vector2

"""
class CarSprite(pygame.sprite.Sprite):

    MAX_FORWARD_SPEED = 0.2
    MAX_REV_SPEED = 0.2
    TURN_SPEED = 0.7

    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.player_img
        self.position = vec(x, y)
        # self.hit_rect = PLAYER_HIT_RECT
        # self.hit_rect.center = self.rect.center
        self.speed = self.direction = 0
        self.k_left = self.k_right = self.k_down = self.k_up = 0

    def get_keys(self, event):
        keys = pg.key.get_pressed()

        keyIsDown = event.type == KEYDOWN

        if event.key == K_RIGHT:
            self.k_right = -0.1
        elif event.key == K_LEFT:
            self.k_left = 0.1
        elif keys[K_UP]:
            self.k_up += 0.01
        elif keys[K_DOWN]:
            self.k_down += -0.01
        elif keys[K_SPACE]:
            self.speed = 0
            self.k_up = 0
            self.k_down = 0
        elif keys[K_ESCAPE]:
            self.exit(0)
        elif keys[K_r]:
            self.position = 500, 500

    def update(self):
        self.speed += (self.k_up + self.k_down)

        if self.speed > self.MAX_FORWARD_SPEED:
            self.speed = self.MAX_FORWARD_SPEED
        if self.speed < -self.MAX_REV_SPEED:
            self.speed = -self.MAX_REV_SPEED

        self.direction += (self.k_right + self.k_left)
        x, y = (self.position)
        self.rad = self.direction * math.pi / 180
        x += -self.speed * math.sin(self.rad)
        y += -self.speed * math.cos(self.rad)
        self.position = (x, y)
        self.image = pygame.transform.rotate(self.src_image, self.direction)
        self.rect = self.image.get_rect()
        self.rect.center = self.position
"""


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.startPosition = vec(x,y)
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
        self.hitSomething = False

    def get_keys(self):
        # decrement speed instead
        self.vel = vec(0, 0)
        self.rot_speed = 0
        keys = pg.key.get_pressed()

        if keys[pg.K_LEFT] or keys[pg.K_a]:
            self.rot_speed = PLAYER_ROT_SPEED
        if keys[pg.K_RIGHT] or keys[pg.K_d]:
            self.rot_speed = -PLAYER_ROT_SPEED
        if keys[pg.K_UP] or keys[pg.K_w]:
            # Trigonometri ~ woop woop
            self.vel = vec(PLAYER_SPEED, 0).rotate(-self.rot +
                                                   ROTATE_SPRITE_DEG)
        if keys[pg.K_DOWN] or keys[pg.K_s]:
           # Backa?
            self.vel = vec(-PLAYER_SPEED / 2, 0).rotate(-self.rot +  ROTATE_SPRITE_DEG)

    def collide_with_walls(self):

        # puts the car on the edge. This will probably be removed
        hits = pg.sprite.spritecollide(
            self, self.game.walls, False, collide_hit_rect)
        if hits:
          self.hitSomething = True

        goalHit = pg.sprite.spritecollide(self, self.game.goals, False, collide_hit_rect)
        if goalHit:
            print('GOAL!!!!')


    def update(self):
        self.get_keys()
        self.pos += self.vel * self.game.dt
        # %360 only between 0 - 360
        self.rot = (self.rot + self.rot_speed * self.game.dt) % 360
        self.rad = -( self.rot * math.pi / 180)
        self.image = pg.transform.rotate(self.game.player_img, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

        # collision check
        self.hit_rect.centerx = self.pos.x
        self.hit_rect.centery = self.pos.y
        self.collide_with_walls()

        self.rect.center = self.hit_rect.center
        if(self.hitSomething):
            self.hitSomething = False
            self.pos = vec(self.startPosition.x,self.startPosition.y)
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


class RayCast():
    def __init__(self, origin, point, angle, obstacles):
        self.currentPos = vec(origin)
        self.target = self.rotate(origin, point, angle)
        self.heading = vec(self.target) - vec(origin)
        self.collidePoint = self.collisions(
            self.heading, self.currentPos, obstacles)

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
                    return currentPos
        return currentPos
