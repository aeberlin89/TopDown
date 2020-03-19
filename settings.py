import pygame as pg
vec = pg.math.Vector2

#define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BROWN = (106, 55, 5)
CYAN = (0, 255, 255)

#game settings
WIDTH = 1024 # 16*64 || 32*32 || 64*16
HEIGHT = 768 # 16*48 || 32*24 || 64*12
FPS = 60
TITLE = "Tilemap Demo"
BGCOLOR = BROWN

TILESIZE = 64
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

WALL_IMG = 'tileGreen_39.png'

#Player Settings
PLAYER_HEALTH = 100
PLAYER_SPEED = 300
PLAYER_ROT_SPEED = 250 #in degrees per second
PLAYER_IMG = 'manBlue_gun.png'
PLAYER_HIT_RECT = pg.Rect(0, 0, 35, 35)
BARREL_OFFSET = vec(30, 10)

#Inventory Settings
WEAPON_LIST = ['pistol', 'automatic rifle']




#Weapon Settings
BULLET_IMG = 'bullet.png'
WEAPONS = {}
WEAPONS['pistol'] = {'bullet_speed': 800,
                     'bullet_lifetime': 1800,
                     'rate': 400,
                     'kickback': 0,
                     'spread': 5,
                     'damage': 20,
                     'bullet_size': 'lg',
                     'bullet_count': 1
                     }
WEAPONS['shotgun'] = {'bullet_speed': 700,
                      'bullet_lifetime': 500,
                      'rate': 800,
                      'kickback': 1000,
                      'spread': 20,
                      'damage': 10,
                      'bullet_size': 'sm',
                      'bullet_count': 12
                      }
WEAPONS['rifle'] = {'bullet_speed': 1500,
                    'bullet_lifetime': 3000,
                    'rate': 1000,
                    'kickback': 1000,
                    'spread': 2,
                    'damage': 50,
                    'bullet_size': 'lg',
                    'bullet_count': 1
                    }
WEAPONS['automatic rifle'] = {'bullet_speed': 1400,
                              'bullet_lifetime': 3000,
                              'rate': 100,
                              'kickback': 100,
                              'spread': 2,
                              'damage': 50,
                              'bullet_size': 'lg',
                              'bullet_count': 1
                              }



DAMAGE_VARIANCE = [.1, .5, .6, .6, .7, .7, .7, .8, .8, .8, .8, .9, .9, .9, .9, .9,
                   1, 1, 1, 1, 1, 1, 1, 1, 1.2, 1.2, 1.2, 1.2, 1.2,
                   1.4, 1.4, 1.4, 1.4, 1.6, 1.6, 1.6, 1.8, 1.8, 2, 10]
#list to decide if rifle bullet will keep going on collision with mob
RIFLE_BULLET_STRENGTH = [0, 0, 1, 1, 1]
BULLET_SPEED = 800
BULLET_LIFETIME = 1600
BULLET_RATE = 400
KICKBACK = 0
GUN_SPREAD = 5
BULLET_DAMAGE = 100


#Mob Settings
MOB_IMG = 'zombie1_hold.png'
MOB_SPEEDS = [75, 100, 120, 130, 150, 150, 150, 150, 150, 175, 250]
MOB_HIT_RECT = pg.Rect(0, 0, 30, 30)
MOB_HEALTH = 100
MOB_DAMAGE = 10
MOB_KNOCKBACK = 20
AVOID_RADIUS = 50
DETECT_RADIUS = 500
BULLET_DETECT_RADIUS = 200

#Effects
MUZZLE_FLASHES = ['whitePuff15.png', 'whitePuff16.png', 'whitePuff17.png',
                  'whitePuff18.png']
SPLAT = 'splat_green.png'
FLASH_DURATION = 40
DAMAGE_ALPHA = [i for i in range(0, 255, 50)]
NIGHT_COLOR = (200, 200, 200)
LIGHT_RADIUS = (200, 200)
LIGHT_MASK = 'light_350_med.png'


#Layers
WALL_LAYER = 1
PLAYER_LAYER = 2
BULLET_LAYER = 3
MOB_LAYER = 2
EFFECTS_LAYER = 4
ITEMS_LAYER = 1

#Items
ITEM_IMAGES = {'health': 'health_pack.png',
               'shotgun': 'shotgun.png'
               }
HEALTH_PACK_AMOUNT = 30
BOB_RANGE = 15
BOB_SPEED = 0.4

#Sounds
BG_MUSIC = 'espionage.ogg'
PLAYER_HIT_SOUNDS = ['pain/8.wav', 'pain/9.wav', 'pain/10.wav', 'pain/11.wav']
ZOMBIE_MOAN_SOUNDS = ['brains2.wav', 'brains3.wav', 'zombie-roar-1.wav', 'zombie-roar-2.wav',
                      'zombie-roar-3.wav', 'zombie-roar-5.wav', 'zombie-roar-6.wav', 'zombie-roar-7.wav']
ZOMBIE_HIT_SOUNDS = ['splat-15.wav']
WEAPON_SOUNDS = {'pistol': ['pistol.wav'],
                 'shotgun': ['shotgun.wav'],
                 'rifle': ['pistol.wav'],
                 'automatic rifle': ['pistol.wav']
                 }

EFFECTS_SOUNDS = {'level_start': 'level_start.wav',
                  'health_up': 'health_pack.wav',
                  'gun_pickup': 'health_pack.wav'
                  }


#Levels
LEVELS = ['tiled1.tmx', 'level2.tmx']
