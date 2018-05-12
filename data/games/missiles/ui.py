import pygame as pg

from data.core import constants as prog_constants
from data.components.labels import Label

from . import constants


class UI(object):
    def __init__(self, player, level):
        font = prog_constants.FONTS["Fixedsys500c"]
        self.level_label = Label(font, 16, "Level {}".format(level.level_num),
                    constants.LOW_LIGHT_GREEN, {"topleft": (0, 0)})
        self.cash_label = Label(font, 16, "${}".format(player.cash),
                    constants.LOW_LIGHT_GREEN, {"topleft": (0, 20)})
        self.ammo_label = Label(font, 16, "Ammo: {}".format(player.ammo),
                    constants.LOW_LIGHT_GREEN, {"topleft": (0, 40)})
        
    def update(self, player, level):
        self.cash_label.set_text("${}".format(player.cash))
        self.ammo_label.set_text("Ammo: {}".format(player.ammo))
        
    def draw(self, surface):
        self.level_label.draw(surface)
        self.cash_label.draw(surface)
        self.ammo_label.draw(surface)
        
        
class CityIcon(object):
    def __init__(self, midbottom, points, image, current_points=0):
        self.current_points = current_points
        self.points = points
        self.image = image
        self.rect = self.image.get_rect(midbottom=midbottom)
        self.points_label = Label(prog_constants.FONTS["Fixedsys500c"], 24,
                    "{}".format(self.current_points), constants.LOW_LIGHT_GREEN,
                    {"midtop": (midbottom[0], midbottom[1] + 4)})

    def update(self):
        text = "{}".format(self.current_points)
        if self.points_label.text != text:
            self.points_label.set_text(text)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        self.points_label.draw(surface)