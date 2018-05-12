import os

import pygame as pg

from data.core import tools
from data.core.constants import RENDER_SIZE, BACKGROUND_BASE
from data.core.constants import LOW_LIGHT_GREEN, HIGH_LIGHT_GREEN


SCREEN_SIZE = RENDER_SIZE
SCREEN_RECT = pg.Rect((0, 0), SCREEN_SIZE)
PATH = os.path.join(".", "data", "games", "missiles", "resources")

GFX = None # Loaded and Unloaded on startup and cleanup.
SFX = None

def load():
    """
    Load resources. Called by the game scene on startup.
    """
    global GFX
    global SFX
    if GFX is None:
        GFX = tools.load_all_gfx(os.path.join(PATH, "graphics"))
    if SFX is None:
        SFX = tools.load_all_sfx(os.path.join(PATH, "sound"))

def unload():
    """
    Unload resources. Called by the game scene on cleanup.
    """
    global GFX
    global SFX
    if GFX:
        GFX.clear()
    GFX = None
    if SFX:
        SFX.clear()
    SFX = None