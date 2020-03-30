import pygame as pg
from random import uniform, choice, randint, random
from settings import *
from tilemap import collide_hit_rect, collide_item_hit_rect
import pytweening as tween
from itertools import chain, cycle
vec = pg.math.Vector2

def collide_with_walls(sprite, group, dir):
    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y

def collide_with_water(sprite, group, dir):
    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            sprite.vel.x = sprite.vel.x / 2
    if dir == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            sprite.vel.y = sprite.vel.y / 2

def collide_with_trees(sprite, group, dir):
    if dir == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_item_hit_rect)
        if hits:
            if hits[0].hit_rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].hit_rect.left - sprite.hit_rect.width / 2
            if hits[0].hit_rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].hit_rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if dir == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_item_hit_rect)
        if hits:
            if hits[0].hit_rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].hit_rect.top - sprite.hit_rect.height / 2
            if hits[0].hit_rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].hit_rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y


def collide_with_portal(sprite, group):
    hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
    if hits:
        sprite.game._next_level(sprite.game.current_level, hits[0].to_level)


class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        pg.key.set_repeat(0, 500)
        self._layer = PLAYER_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.player_img
        self.rect = self.image.get_rect()
        #set rect x & y in player and mob so that collisions dont happen upon load
        self.rect.center = (x, y)
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.rot = 90 #0: pointing to the right at 0 degrees
        self.last_shot = 0
        self.health = PLAYER_HEALTH
        self.kills = 0
        self.weapon = self.game.weapon_list[self.game.weapon_index]
        self.damaged = False
        self.display = 'player'
        #self.inventory = self.game.player_inventory

    def get_keys(self):
        #check every update

        self.rot_speed = 0 #normally not rotating
        self.vel = vec(0, 0)
        keys = pg.key.get_pressed()
        #we're rotating, so keys don't move the player in direction, they spid player
        if keys[pg.K_a]:
            self.rot_speed = PLAYER_ROT_SPEED #spin left
        if keys[pg.K_d]:
            self.rot_speed = -PLAYER_ROT_SPEED #spin right
        if keys[pg.K_UP] or keys[pg.K_w]:
            self.vel = vec(PLAYER_SPEED, 0).rotate(-self.rot) #walk forward
        if keys[pg.K_DOWN] or keys[pg.K_s]:
            self.vel = vec(-PLAYER_SPEED / 2, 0).rotate(-self.rot) #walk backward
        if keys[pg.K_SPACE]:
            self.shoot()

    def add_to_inventory(self, type):
        if type in self.game.player_inventory.keys():
            self.game.player_inventory[type] += 1
        else:
            self.game.player_inventory[type] = 1

    def print_inventory(self):
        print(self.inventory)

    def shoot(self):
        now = pg.time.get_ticks()
        if now - self.last_shot > WEAPONS[self.weapon]['rate']:
            self.last_shot = now
            dir = vec(1, 0).rotate(-self.rot)
            pos = self.pos + BARREL_OFFSET.rotate(-self.rot)
            self.vel = vec(-WEAPONS[self.weapon]['kickback'], 0).rotate(-self.rot)
            for i in range(WEAPONS[self.weapon]['bullet_count']):
                spread = uniform(-WEAPONS[self.weapon]['spread'], WEAPONS[self.weapon]['spread'])
                Bullet(self.game, pos, dir.rotate(spread), WEAPONS[self.weapon]['damage'])
                snd = choice(self.game.weapon_sounds[self.weapon])
                if snd.get_num_channels() > 2:
                    snd.stop()
                snd.play()
            MuzzleFlash(self.game, pos)

    def hit(self):
        self.damaged = True
        self.damage_alpha = chain(DAMAGE_ALPHA * 4)

    def update(self):
        self.weapon_list = cycle(self.game.weapon_list)
        self.get_keys()
        self.rot = (self.rot + self.rot_speed * self.game.dt) % 360
        self.image = pg.transform.rotate(self.game.player_img, self.rot)
        if self.damaged:
            try:
                self.image.fill((255, 0, 0, next(self.damage_alpha)), special_flags=pg.BLEND_RGBA_MULT)
            except:
                self.damaged = False
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

        collide_with_water(self, self.game.water, 'x')
        collide_with_water(self, self.game.water, 'y')

        self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x
        collide_with_walls(self, self.game.walls, 'x')
        collide_with_trees(self, self.game.trees, 'x')
        self.hit_rect.centery = self.pos.y
        collide_with_walls(self, self.game.walls, 'y')
        collide_with_trees(self, self.game.trees, 'y')

        self.rect.center = self.hit_rect.center

        collide_with_portal(self, self.game.portals)
        collide_with_portal(self, self.game.portals)




    def add_health(self, amount):
        self.health += amount
        if self.health > PLAYER_HEALTH:
            self.health = PLAYER_HEALTH

class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = MOB_LAYER
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.mob_img.copy()
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = MOB_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center
        self.pos = vec(x, y)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.rect.center = self.pos
        self.rot = 0
        self.health = MOB_HEALTH
        self.speed = choice(MOB_SPEEDS)
        self.target = game.player
        self.state = 'inactive'
        self.damaged = False
        self.id = (x, y)
        self.display = 'zombie'

    def hit(self):
        self.damaged = True
        self.damage_alpha = chain(DAMAGE_ALPHA * 2)


    def avoid_mobs(self):
        for mob in self.game.mobs:
            if mob != self:
                dist = self.pos - mob.pos
                if 0 < dist.length() < AVOID_RADIUS:
                    self.acc += dist.normalize()

    def update(self):
        target_dist = self.target.pos - self.pos
        self.rot = target_dist.angle_to(vec(1, 0)) #angle to x axis
        self.image = pg.transform.rotate(self.game.mob_img, self.rot)
        if self.damaged:
            #if we shoot a zombie from a long distance (outside detect radius), the will now chase
            self.state = 'active'
            try:
                self.image.fill((0, 255, 0, next(self.damage_alpha)), special_flags=pg.BLEND_RGBA_MULT)
            except:
                self.damaged = False

        self.rect = self.image.get_rect()
        self.rect.center = self.pos

        #If a bullet passes near zombie, they will now chase
        for bullet in self.game.bullets:
            bullet_dist = self.pos - bullet.pos
            if bullet_dist.length_squared() < BULLET_DETECT_RADIUS**2:
                self.state = 'active'

        #chase only with close player proximity
        if target_dist.length_squared() < DETECT_RADIUS**2 or self.state == 'active':
            if random() < 0.002:
                choice(self.game.zombie_moan_sounds).play()
            self.state = 'active'
            self.acc = vec(1, 0).rotate(-self.rot)
            self.avoid_mobs()
            self.acc.scale_to_length(self.speed)
            self.acc += self.vel * -1 #limits acceleration and gives max speed
            self.vel += self.acc * self.game.dt
            self.pos += self.vel * self.game.dt + 0.5 * self.acc * self.game.dt ** 2
            self.hit_rect.centerx = self.pos.x
            collide_with_walls(self, self.game.walls, 'x')
            self.hit_rect.centery = self.pos.y
            collide_with_walls(self, self.game.walls, 'y')
            self.rect.center = self.hit_rect.center

        if self.health <= 0:
            choice(self.game.zombie_hit_sounds).play()
            self.kill()
            self.game.mob_killed_id[self.game.current_level].append(self.id)
            self.game.player.kills += 1
            self.game.score += 100
            #drop item
            if randint(0,5) % 5 == 0:
                Item(self.game, self.pos, 'wood')
            self.game.map_img.blit(self.game.splat, self.pos - vec(32,32))

    def draw_health(self):
        if self.health > 60:
            col = GREEN
        elif self.health > 30:
            col = YELLOW
        else:
            col = RED
        width = int(self.rect.width * self.health / MOB_HEALTH)
        self.health_bar = pg.Rect(0, 0, width, 7)
        if self.health < MOB_HEALTH:
            pg.draw.rect(self.image, col, self.health_bar)



class Bullet(pg.sprite.Sprite):
    def __init__(self, game, pos, dir, damage):
        self._layer = BULLET_LAYER
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.bullet_images[WEAPONS[game.player.weapon]['bullet_size']]
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = vec(pos)
        self.rect.center = pos
        #spread = uniform(-GUN_SPREAD, GUN_SPREAD)
        self.vel = dir * WEAPONS[game.player.weapon]['bullet_speed'] * uniform(0.9, 1.1)
        self.spawn_time = pg.time.get_ticks()
        self.damage = damage * choice(DAMAGE_VARIANCE)
        self.display = 'bullet'

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pg.sprite.spritecollideany(self, self.game.walls):
            self.kill()
        if pg.time.get_ticks() - self.spawn_time > WEAPONS[self.game.player.weapon]['bullet_lifetime']:
            self.kill()

class Wall(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self._layer = WALL_LAYER
        #make it in the sprite group so that it gets drawn
        #and wall group to hold all the wall objects
        self.groups = game.all_sprites, game.walls
        #initialize as a sprite
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.wall_img

        self.rect = self.image.get_rect()
        self.x = x
        self.y = y
        #walls are stationary so they do not need to be updated
        self.rect.x = x * TILESIZE
        self.rect.y = y * TILESIZE


class Obstacle(pg.sprite.Sprite):
    #creates invisible sprite for collisions
    def __init__(self, game, x, y, w, h):
        self._layer = WALL_LAYER
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y

class Water(pg.sprite.Sprite):
    #creates invisible sprite for collisions
    def __init__(self, game, x, y, w, h):
        self._layer = GROUND_LAYER
        self.groups = game.water
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y


class Tree(pg.sprite.Sprite):
    def __init__(self, game, pos, type):
        self._layer = WALL_LAYER
        self.groups = game.all_sprites, game.trees#, game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.tree_images[type].copy()
        self.rect = self.image.get_rect()

        #positional attributes
        self.pos = pos
        self.rot = 0
        self.rect.center = pos
        self.hit_rect = TREE_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center + vec(0,10)

        #personal attributes
        self.type = type
        self.birthday = pg.time.get_ticks()
        self.age = 0
        self.health = TREE_HEALTH
        self.display = type + ' (' + str("{:.0f}".format(self.age)) + '%)'

        #flags
        self._to_cut = False
        self._mature = False


    def get_age(self):
        self.age = (pg.time.get_ticks() - self.birthday)/1000
        if self.age >= 100:
            self.age = 100
        return(str("{:.0f}".format(self.age)) + '%')

    def update(self):
        if self.health <= 0:
            self.kill()
            #Automatically spawn at least one wood, with chances for more
            Item(self.game,self.pos, 'wood')
            if randint(0,2) % 2 == 0:
                Item(self.game,self.pos+ vec(25,0), 'wood')
            if randint(0,5) % 5 == 0:
                Item(self.game, self.pos+ vec(0,25), 'wood')
            if randint(0,10) % 10 == 0:
                Item(self.game, self.pos + vec(25,25), 'wood')
        self.image = pg.transform.rotate(self.game.tree_images[self.type], self.rot)
        self.age = (pg.time.get_ticks() - self.birthday)/1000
        if self.age >= 100:
            self.age = 100
        self.display = self.type + ' (' + str("{:.0f}".format(self.age)) + '%)'

    def draw_health(self):
        if self.health > 120:
            col = GREEN
        elif self.health > 60:
            col = YELLOW
        else:
            col = RED
        width = int(self.rect.width * self.health / TREE_HEALTH)
        self.health_bar = pg.Rect(0, 0, width, 7)
        if self.health < TREE_HEALTH:
            pg.draw.rect(self.image, col, self.health_bar)


class MuzzleFlash(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self._layer = EFFECTS_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        size = randint(20, 50)
        self.image = pg.transform.scale(choice(game.gun_flashes), (size, size))
        self.rect = self.image.get_rect()
        self.hit_rect = self.rect
        self.pos = pos
        self.rect.center = pos
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        if pg.time.get_ticks() - self.spawn_time > FLASH_DURATION:
            self.kill()

class Item(pg.sprite.Sprite):
    def __init__(self, game, pos, type):
        self._layer = ITEMS_LAYER
        self.groups = game.all_sprites, game.items
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.item_images[type]
        self.rect = self.image.get_rect()
        self.type = type
        self.display = type
        self.pos = pos
        self.rect.center = pos
        self.tween = tween.easeInOutSine
        self.step = 0
        self.dir = 1
        #create flag so item does not respawn upon map re-gen once picked up
        self.picked_up = False

        #define a hit rect that is used for collision (collide_item_hit_rect) so that the
        #player has to get closer to the item to pick it up compared to just colliding
        #with the item's rect
        self.hit_rect = ITEM_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center


    def update(self):
        #bobbing motion
        offset = BOB_RANGE * (self.tween(self.step / BOB_RANGE) - 0.5)
        self.rect.centery = self.pos.y + offset * self.dir
        self.step += BOB_SPEED
        if self.step > BOB_RANGE:
            self.step = 0
            self.dir *= -1

class Portal(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h, from_level, to_level):
        self.groups = game.portals
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.from_level = from_level
        self.to_level = to_level
        self.rect = pg.Rect(x, y, w, h)
        self.hit_rect = self.rect


#class Inventory_Item(pg.sprite.Sprite):
#    def __init__(self, game, type):
#        self._layer = ITEMS_LAYER
#        self.groups = game.inventory_items
#        pg.sprite.Sprite.__init__(self, self.groups)
#        self.game = game
#        self.image = game.inventory_images[type]
#        self.rect = self.image.get_rect()
#        self.hit_rect = self.rect
        #self.x = x
        #self.y = y

        #self.rect.x = x #* TILESIZE
        #self.rect.y = y #* TILESIZE


        #self.type = type
        #self.pos = pos
        #self.rect.center = pos
        #self.tween = tween.easeInOutSine
        #self.step = 0
        #self.dir = 1
