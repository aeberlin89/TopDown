#Tilemap Demo
import pygame as pg
import sys
from os import path
from settings import *
from sprites import *
from tilemap import *
from itertools import cycle

#HUD functions
def draw_player_health(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 100
    BAR_HEIGHT = 20
    fill = pct * BAR_LENGTH
    outline_rect = pg.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pg.Rect(x, y, fill, BAR_HEIGHT)
    if pct > 0.6:
        col = GREEN
    elif pct > 0.3:
        col = YELLOW
    else:
        col = RED
    pg.draw.rect(surf, col, fill_rect)
    pg.draw.rect(surf, WHITE, outline_rect, 2)

class Game:
    def __init__(self):
        pg.mixer.pre_init(44100, -16, 1, 2048)
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()

        #use keyboard repeat function if key is held down
        #first parameter is how long the key needs to be held - in ms - to start repeating
        #second parameter is how long between each 'repeat' once repeating starts
        pg.key.set_repeat(0, 500)
        self.current_level = 1
        self.weapon_list = WEAPON_LIST
        self.weapon_index = 0

        self.score = 0
        self.load_data()

    def draw_text(self, text, font_name, size, color, x, y, align="nw"):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "nw":
            text_rect.topleft = (x, y)
        elif align == "ne":
            text_rect.topright = (x, y)
        elif align == "se":
            text_rect.bottomleft = (x, y)
        elif align == "sw":
            text_rect.bottomright = (x, y)
        elif align == "n":
            text_rect.midtop = (x, y)
        elif align == "s":
            text_rect.midbottom = (x, y)
        elif align == "e":
            text_rect.midright = (x, y)
        elif align == "w":
            text_rect.midleft = (x, y)
        elif align == "center":
            text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)


    def load_data(self):
        game_folder = path.dirname(__file__)
        img_folder = path.join(game_folder, 'img')
        snd_folder = path.join(game_folder, 'snd')
        music_folder = path.join(game_folder, 'music')
        self.map_folder = path.join(game_folder, 'maps')

        self.title_font = path.join(img_folder, 'ZOMBIE.TTF')
        #make dim screen for pausing
        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 180))

        #self.weapon_list = WEAPON_LIST

        self.player_img = pg.image.load(path.join(img_folder, PLAYER_IMG)).convert_alpha()
        self.bullet_images = {}
        self.bullet_images['lg'] = pg.image.load(path.join(img_folder, BULLET_IMG)).convert_alpha()
        self.bullet_images['sm'] = pg.transform.scale(self.bullet_images['lg'], (10, 10))
        self.mob_img = pg.image.load(path.join(img_folder, MOB_IMG)).convert_alpha()
        self.wall_img = pg.image.load(path.join(img_folder, WALL_IMG)).convert_alpha()
        self.wall_img = pg.transform.scale(self.wall_img, (TILESIZE, TILESIZE))
        self.splat = pg.image.load(path.join(img_folder, SPLAT)).convert_alpha()
        self.splat = pg.transform.scale(self.splat, (int(TILESIZE), int(TILESIZE)))

        self.gun_flashes = []
        for img in MUZZLE_FLASHES:
            self.gun_flashes.append(pg.image.load(path.join(img_folder, img)).convert_alpha())
        self.item_images = {}
        for item in ITEM_IMAGES:
            self.item_images[item] = pg.image.load(path.join(img_folder, ITEM_IMAGES[item])).convert_alpha()
            self.item_images[item] = pg.transform.scale(self.item_images[item], (int(TILESIZE/2), int(TILESIZE/2.5)))

        #Lighting effect
        self.fog = pg.Surface((WIDTH,HEIGHT))
        self.fog.fill(NIGHT_COLOR)
        self.light_mask = pg.image.load(path.join(img_folder, LIGHT_MASK)).convert_alpha()
        self.light_mask = pg.transform.scale(self.light_mask, LIGHT_RADIUS)
        self.light_rect = self.light_mask.get_rect()

        #Sound loading
        pg.mixer.music.load(path.join(music_folder, BG_MUSIC))
        self.effects_sounds = {}
        for type in EFFECTS_SOUNDS:
            s = pg.mixer.Sound(path.join(snd_folder, EFFECTS_SOUNDS[type]))
            s.set_volume(0.05)
            self.effects_sounds[type] = s

        self.weapon_sounds = {}
        for weapon in WEAPON_SOUNDS:
            self.weapon_sounds[weapon] = []
            for snd in WEAPON_SOUNDS[weapon]:
                s = pg.mixer.Sound(path.join(snd_folder, snd))
                s.set_volume(0.1)
                self.weapon_sounds[weapon].append(s)


        self.zombie_moan_sounds = []
        for snd in ZOMBIE_MOAN_SOUNDS:
            s = pg.mixer.Sound(path.join(snd_folder, snd))
            s.set_volume(0.2)
            self.zombie_moan_sounds.append(s)
        self.player_hit_sounds = []
        for snd in PLAYER_HIT_SOUNDS:
            s = pg.mixer.Sound(path.join(snd_folder, snd))
            s.set_volume(0.5)
            self.player_hit_sounds.append(s)
        self.zombie_hit_sounds = []
        for snd in ZOMBIE_HIT_SOUNDS:
            s = pg.mixer.Sound(path.join(snd_folder, snd))
            s.set_volume(0.2)
            self.zombie_hit_sounds.append(s)

    def new(self):
        #initialize all variables and do all the setup for a new game
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.walls = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.items = pg.sprite.Group()

        self.map = TiledMap(path.join(self.map_folder, LEVELS[self.current_level]))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()

        #total zombies loaded
        self.zombies_loaded = 0

        #use enumerate to get the index value along with the data
        #the index value from the data file will be stored in row, and will be used as our 'y' value on the map
        #then, the index value from the data stored in 'tiles' will be stored in 'col', which will be used as our 'x' value on the map
        #for row, tiles in enumerate(self.map.data):
        #    for col, tile in enumerate(tiles):
        #        #if txt file has a '1' at a specific row,col coordinate, spawn a wall
        #        if tile == '1':
        #            Wall(self, col, row)
        #        if tile == 'M':
        #            Mob(self, col, row)
        #        if tile == 'P':
        #            self.player = Player(self, col, row)
        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width / 2, tile_object.y + tile_object.height / 2)
            if tile_object.name == 'player':
                self.player = Player(self, obj_center.x, obj_center.y)
            elif tile_object.name == 'zombie':
                Mob(self, obj_center.x, obj_center.y)
                self.zombies_loaded += 1
            elif tile_object.name == 'wall':
                Obstacle(self, tile_object.x, tile_object.y,
                        tile_object.width, tile_object.height)
            elif tile_object.name in ['health', 'shotgun']:
                Item(self, obj_center, tile_object.name)

        self.camera = Camera(self.map.width, self.map.height)
        self.draw_debug = False
        self.paused = False
        self.night = False
        self.effects_sounds['level_start'].play()

    def run(self):
        #game loop
        self.playing = True
        pg.mixer.music.play(loops=-1)
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            #Check to see if paused to run updates
            if not self.paused:
                self.update()
            self.draw()
            if self.player.kills >= self.zombies_loaded:
            #if self.player.kills >= 2:
                self.current_level += 1
                if self.current_level == 2:
                    self.current_level = 0
                self.load_data()
                break

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        #the update portion of the game loop

        self.all_sprites.update()
        self.camera.update(self.player)

        #game over?
        if len(self.mobs) == 0:
            self.playing = False

        #player hits items
        hits = pg.sprite.spritecollide(self.player, self.items, False)
        for hit in hits:
            if hit.type == 'health' and self.player.health < PLAYER_HEALTH:
                hit.kill()
                self.effects_sounds['health_up'].play()
                self.player.add_health(HEALTH_PACK_AMOUNT)
            if hit.type == 'shotgun':
                self.add_item = True
                for i in range(0, len(self.weapon_list)):
                    if self.weapon_list[i] == hit.type:
                        self.add_item = False
                if self.add_item == True:
                    self.weapon_list.append(hit.type)
                    hit.kill()
                    self.effects_sounds['gun_pickup'].play()




        #mobs hit player
        hits = pg.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
        for hit in hits:
            if random() < 0.7:
                choice(self.player_hit_sounds).play()
            self.player.health -= MOB_DAMAGE
            hit.vel = vec(0,0)
            if self.player.health <= 0:
                self.playing = False

        #if player gets hit, knock back to prevent continual collisions
        if hits:
            self.player.hit()
            self.player.pos += vec(MOB_KNOCKBACK, 0).rotate(-hits[0].rot)


        #bullets hit mobs
        hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, False)

        #each key of the dictionary 'hits' is a mob that got hit
        #we need to multiply by the number of bullets that hit it in order to calculate total damage done
        for mob in hits:
            #make mob blink when damaged
            mob.hit()
            #hit.health -= WEAPONS[self.player.weapon]['damage'] * len(hits[hit])
            for bullet in hits[mob]:
                #first check to see if weapon is a rifle, which shoots stronger bullets which
                #are capable of passing through a mob and striking another mob
                if self.player.weapon == 'rifle' or self.player.weapon == 'automatic rifle':
                    if choice(RIFLE_BULLET_STRENGTH) == 0:
                        bullet.kill()
                else:
                    bullet.kill()
                mob.health -= bullet.damage
            mob.vel = vec(0, 0)

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def render_fog(self):
        #draw the light mask (gradient) onto the fog image
        self.fog.fill(NIGHT_COLOR)
        self.light_rect.center = self.camera.apply(self.player).center
        self.fog.blit(self.light_mask, self.light_rect)
        self.screen.blit(self.fog, (0,0), special_flags=pg.BLEND_MULT)

    def draw(self):
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        #self.screen.fill(BGCOLOR)
        #draw tiled map
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        #self.draw_grid()
        for sprite in self.all_sprites:
            if isinstance(sprite, Mob):
                sprite.draw_health()
            self.screen.blit(sprite.image, self.camera.apply(sprite))
            if self.draw_debug:
                pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(sprite.hit_rect), 1)
        if self.draw_debug:
            for wall in self.walls:
                pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(wall.rect), 1)

        #below draws the hit rect around the player
        #pg.draw.rect(self.screen, WHITE, self.player.hit_rect, 2)

        if self.night:
            self.render_fog()

        #HUD functions
        #Draw Health
        draw_player_health(self.screen, 10, 10, self.player.health / PLAYER_HEALTH)
        #Draw Weapon
        self.draw_text(self.player.weapon, self.title_font, 20, WHITE, 10, 35, align='nw')
        #Draw Level
        self.draw_text("Level " + str(self.current_level + 1), self.title_font, 20, WHITE, WIDTH / 2, 15, align='center')
        #Draw Score
        self.draw_text(str(self.score), self.title_font, 20, WHITE, WIDTH / 2, 35, align='center')
        #Draw Kills
        self.draw_text('Kills', self.title_font, 25, WHITE, WIDTH - 80, 10, align='nw')
        self.draw_text(str(self.player.kills) + '/' + str(self.zombies_loaded), self.title_font, 25, WHITE, WIDTH - 80, 35, align='nw')

        if self.paused:
            self.screen.blit(self.dim_screen, (0, 0))
            self.draw_text("Paused", self.title_font, 105, RED, WIDTH / 2, HEIGHT / 2, align='center')
        pg.display.flip()

    def events(self):
        #catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_h:
                    self.draw_debug = not self.draw_debug
                if event.key == pg.K_p:
                    self.paused = not self.paused
                if event.key == pg.K_q:
                    self.weapon_index += 1
                    if self.weapon_index > (len(self.weapon_list) - 1):
                        self.weapon_index = 0
                    self.player.weapon = self.weapon_list[self.weapon_index]
                if event.key == pg.K_n:
                    self.night = not self.night



    def show_start_screen(self):
        pass

    def show_go_screen(self):
        self.screen.fill(BLACK)
        self.draw_text("GAME OVER", self.title_font, 100, RED,
                       WIDTH / 2, HEIGHT / 2, align='center')
        self.draw_text("Press a key to start", self.title_font,
                       75, WHITE, WIDTH / 2, HEIGHT * 3/4, align="center")
        pg.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        pg.event.wait()
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    waiting = False
                    self.quit()
                if event.type == pg.KEYUP:
                    waiting = False

#create the game object
g = Game()
g.show_start_screen()
while True:
    g.new()
    g.run()
    g.show_go_screen()
