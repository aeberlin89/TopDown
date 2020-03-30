import pygame as pg
import pytmx
from settings import *


def collide_hit_rect(one, two):
    #returns true or false
    return one.hit_rect.colliderect(two.rect)

def collide_item_hit_rect(one, two):
    #returns true or false
    return one.hit_rect.colliderect(two.hit_rect)

class Map:
    def __init__(self, filename):
        self.data = []
        with open(filename, 'rt') as f:
            for line in f:
                self.data.append(line.strip())

        self.tilewidth = len(self.data[0])
        self.tileheight = len(self.data)
        self.width = self.tilewidth * TILESIZE
        self.height = self.tileheight * TILESIZE

class TiledMap:
    def __init__(self, filename):
        self.tm = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = self.tm.width * self.tm.tilewidth
        self.height = self.tm.height * self.tm.tileheight
        self.tmxdata = self.tm

    def render(self, surface):
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid, in layer:
                    tile = ti(gid)
                    if tile:
                        surface.blit(tile, (x * self.tmxdata.tilewidth,
                                            y * self.tmxdata.tileheight))

    def make_map(self):
        temp_surface = pg.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface

    def zoom(self, img, dir):
        self.width *= dir
        self.height *= dir
        temp_surface = img
        temp_surface = pg.transform.scale(temp_surface, (int(self.width), int(self.height)))
        print(self.width, self.height)
        self.render(temp_surface)
        return temp_surface

    #def zoom(self, dir):
        #if dir == 'in':
        #    self.tm.width += 1
        #    self.tm.height += 1
        #if dir == 'out':
        #    self.tm.width -= 1
        #    self.tm.height -= 1

class Camera:
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def scroll(self, dir, game):
        self.game = game
        self.dir = dir
        if self.dir == 'up':
            print('down')
            print(self.height, '/', game.map.height)
            if self.height >= HEIGHT + 10:
                self.height -= 10

        elif self.dir == 'down':
            print('down')
            print(self.height, '/', game.map.height)
            if self.height <= game.map.height - 10:
                self.height += 10

        elif self.dir == 'left':
            print('left')
            print(WIDTH)
            print(self.width, '/', game.map.width)
            if self.width >= WIDTH + 10:
                self.width -= 10

        elif self.dir == 'right':
            print('right')
            print(WIDTH)
            print(self.width, '/', game.map.width)
            if self.width <= game.map.width - 10:
                self.width += 10


    def update(self, target):
        x = -target.rect.centerx + int(WIDTH/2)
        y = -target.rect.centery + int(HEIGHT/2)

        #limit scrolling to map size
        x = min(0, x) #left
        y = min(0, y) #top
        x = max(-(self.width - WIDTH), x) #right
        y = max(-(self.height - HEIGHT), y) #bottom
        #print('camera x: ', x, 'camera y: ', y)

        #x, y are negatives of topleft coordinates of screen because of offset
        self.camera = pg.Rect(x, y, self.width, self.height)
