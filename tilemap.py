import pygame as py
from settings import *
import pytmx
import pygame as pg


def collide_hit_rect(one, two):
    return one.hit_rect.colliderect(two.rect)


class Map:
    def __init__(self, filename):
        self.data = []
        with open(filename, 'rt') as f:
            for line in f:
                self.data.append(line)

        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)
        #pixwidth of map
        self.width = self.tilewidth * TILESIZE
        self.height = self.tileheight * TILESIZE

''''
class TiledMap:
    def __init__(self, filename):
        tm = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = tm.width * tm.tilewidth * TILESIZE
        self.height = tm.height * tm.tileheight * TILESIZE
        self.tmxdata = tm

    def render(self, surface):
        ti = self.tmxdata.get_tile_image_by_gid

        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for(x,y, gid) in layer:
                    tile = ti(gid)
                    if tile:
                        tile = pg.transform.scale(tile, (TILESIZE, TILESIZE))
                        surface.blit(tile, (x * TILESIZE, y*TILESIZE))

        print(self.tmxdata.visible_object_groups)

    def make_map(self):
        temp_surface = pg.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface
'''