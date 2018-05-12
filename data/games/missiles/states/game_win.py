import pygame as pg

from data.components.state_machine import _State
from data.core.tools import scaled_mouse_pos
from data.core import constants as prog_constants
from data.components.labels import Label, ButtonGroup
from data.components.special_buttons import NeonButton
from .. import constants


class GameWin(_State):
    def __init__(self, controller):
        super(GameWin, self).__init__(controller)
        font = prog_constants.FONTS["Fixedsys500c"]
        color = constants.LOW_LIGHT_GREEN
        sr = constants.SCREEN_RECT
        self.labels = [
                    Label(font, 48, "Congratulations", color,
                                {"midtop": (sr.centerx, 200)}),
                    Label(font, 48, "Your cities are saved", color,
                                {"midtop": (sr.centerx, 300)})]
        self.buttons = ButtonGroup()
        NeonButton((373, 630), "OK", 32, self.to_title,
                    None, self.buttons)

    def to_title(self, *args):
        self.done = True
        self.next = "TITLE"
        self.player.clear_save()

    def startup(self, persistent):
        self.persist = persistent
        self.player = self.persist["player"]

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
