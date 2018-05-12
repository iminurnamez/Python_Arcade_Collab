import pygame as pg

from data.components.state_machine import _State
from data.core.tools import scaled_mouse_pos
from data.core import constants as prog_constants
from .. import constants
from ..ui import UI


class Gameplay(_State):
    def __init__(self, controller):
        super(Gameplay, self).__init__(controller)

    def startup(self, persistent):
        self.persist = persistent
        self.player = self.persist["player"]
        self.level = self.persist["level"]
        self.ui = UI(self.player, self.level)

    def get_event(self,event, scale):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYUP:
            if event.key == pg.K_ESCAPE:
                self.quit = True
        self.level.get_event(event, scale)

    def update(self, surface, keys, current_time, dt, scale):
        self.level.update(dt)
        self.ui.update(self.player, self.level)
        if self.level.done:
            self.done = True
            if self.level.complete:
                self.next = "LEVEL_WIN"
            else:
                self.next = "LEVEL_FAIL"
        else:
            self.draw(surface)

    def draw(self, surface):
        self.level.draw(surface)
        self.ui.draw(surface)