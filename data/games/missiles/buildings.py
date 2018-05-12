import pygame as pg

from . import constants


class Building(pg.sprite.Sprite):
    def __init__(self, midbottom, *groups):
        super(Building, self).__init__(*groups)
        self.rect = self.image.get_rect(midbottom=midbottom)
        self.mask = pg.mask.from_surface(self.image)
        self.damaged = False

    def collide_with_explosion(self, explosion):
        ex, ey = explosion.pos
        x = int(ex - self.rect.x)
        y = int(ey - self.rect.y)
        if pg.sprite.collide_mask(self, explosion):
            if not self.damaged:
                self.damaged = True
                self.image = self.damaged_image.copy()
            pg.draw.circle(self.image, pg.Color(0, 0, 0, 0),
                        (x, y), int(explosion.radius))
            self.mask = pg.mask.from_surface(self.image)

    def update(self, dt, explosions):
        for e in explosions:
            self.collide_with_explosion(e)

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class City(Building):
    def __init__(self, midbottom, *groups):
        self.image = constants.GFX["city"]
        self.damaged_image = constants.GFX["city-damaged"]
        super(City, self).__init__(midbottom, *groups)
        self.population = 1

class MockCity(Building):
    def __init__(self, midbottom, image, damaged_image, *groups):
        self.image = image
        self.damaged_image = damaged_image
        
        super(MockCity, self).__init__(midbottom, *groups)


class Dome(Building):
    def __init__(self, *groups):
        self.image = self.damaged_image = self.make_image()
        super(Dome, self).__init__(
                    (constants.SCREEN_SIZE[0] // 2, constants.SCREEN_SIZE[1]),
                    *groups)

    def make_image(self):
        w, h = constants.SCREEN_SIZE
        image = pg.Surface((w, h))
        image.fill(pg.Color("black"))
        radius = (w // 2) + 10
        anchor_y = h + 180
        pg.draw.circle(image, pg.Color("antiquewhite"), (w // 2, anchor_y), radius)
        pg.draw.circle(image, pg.Color("black"), (w // 2, anchor_y + 40), radius)
        image.set_colorkey(pg.Color("black"))
        image  = image.subsurface(pg.Rect(0, h//2, w, h - (h//2)))
        return image
