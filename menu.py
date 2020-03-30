from settings import *

class MenuButtonContainer:
    #rect that holds menu buttons
    #need game and screen info
    #initializing with a slot size of 1
    def __init__(self, game, x, y, w, h):
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.width = w
        self.height = h
        self.slots = 0
        self.slot_width = w / (self.slots + 1)
        self.slot_height = h
        self.slot_rows = 1
        self.slot_columns = 1


class MenuButton:
    #Button to open menu type
    #need the container the button is to be placed in as well as position info
    def __init__(self, game, container, color, text):
        self.container = container
        self.game = game
        self.font = self.game.button_font
        self.background_color = color
        self.text_color = MAIN_MENU_TEXT_COLOR
        self.text = text
        self.x = self.container.rect.x + (self.container.slots * 200)#self.container.slot_width)
        self.y = self.container.rect.y
        self.width = 200#self.container.slot_width
        self.height = self.container.slot_height
        self.surf = pg.Surface((self.width, self.height)).convert_alpha()
        self.rect = pg.Rect(self.x, self.y, self.width, self.height)
        self.hovered = False



    def draw_rect(self):
        #create a surface the size of the button that will be blitted to the screen
        #then fill the surface with the buttons color
        #then draw an outline on the edge of the surface
        #finally, blit the text to the surface
        #self.surf.fill(self.background_color)
        #self.game.screen.blit(self.surf, (self.x, self.y))
        if self.hovered:
            self.background_color = (20, 20, 180)
        elif self.hovered == False:
            self.background_color = BLUE

        pg.draw.rect(self.game.screen, self.background_color, self.rect)
        pg.draw.rect(self.game.screen, WHITE, self.rect, 2)

        #self.draw_text()
        self.text_font = pg.font.Font(self.font, 15)
        #self.game.draw_text(self.text, self.game.button_font, 20, WHITE, self.x + self.width / 2, self.y + self.height / 1.7, align='center')
        self.game.new_draw_text(self.text, WHITE, self.x + self.width / 2, self.y + self.height / 1.7, align='center')
        #self.text_surface = self.text_font.render(self.text, True, self.text_color)
        #self.text_rect = self.text_surface.get_rect()
        #self.text_rect.center = (self.x + (self.width / 2), self.y + (self.height / 2))
        #self.game.screen.blit(self.text_surface, self.text_rect)
        pass


    def draw_text(self):
        #self.text_font = pg.font.Font(self.font, 15)
        #self.text_surface = self.text_font.render(self.text, True, self.text_color)
        #self.text_rect = self.text_surface.get_rect()
        #self.text_rect.center = (self.x + (self.width / 2), self.y + (self.height / 2))
        #self.game.screen.blit(self.text_surface, self.text_rect)
        pass





class Menu:
    #Opened when correlating button is clicked
    #need the correlating button
    def __init__(self, button):
        self.button = button


class MenuList:
    #stuff in the menu
    #need the correlating menu
    pass

class SubMenu:
    #If a menu list item is clicked and needs to provide more info,
    #a new submenu opens
    #need the correlating menu list item
    pass
