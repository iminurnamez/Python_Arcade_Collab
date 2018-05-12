import pygame as pg

from data.components.state_machine import _State
from data.core.tools import scaled_mouse_pos
from data.core import constants as prog_constants
from data.components.labels import Label, ButtonGroup
from data.components.special_buttons import NeonButton

from .. import constants


class LevelFail(_State):
    def __init__(self, controller):
        super(LevelFail, self).__init__(controller)

    def startup(self, persistent):
        self.persist = persistent
        font = prog_constants.FONTS["Fixedsys500c"]
        sr = constants.SCREEN_RECT
        color = constants.LOW_LIGHT_GREEN
        level_num = self.persist["player"].level_num
        self.labels = [
                Label(font, 48, "Level {} Failed".format(level_num), color,
                            {"midtop": (sr.centerx, 5)}),
                Label(font, 32, "All your cities are", color,
                            {"midbottom": (sr.centerx, 200)}),
                Label(font, 32, "belong to dust", color,
                            {"midtop": (sr.centerx, 200)})]

        self.buttons = ButtonGroup()
        NeonButton((373, 630), "OK", 32, self.to_high_scores,
                    None, self.buttons)

    def to_high_scores(self, *args):
        self.persist["player"].clear_save()
        self.done = True
        self.next = "HIGH_SCORES"


    def get_event(self, event, scale):
        self.buttons.get_event(event)

    def update(self, surface, keys, current_time, dt, scale):
        self.buttons.update(scaled_mouse_pos(scale))
        self.draw(surface)

    def draw(self, surface):
        surface.fill(constants.BACKGROUND_BASE)
        for label in self.labels:
            label.draw(surface)
        self.buttons.draw(surface)