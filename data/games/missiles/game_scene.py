import random
import collections

import pygame as pg

from data.components.state_machine import _State, StateMachine
from . import constants
from .states.title_screen import TitleScreen 
from .states.level_start import LevelStart
from .states.gameplay import Gameplay
from .states.level_win import LevelWin
from .states.level_fail import LevelFail
from .states.high_scores import HighScores
from .states.game_win import GameWin 


class Scene(_State):
    """
    This State is updated while our game is running.
    The game autodetection requires that the name of this class not be changed.
    """
    def __init__(self, controller):
        super(Scene, self).__init__(controller)
        constants.load()
        self.screen_rect = pg.Rect((0, 0), constants.RENDER_SIZE)
        machine_states = {"TITLE" : TitleScreen(self),
                          "LEVEL_START": LevelStart(self),
                          "GAME" : Gameplay(self),
                          "LEVEL_WIN": LevelWin(self),
                          "LEVEL_FAIL": LevelFail(self),
                          "HIGH_SCORES": HighScores(self),
                          "GAME_WIN": GameWin(self)}
        self.state_machine = StateMachine(True)
        self.state_machine.setup_states(machine_states)
        self.state_machine.start_state("TITLE")

    def startup(self, persistent):
        """
        Load game specific resources into constants.
        """
        constants.load()
        super(Scene, self).startup(persistent)
    
    def update(self, surface, keys, current_time, dt, scale):
        """
        Updates the game scene screen.
        """
        if self.state_machine.done:
            self.done = True
            self.next = "lobby"
        self.state_machine.update(surface, keys, current_time, dt, scale)

    def get_event(self, event, scale):
        if event.type == pg.QUIT:
            self.done = True
            self.quit = True
        self.state_machine.get_event(event, scale)

    def cleanup(self):
        """
        Unload game specific resources from constants to reclaim memory.
        """
        constants.unload()
        return super(Scene, self).cleanup()