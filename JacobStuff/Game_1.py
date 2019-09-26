import pygame
import math
import sys
import time
from pygame.locals import *
from pygame.math import Vector2

pygame.init()
screen = pygame.display.set_mode((600, 600))
clock = pygame.time.Clock()


def ray_cast(origin, target, obstacles):
    currentPos = Vector2(origin)
    heading = target - origin

    direction = heading.normalize()
    for i in range(int(heading.length())):
        currentPos += direction
        for sprite in obstacles:
            if sprite.rect.collidepoint(currentPos):
                return currentPos
    return Vector2(target)


def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy


class Block(pygame.sprite.Sprite):
    def __init__(self, color, width, height, pos):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.Surface([width, height])
        self.image.fill(color)

        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos[0], pos[1]


class CarSprite(pygame.sprite.Sprite):

    MAX_FORWARD_SPEED = 0.2
    MAX_REV_SPEED = 0.2
    TURN_SPEED = 0.7

    def __init__(self, image, pos):
        pygame.sprite.Sprite.__init__(self)
        self.src_image = pygame.image.load(image)
        self.position = pos
        self.speed = self.direction = 0
        self.k_left = self.k_right = self.k_down = self.k_up = 0

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


rect = screen.get_rect()
car = CarSprite('car_small_1.png', (500, 500))
block = Block(pygame.Color('goldenrod4'), 120, 60, [300, 300])
block_group = pygame.sprite.RenderPlain(block)
car_group = pygame.sprite.RenderPlain(car)
run = True
while run:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

        if not hasattr(event, 'key'):
            continue
        """
        down = event.type == KEYDOWN

        if event.key == K_RIGHT:
            car.k_right = down * -1
        elif event.key == K_LEFT:
            car.k_left = down * 1
        elif event.key == K_UP:
            car.k_up = down * 5
        elif event.key == K_DOWN:
            car.k_down = down * -5
        elif event.key == K_ESCAPE:
            sys.exit(0)
        """
        keys = pygame.key.get_pressed()

        keyIsDown = event.type == KEYDOWN

        if event.key == K_RIGHT:
            car.k_right = keyIsDown * -0.5
        elif event.key == K_LEFT:
            car.k_left = keyIsDown * 0.5
        elif keys[K_UP]:
            car.k_up += 0.01
        elif keys[K_DOWN]:
            car.k_down += -0.04
        elif keys[K_SPACE]:
            car.speed = 0
            car.k_up = 0
            car.k_down = 0
        elif keys[K_ESCAPE]:
            sys.exit(0)
        elif keys[K_r]:
            car.position = 500, 500

    screen.fill((30, 30, 30))
    car_group.update()

    collisions = pygame.sprite.groupcollide(
        car_group, block_group, False, True, collided=None)

    rayCastEnd = rotate(
        car.position, (car.position[0], car.position[1] - 200), -car.rad)
    rayCastVec = Vector2(rayCastEnd)
    collision_point = ray_cast(car.position, rayCastVec, block_group)

    if collisions != {}:
        pass
    pygame.draw.line(screen, (50, 190, 100), car.position, rayCastVec, 2)
    pygame.draw.circle(screen, (40, 180, 250), [
                       int(x) for x in collision_point], 5)
    pygame.draw.rect(screen, (255, 0, 0), car.rect, 2)
    car_group.draw(screen)
    block_group.draw(screen)

    pygame.display.flip()

pygame.quit()
