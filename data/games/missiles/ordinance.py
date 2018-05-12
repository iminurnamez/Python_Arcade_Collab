from random import choice
import pygame as pg

from data.core import constants as prog_consts
from data.components.angles import get_angle, project

from . import constants


class Explosion(pg.sprite.Sprite):
    covers = {x: pg.Surface((x*2, x*2))
                for x in range(1, 51)}
    masks = {}
    for radius, img in covers.items():
        img.fill(pg.Color("black"))
        img.set_colorkey(pg.Color("black"))
        pg.draw.circle(img, pg.Color(166, 0, 33), (radius, radius), radius)
        masks[radius] = pg.mask.from_surface(img)
        img.fill(pg.Color("purple"))
        pg.draw.circle(img, pg.Color("black"), (radius, radius), radius)
        covers[radius] = img
        
    explosion_colors = [
                (166, 0, 33), (232, 0, 21), (255, 0, 3), (166, 31, 0),
                (255, 0, 0), (232, 68, 0), (255, 95, 0), (255, 98, 0),
                (232, 153, 0), (255, 188, 0), (166, 92, 0), (255, 191, 0),
                (255, 238, 191), (255, 215, 191), (255, 191, 192),
                (255, 246, 222)]

    def __init__(self, pos, max_radius, growth_rate, *groups):
        super(Explosion, self).__init__(*groups)
        self.pos = pos
        self.radius = 1
        self.max_radius = max_radius
        self.growth_rate = growth_rate
        self.increasing = True
        self.color_timer = 0
        self.color_change_frequency = 80
        self.color = choice(self.explosion_colors)
        self.get_image()
        
        
    def update(self, dt):
        self.color_timer += dt
        if self.color_timer >= self.color_change_frequency:
            self.color_timer -= self.color_change_frequency
            self.color = choice(self.explosion_colors)
        if self.increasing:
            self.radius += self.growth_rate * dt
            if self.radius >= self.max_radius:
                self.increasing = False
        else:
            self.radius -= self.growth_rate * dt
            if self.radius < 1:
                self.kill()
        self.get_image()

    def get_image(self):
        int_radius = max(1, int(self.radius))
        cover = self.covers[int_radius]
        self.image = cover.copy()
        self.image.set_colorkey(pg.Color("purple"))
        self.image.fill(self.color)
        self.image.blit(cover, (0, 0))
        self.rect = self.image.get_rect(center=self.pos)
        self.mask = self.masks[int_radius]


class Missile(pg.sprite.Sprite):
    def __init__(self, origin, target, speed, max_radius, growth_rate):
        super(Missile, self).__init__()
        self.origin = self.pos = origin
        self.angle = get_angle(origin, target)
        self.speed = speed
        self.rect = pg.Rect(0, 0, 1, 1)
        self.rect.center = self.pos
        self.max_radius = max_radius
        self.growth_rate = growth_rate
        self.points = [self.rect.center, self.rect.center]

    def explode(self, *groups):
        Explosion(self.pos, self.max_radius, self.growth_rate, *groups)
        self.kill()
        
    def update(self, dt, all_explosions, explosions, buildings):
        dist = self.speed * dt
        self.pos = project(self.pos, self.angle, dist)
        self.rect.center = self.pos
        mx, my = int(self.pos[0]), int(self.pos[1])
        if self.rect.center != self.points[-1]:
            self.points.append(self.rect.center)
        collidables = pg.sprite.Group(all_explosions, buildings)
        for target in collidables:
            if target.rect.collidepoint((mx, my)):
                x = mx - target.rect.left
                y = my - target.rect.top
                if target.mask.get_at((x, y)):
                    self.explode(all_explosions, explosions)
                    break
        else:
            if self.pos[1] >= constants.SCREEN_SIZE[1]:
                self.explode(all_explosions, explosions)

    def draw(self, surface):
        pg.draw.lines(surface, pg.Color("antiquewhite"), False, self.points)
        surface.set_at(self.points[-1], (166, 0, 33, 255))