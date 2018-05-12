from random import randint

import pygame as pg

from data.core.tools import scaled_mouse_pos


from . import constants
from .buildings import City, Dome
from .ordinance import Explosion, Missile


class CitySlot(object):
    def __init__(self, midbottom, occupant=None):
        self.midbottom = midbottom
        self.occupant = occupant
        

class Level(object):
    def __init__(self, player):
        self.done = False
        self.complete = False
        self.animations = pg.sprite.Group()
        self.missiles = pg.sprite.Group()
        self.explosions = pg.sprite.Group()
        self.all_explosions = pg.sprite.Group()
        self.buildings = pg.sprite.Group()
        self.player = player
        self.level_num = player.level_num
        self.num_missiles = 20 + ((self.level_num - 1) * 5)
        self.missile_speed = .04 * (1 + ((self.level_num - 1)/ 20.))
        self.missile_timer = 0
        self.missile_frequency = 1200 - (self.level_num * 25)
        spots = (464, 124, 804, 294, 634) 
        self.city_slots = [
                    CitySlot((spot, 696)) for spot in spots]
        for city in self.player.cities:
            self.buildings.add(city)
            for slot in self.city_slots:
                if slot.midbottom == city.rect.midbottom:
                    slot.occupant = city

        if self.player.dome:
            Dome(self.buildings)
                
    def get_event(self,event, scale):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                self.quit = True
        elif event.type == pg.MOUSEBUTTONUP:
            if event.button == 1:
                self.add_explosion(scaled_mouse_pos(scale, event.pos))

    def update(self, dt):
        self.animations.update(dt)
        self.missile_timer += dt
        if self.missile_timer >= self.missile_frequency:
            self.add_missile()
            self.missile_timer -= self.missile_frequency
        mouse_pos = pg.mouse.get_pos()
        self.all_explosions.update(dt)
        self.missiles.update(dt, self.all_explosions, self.explosions, self.buildings)
        self.buildings.update(dt, self.explosions)
        if not any((self.num_missiles, self.missiles, self.all_explosions)):
            self.done = True
            self.complete = True
        if all((city.damaged for city in self.player.cities)):
            self.done = True
        
    def draw(self, surface):
        surface.fill(constants.BACKGROUND_BASE)
        self.buildings.draw(surface)
        for m in self.missiles:
            m.draw(surface)
        self.all_explosions.draw(surface)        
    
    def add_city(self):
        for slot in self.city_slots:
            if slot.occupant is None:
                city = City(slot.midbottom, self.buildings)
                slot.occupant = city
                self.player.cities.append(city)
                return True
        
    def add_explosion(self, pos):
        if self.player.ammo < 1:
            return
        explosion = Explosion(pos, self.player.explosion_radius,
                    self.player.explosion_growth_rate,
                    self.all_explosions)
        constants.SFX["explosion2"].play()
        self.player.ammo -= 1
        
    def add_missile(self):
        if self.num_missiles > 0:
            origin = randint(0, constants.SCREEN_SIZE[0]), -20
            target = randint(0, constants.SCREEN_SIZE[0]), constants.SCREEN_SIZE[1] - 20
            m = Missile(origin, target, self.missile_speed, 20, .1)
            self.missiles.add(m)
            self.num_missiles -= 1
        
