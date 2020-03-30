#Tilemap Demo
import pygame as pg
import sys
from os import path
from settings import *
from sprites import *
from tilemap import *
from hud import *
from menu import *
from itertools import cycle
import cProfile


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

#global font
#font = pg.font.Font(None, 20)


class Game:
    def __init__(self):
        pg.mixer.pre_init(44100, -16, 1, 2048)
        pg.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()

        self.game_folder = path.dirname(__file__)
        self.img_folder = path.join(self.game_folder, 'img')
        self.button_font = path.join(self.img_folder, BUTTON_FONT)
        global font
        font = pg.font.Font(self.button_font, 20)

        #use keyboard repeat function if key is held down
        #first parameter is how long the key needs to be held - in ms - to start repeating
        #second parameter is how long between each 'repeat' once repeating starts
        pg.key.set_repeat(0, 500)
        self.levels = LEVELS
        self.current_level = 'level2.tmx'
        self.weapon_list = WEAPON_LIST
        self.weapon_index = 0
        self.temp_player_rot = 90
        self.player_inventory = {}
        self.game_over = False
        self.picked_up_item_pos = {}
        self.picked_up_item_pos[self.current_level] = []
        self.mob_killed_id = {}
        self.mob_killed_id[self.current_level] = []
        self.score = 0
        self.load_data()

    def new_draw_text(self, text, color, x, y, align='nw'):
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "nw":
            text_rect.topleft = (x, y)
        elif align == "ne":
            text_rect.topright = (x, y)
        elif align == "sw":
            text_rect.bottomleft = (x, y)
        elif align == "se":
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

    def draw_text(self, text, font_name, size, color, x, y, align="nw"):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "nw":
            text_rect.topleft = (x, y)
        elif align == "ne":
            text_rect.topright = (x, y)
        elif align == "sw":
            text_rect.bottomleft = (x, y)
        elif align == "se":
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
        #self.game_folder = path.dirname(__file__)
        #self.img_folder = path.join(game_folder, 'img')
        snd_folder = path.join(self.game_folder, 'snd')
        music_folder = path.join(self.game_folder, 'music')
        self.map_folder = path.join(self.game_folder, 'maps')

        self.title_font = path.join(self.img_folder, TITLE_FONT)
        self.info_font = path.join(self.img_folder, 'Timeless.ttf')
        self.button_font = path.join(self.img_folder, BUTTON_FONT)
        #make dim screen for pausing
        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 180))

        #make inventory screen
        self.inv_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.inv_screen.fill((0,0,0,180))
        #for right now we are drawing a rectangle to look like parchment as a placeholder
        #ideally, we will use proper asset to make image to fill this rect
        pg.draw.rect(self.inv_screen, PARCHMENT, ((PARCHMENT_LEFT_EDGE, 70), (WIDTH - 400, HEIGHT - 140)))

        self.player_img = pg.image.load(path.join(self.img_folder, PLAYER_IMG)).convert_alpha()
        self.player_img = pg.transform.scale(self.player_img, (int(PLAYER_WIDTH / 1.2), int(PLAYER_HEIGHT / 1.2)))

        self.bullet_images = {}
        self.bullet_images['lg'] = pg.image.load(path.join(self.img_folder, BULLET_IMG)).convert_alpha()
        self.bullet_images['sm'] = pg.transform.scale(self.bullet_images['lg'], (10, 10))

        self.mob_img = pg.image.load(path.join(self.img_folder, MOB_IMG)).convert_alpha()
        self.mob_img = pg.transform.scale(self.mob_img, (int(MOB_WIDTH / 1.2), int(MOB_HEIGHT / 1.2)))

        self.wall_img = pg.image.load(path.join(self.img_folder, WALL_IMG)).convert_alpha()
        self.wall_img = pg.transform.scale(self.wall_img, (TILESIZE, TILESIZE))

        self.splat = pg.image.load(path.join(self.img_folder, SPLAT)).convert_alpha()
        self.splat = pg.transform.scale(self.splat, (int(TILESIZE), int(TILESIZE)))

        self.inventory_images = {}

        self.gun_flashes = []
        for img in MUZZLE_FLASHES:
            self.gun_flashes.append(pg.image.load(path.join(self.img_folder, img)).convert_alpha())
        self.item_images = {}
        for item in ITEM_IMAGES:
            self.item_images[item] = pg.image.load(path.join(self.img_folder, ITEM_IMAGES[item])).convert_alpha()
            if item in ['shotgun', 'health']:
                self.item_images[item] = pg.transform.scale(self.item_images[item], (int(TILESIZE/2), int(TILESIZE/2)))
            else:
                self.item_images[item] = pg.transform.scale(self.item_images[item], (int(TILESIZE), int(TILESIZE)))
        self.trees_list = TREES_LIST
        self.tree_images = {}
        for tree in TREE_IMAGES:
            self.tree_images[tree] = pg.image.load(path.join(self.img_folder, TREE_IMAGES[tree])).convert_alpha()
            self.tree_images[tree] = pg.transform.scale(self.tree_images[tree], (int(TILESIZE*.54), int(TILESIZE)))

        #Lighting effect
        self.fog = pg.Surface((WIDTH,HEIGHT))
        self.fog.fill(NIGHT_COLOR)
        self.light_mask = pg.image.load(path.join(self.img_folder, LIGHT_MASK)).convert_alpha()
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
        self.water = pg.sprite.Group()
        self.trees = pg.sprite.Group()
        self.portals = pg.sprite.Group()

        #create main menu
        #first create invisible container for storing menu buttons
        self.main_menu_container = MenuButtonContainer(self, 2, HEIGHT - 32, WIDTH, 30)
        #create an empty list for menu buttons. Buttons can be changed in settings
        self.main_menu_button_list = []
        #populate list with buttons from settings
        self.button_pos_x = []
        self.button_pos_y = []

        for button in MAIN_MENU_BUTTONS:
            self.main_menu_button_list.append(MenuButton(self, self.main_menu_container,
                                                         BLUE, button))
            self.main_menu_container.slots += 1
        for button in self.main_menu_button_list:
            self.button_pos_x.append((button.x, button.x + button.width))
            #since y values will be the same for all buttons, this may not be necessary
            self.button_pos_y.append((button.y, button.y + button.height))



        #if current level is loading for the first time, initialize empty list stored in dicts
        #of positions for items picked up and loaded mobs
        if not self.current_level in self.picked_up_item_pos.keys():
            self.picked_up_item_pos[self.current_level] = []
        if not self.current_level in self.mob_killed_id.keys():
            self.mob_killed_id[self.current_level] = []

        print(self.current_level)


        self.map = TiledMap(path.join(self.map_folder, self.current_level))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()

        #total zombies loaded
        self.zombies_loaded = 0

        for tile_object in self.map.tmxdata.objects:
            obj_center = vec(tile_object.x + tile_object.width / 2, tile_object.y + tile_object.height / 2)
            if tile_object.name == 'player':
                self.player = Player(self, obj_center.x, obj_center.y)
                self.player.rot = self.temp_player_rot
            elif tile_object.name == 'zombie':
                #check to see if mob has been killed in a previous visit to the level
                if not (obj_center.x, obj_center.y) in self.mob_killed_id[self.current_level]:
                    Mob(self, obj_center.x, obj_center.y)
                    self.zombies_loaded += 1
            elif tile_object.name == 'wall':
                Obstacle(self, tile_object.x, tile_object.y,
                        tile_object.width, tile_object.height)

            elif tile_object.name in self.trees_list:
                Tree(self, obj_center, tile_object.name)
                print('loaded tree')

            elif tile_object.name == 'water':
                Water(self, tile_object.x, tile_object.y,
                        tile_object.width, tile_object.height)

            elif tile_object.name in ['health', 'shotgun', 'wood', 'stone', 'knife']:
                #check to see if item has already been picked up in a previous visit to the level
                if not (obj_center) in self.picked_up_item_pos[self.current_level]:
                    Item(self, obj_center, tile_object.name)

            elif tile_object.type == 'level_portal':
                Portal(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height,
                       self.current_level, tile_object.name)
                #self._next_level(tile_object.name)

        self.camera = Camera(self.map.width, self.map.height)
        self.camera_focus = self.player
        self.draw_debug = False
        self.paused = False
        self.show_inventory = False
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
            if not self.paused and not self.show_inventory:
                self.update()
            self.draw()

            #once level portals are working, get rid of this
            #if self.player.kills >= self.zombies_loaded:
            #    self.current_level += 1
            #    if self.current_level == 2:
            #        self.current_level = 0
            #    self.load_data()
            #    break

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        #the update portion of the game loop

        self.all_sprites.update()
        self.camera.update(self.camera_focus)


        #game over?
        if self.player.health <= 0:
            self.game_over = True
            self.playing = False

        #player hits items
        hits = pg.sprite.spritecollide(self.player, self.items, False, collide_item_hit_rect)
        for hit in hits:
            if hit.type == 'health' and self.player.health < PLAYER_HEALTH:
                hit.kill()
                self.picked_up_item_pos[self.current_level].append(hit.pos)
                self.effects_sounds['health_up'].play()
                self.player.add_health(HEALTH_PACK_AMOUNT)
            elif hit.type == 'shotgun':
                self.add_item = True
                for i in range(0, len(self.weapon_list)):
                    if self.weapon_list[i] == hit.type:
                        self.add_item = False
                if self.add_item == True:
                    #self.player.add_to_inventory(hit.type)
                    self.weapon_list.append(hit.type)
                    self.picked_up_item_pos[self.current_level].append(hit.pos)
                    hit.kill()
                    self.effects_sounds['gun_pickup'].play()
            if hit.type in ['wood', 'stone', 'knife']:
                self.picked_up_item_pos[self.current_level].append(hit.pos)
                #print(self.current_level, self.picked_up_item_pos[self.current_level])
                hit.kill()
                self.effects_sounds['health_up'].play()

                self.player.add_to_inventory(hit.type)

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


        #bullets hit trees
        hits = pg.sprite.groupcollide(self.trees, self.bullets, False, False)
        for tree in hits:
            for bullet in hits[tree]:
                bullet.kill()
                tree.health -= bullet.damage

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

    def _next_level(self, from_level, to_level):
        self.current_level = to_level
        self.playing = False
        self.temp_player_rot = self.player.rot
        self.load_data()
        #self.player.rot = temp

    def display_inventory(self):
        pass

    def draw_inventory(self):
        if self.show_inventory and not self.paused:
            self.screen.blit(self.inv_screen, (0, 0))
            self.draw_text("Inventory", self.title_font, 80, RED, WIDTH / 2, HEIGHT / 5, align='center')
            index = 50
            for item in self.player_inventory:
                self.inventory_images[item] = pg.image.load(path.join(self.img_folder, ITEM_IMAGES[item])).convert_alpha()
                #draw image of inventory item
                self.inv_screen.blit(self.inventory_images[item], ((PARCHMENT_LEFT_EDGE + 10), (HEIGHT / 5) + index))
                #draw number of units of inventory item
                self.draw_text(str(self.player_inventory[item]), self.title_font, 15, BLACK, (PARCHMENT_LEFT_EDGE) + (TILESIZE),
                               (HEIGHT / 5) + index + (TILESIZE/1.2), align='center')
                #shift index for next invetory image to be drawn
                index += TILESIZE


    def draw(self):
        pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        #self.screen.fill(BGCOLOR)
        #draw tiled map
        #blit(what, where)
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))

        #for sprites
        for sprite in self.all_sprites:
            if isinstance(sprite, Mob) or isinstance(sprite, Tree):
                sprite.draw_health()
            self.screen.blit(sprite.image, self.camera.apply(sprite))

            if self.draw_debug:
                pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(sprite.hit_rect), 1)

        #for stationary obstacles drawn to map
        if self.draw_debug:
            for wall in self.walls:
                pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(wall.rect), 1)
            for water in self.water:
                pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(water.rect), 1)
            for tree in self.trees:
                pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(tree.hit_rect), 1)
            for portal in self.portals:
                pg.draw.rect(self.screen, CYAN, self.camera.apply_rect(portal.rect), 1)

        #below draws the hit rect around the player
        #pg.draw.rect(self.screen, WHITE, self.player.hit_rect, 2)

        if self.night:
            self.render_fog()

        #draw main menu
        for button in self.main_menu_button_list:
            button.draw_rect()
            #pg.draw.rect(self.screen, WHITE, button.rect, 1)

        pos = pg.mouse.get_pos()
        #print(pos)
        #print(self.button_pos_x)
        #print(self.button_pos_y)
        temp_y = self.button_pos_y[0][0]
        #since y values will be the same for all buttons, this may not be necessary

        print(pos[0])
        for numbers in self.button_pos_x:
            if (pos[1] > temp_y) and (pos[1] < temp_y + self.main_menu_container.height) and (pos[0] > numbers[0]) and (pos[0] < numbers[1]):
                #find button with matching x values

                for button in self.main_menu_button_list:
                    if numbers == (button.x, button.x + button.width):
                        button.hovered = True
                        button.background_color = GREEN
                        button.draw_rect()
                    else:
                        button.hovered = False
            else:
                for button in self.main_menu_button_list:
                    button.hovered = False





        #HUD functions
        #Draw Health
        draw_player_health(self.screen, 10, 10, self.player.health / PLAYER_HEALTH)
        #Draw Weapon
        #self.draw_text(self.player.weapon, self.title_font, 20, WHITE, 10, 35, align='nw')
        #Draw Level
        self.draw_text(self.current_level, self.title_font, 20, WHITE, WIDTH / 2, 15, align='center')
        #Draw Score
        self.new_draw_text(str(self.score), WHITE, WIDTH / 2, 35, align='center')
        #Draw Kills
        self.new_draw_text('Kills', WHITE, WIDTH - 80, 10, align='nw')
        self.new_draw_text(str(self.player.kills) + '/' + str(self.zombies_loaded), WHITE, WIDTH - 80, 35, align='nw')
        #Draw Sprite Info
        #self.new_draw_text(self.camera_focus.display, WHITE, WIDTH - 10, HEIGHT - 25, align='se')
        #self.new_draw_text(str(self.camera_focus.rect.x) + 'X' + str(self.camera_focus.rect.y), WHITE, WIDTH - 10, HEIGHT - 10, align='se')


        if self.paused and not self.show_inventory:
            self.screen.blit(self.dim_screen, (0, 0))
            self.draw_text("Paused", self.title_font, 105, RED, WIDTH / 2, HEIGHT / 2, align='center')

        self.draw_inventory()

        pg.display.flip()


    def events(self):
        #catch all events here
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()

            if event.type == pg.MOUSEBUTTONUP:
                pos = pg.mouse.get_pos()
                for sprite in self.all_sprites:
                    entity = self.camera.apply(sprite)
                    if entity.collidepoint(pos):
                        self.camera_focus = sprite

            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pass
                    #need to set the camera focus to another target upon being clicked
                    #to do so, check for collision between sprite rect and mouse position

                    pos = pg.mouse.get_pos()
                    for sprite in self.all_sprites:
                        if sprite.rect.collidepoint(pos):
                            print(sprite)
                            self.camera_focus = sprite

                    #clicked_sprite = [sprite for sprite in self.all_sprites if sprite.rect.collidepoint(pos)]
                    #self.camera_focus = clicked_sprite

                if event.button == 2:
                    #middle button pressed
                    pass
                if event.button == 3:
                    #right button pressed
                    pass
                if event.button == 4:
                    pass
                    #wheel turned forward


                    #self.camera.scroll('up', self)

                if event.button == 5:
                    pass
                    #wheel turned backward
                    #self.camera.scroll('down', self)


            if event.type == pg.KEYDOWN:
                if event.key == pg.K_x:
                    self.map_img = self.map.zoom(self.map_img, 1.1)
                    self.map_rect = self.map_img.get_rect()

                if event.key == pg.K_z:
                    self.map_img = self.map.zoom(self.map_img, 0.9)
                    self.map_rect = self.map_img.get_rect()

                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_LEFT:
                    self.camera.scroll('left', self)
                if event.key == pg.K_RIGHT:
                    self.camera.scroll('right', self)
                if event.key == pg.K_g:
                    self.camera_focus = self.player
                if event.key == pg.K_h:
                    self.draw_debug = not self.draw_debug
                if event.key == pg.K_p:
                    #show pause screen
                    #if inventory screen is up, then we go back to pause screen
                    if not self.show_inventory:
                        self.paused = not self.paused
                    elif self.show_inventory:
                        self.show_inventory = not self.show_inventory
                        self.paused = not self.paused
                if event.key == pg.K_q:
                    self.weapon_index += 1
                    if self.weapon_index > (len(self.weapon_list) - 1):
                        self.weapon_index = 0
                    self.player.weapon = self.weapon_list[self.weapon_index]
                if event.key == pg.K_n:
                    self.night = not self.night
                if event.key == pg.K_i:
                    #show inventory screen
                    #if pause screen is up, then we go to inventory screen
                    if not self.paused:
                        self.show_inventory = not self.show_inventory
                        #if self.show_inventory:
                            #self.display_inventory()
                            #self.player.print_inventory()
                    elif self.paused:
                        self.paused = not self.paused
                        self.show_inventory = not self.show_inventory
                        #self.player.print_inventory()



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
    if g.game_over:
        g.show_go_screen()
