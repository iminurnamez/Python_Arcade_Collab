import os
import json
from random import randint

import pygame as pg

from data.components.state_machine import _State
from data.core.tools import scaled_mouse_pos
from data.core import constants as prog_constants
from data.components.labels import Label, FlashingText
from .. import constants
from ..buildings import MockCity
from ..player import Player
from ..level import Level
from ..ordinance import Missile, Explosion


def load_player():
    p = os.path.join(".", "data", "games", "missiles",
                    "resources", "save.json")
    try:
        with open(p, "r") as f:
            player_dict = json.load(f)
    except IOError:
        player_dict = None
    except ValueError:
        player_dict = None
    return Player(player_dict)


class TitleScreen(_State):
    def __init__(self, controller):
        super(TitleScreen, self).__init__(controller)
        
    def startup(self, persistent):
        self.persist = persistent    
        self.labels = pg.sprite.Group()
        font = prog_constants.FONTS["Fixedsys500c"]
        sr = constants.SCREEN_RECT
        self.missiles = pg.sprite.Group()
        self.all_explosions = pg.sprite.Group()
        self.explosions = pg.sprite.Group()
        self.buildings = pg.sprite.Group()    
        
        left, bottom = 50, 500
        for x in "Missiles":
            label = Label(font, 192, x, constants.LOW_LIGHT_GREEN,
                        {"bottomleft": (left, bottom)})
            img = label.image
            damaged_label = Label(font, 192, x, (166, 0, 33),
                        {"bottomleft": (left, bottom)})
            damaged_img = damaged_label.image
            width = img.get_width()
            MockCity((left + (width//2), bottom), img, damaged_img, 
                        self.buildings)
            left += width
        self.blinker = FlashingText(font, 50, "[Press Any Key]",
                    pg.Color("white"), {"center": (sr.centerx, 625)}, 350)
        self.missile_speed = .12
        self.missile_timer = 0
        self.missile_frequency = 200

    def add_missile(self):
        origin = randint(0, constants.SCREEN_SIZE[0]), -20
        target = randint(0, constants.SCREEN_SIZE[0]), constants.SCREEN_SIZE[1] - 20
        m = Missile(origin, target, self.missile_speed, 20, .1)
        self.missiles.add(m)

    def start_game(self, *args):
        self.done = True
        self.next = "LEVEL_START"
        player = load_player()
        self.persist["player"] = player
        self.persist["level"] = Level(player)
            
    def get_event(self, event, scale):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.quit = True
            else:
                self.start_game()
        elif event.type == pg.MOUSEBUTTONUP:
            self.start_game()

    def update(self, surface, keys, current_time, dt, scale):
        self.blinker.update(current_time)
        self.missile_timer += dt
        if self.missile_timer >= self.missile_frequency:
            self.add_missile()
            self.missile_timer -= self.missile_frequency
        self.explosions.update(dt)
        self.missiles.update(dt, self.all_explosions, self.explosions, self.buildings)
        self.buildings.update(dt, self.explosions)
        
        self.draw(surface)

    def draw(self, surface):
        surface.fill(constants.BACKGROUND_BASE)
        self.buildings.draw(surface)
        for m in self.missiles:
            m.draw(surface)
        self.explosions.draw(surface)
        self.blinker.draw(surface)
