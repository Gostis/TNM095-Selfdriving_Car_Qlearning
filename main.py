import pygame as pg
import sys
from os import path
from settings import *
from sprites import *
from tilemap import *
import math


class Game:
    def __init__(self):
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()

        # repeating wont be needed.
        pg.key.set_repeat(500, 100)

        self.load_data()

    def load_data(self):
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'images')
        self.map = Map(path.join(game_folder, 'map.txt'))
        # Other image
        # self.map = TiledMap(path.join(img_folder, 'MAP1_COLISIONS.tmx'))
        # self.map_img = self.map.make_map()
        # self.map_rect = self.map_img.get_rect()

        self.player_img = pg.image.load(
            path.join(img_folder, PLAYER_IMG)).convert_alpha()
        # Other car
        # .player_img = pg.transform.rotate(pg.transform.scale(self.player_img, (math.floor(self.player_img.get_width() / SHRINK_FACTOR ),math.floor(self.player_img.get_height() / SHRINK_FACTOR))), 180-ROTATE_SPRITE_DEG)
       # self.player_img = pg.transform.rotate(pg.transform.scale(
       #     self.player_img, (self.player_img.get_width(), #self.player_img.get_height())), 0)

    def new(self):
        # initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.goals = pg.sprite.Group()
        # self.player = Player(self,4, 12)

        for row, tiles in enumerate(self.map.data):
            for col, tile in enumerate(tiles):
                if tile == 'x':
                    Wall(self, col, row)
                if tile == 'P':
                    self.player = Player(self, 100, 200)
                if tile == 'G':
                    Goal(self, col, row)

        '''
        for tile_object in self.map.tmxdata.objects:
            if tile_object.name == 'Player':
                self.player = Player(self, 100, 100)

            if tile_object.name == 'Death':
                Obstacle(self,tile_object.x *TILESIZE ,tile_object.y * TILESIZE,
                         tile_object.width * TILESIZE,tile_object.height * TILESIZE)
        '''

    def run(self):
        # game loop - set self.playing = False to end the game
        self.playing = True
        self.coll = False
        self.i = 0
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        # update portion of the game loop
        self.all_sprites.update()

        # Raycasts
        self.rayCastSouth = RayCast((self.player.pos.x, self.player.pos.y), (
            self.player.pos.x, self.player.pos.y - RAYCAST_LENGTH), self.player.rad, self.walls)

        self.rayCastNorth = RayCast((self.player.pos.x, self.player.pos.y), (
            self.player.pos.x, self.player.pos.y + RAYCAST_LENGTH), self.player.rad, self.walls)

        self.rayCastEast = RayCast((self.player.pos.x, self.player.pos.y), (
            self.player.pos.x + RAYCAST_LENGTH, self.player.pos.y), self.player.rad, self.walls)

        self.rayCastWest = RayCast((self.player.pos.x, self.player.pos.y), (
            self.player.pos.x - RAYCAST_LENGTH, self.player.pos.y), self.player.rad, self.walls)

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def draw(self):
        self.screen.fill(BGCOLOR)

        # self.screen.blit(self.map_img, (0,0))
        self.draw_grid()

        self.all_sprites.draw(self.screen)
        # Raycasts

        pg.draw.line(self.screen, LIGHTGREEN,
                     (self.player.pos.x, self.player.pos.y), self.rayCastSouth.target, 2)
        pg.draw.circle(self.screen, TEAL, [
            int(x) for x in self.rayCastSouth.collidePoint], 5)

        pg.draw.line(self.screen, LIGHTGREEN,
                     (self.player.pos.x, self.player.pos.y), self.rayCastNorth.target, 2)
        pg.draw.circle(self.screen, TEAL, [
            int(x) for x in self.rayCastNorth.collidePoint], 5)

        pg.draw.line(self.screen, LIGHTGREEN,
                     (self.player.pos.x, self.player.pos.y), self.rayCastEast.target, 2)
        pg.draw.circle(self.screen, TEAL, [
            int(x) for x in self.rayCastEast.collidePoint], 5)

        pg.draw.line(self.screen, LIGHTGREEN,
                     (self.player.pos.x, self.player.pos.y), self.rayCastWest.target, 2)
        pg.draw.circle(self.screen, TEAL, [
            int(x) for x in self.rayCastWest.collidePoint], 5)

        #####
        pg.draw.rect(self.screen, WHITE, self.player.hit_rect, 2)
        pg.display.flip()

    def events(self):
        # catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()

    def show_start_screen(self):
        pass

    def show_go_screen(self):
        pass


# create the game object
g = Game()
g.show_start_screen()
while True:
    g.new()
    g.run()
    g.show_go_screen()
