import pygame as pg

from data.core.constants import GFX, FONTS
from data.components.labels import Label, Button
from . import constants


class SmallNeonButton(Button):
    """
    Neon sign style button that glows on mouseover.
    """
    width = 91
    height = 29
    
    def __init__(self, pos, text, font_size=16,
                 call=None, args=None, *groups, **kwargs):
        text = text.replace("_", " ")
        
        blank = GFX["neon_button_blank"]
        scaled = pg.transform.scale(blank,
                    (blank.get_width()//2, blank.get_height()//2))
        on_label = Label(FONTS["Fixedsys500c"], font_size, text,
                         constants.HIGH_LIGHT_GREEN, {"center": (45, 14)})
        off_label = Label(FONTS["Fixedsys500c"], font_size, text,
                          constants.LOW_LIGHT_GREEN, {"center": (45, 14)})
        on_image = scaled.subsurface((self.width, 0, self.width, self.height))
        off_image = scaled.subsurface((0, 0, self.width, self.height))
        on_label.draw(on_image)
        off_label.draw(off_image)
        rect = on_image.get_rect(topleft=pos)
        settings = {"hover_image" : on_image,
                    "idle_image"  : off_image,
                    "call"        : call,
                    "args"        : args}
        settings.update(kwargs)
        super(SmallNeonButton, self).__init__(rect, *groups, **settings)