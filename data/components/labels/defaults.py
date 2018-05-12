import string

import pygame as pg

from data.core.constants import LOW_LIGHT_GREEN, HIGH_LIGHT_GREEN, BACKGROUND_BASE


BUTTON_DEFAULTS = {"call"               : None,
                   "args"               : None,
                   "call_on_up"         : True,
                   "font"               : None,
                   "font_size"          : 36,
                   "text"               : None,
                   "hover_text"         : None,
                   "disable_text"       : None,
                   "text_color"         : pg.Color("white"),
                   "hover_text_color"   : None,
                   "disable_text_color" : None,
                   "fill_color"         : None,
                   "hover_fill_color"   : None,
                   "disable_fill_color" : None,
                   "idle_image"         : None,
                   "hover_image"        : None,
                   "disable_image"      : None,
                   "hover_sound"        : None,
                   "click_sound"        : None,
                   "visible"            : True,
                   "active"             : True,
                   "bindings"           : ()}


TEXTBOX_DEFAULTS = {"id"                : None,
                    "command"           : None,
                    "active"            : True,
                    "color"             : pg.Color("white"),
                    "font_color"        : pg.Color("black"),
                    "outline_color"     : pg.Color("black"),
                    "outline_width"     : 2,
                    "active_color"      : pg.Color("blue"),
                    "font"              : None,
                    "clear_on_enter"    : False,
                    "inactive_on_enter" : True}


TEXTBOX_DEFAULTS2 = {
        "active": True,
        "visible": True,
        "call": None,         #call(self.final) will be called on enter
        "validator": None, #function to validate textbox input, checked on enter command
        "accept": string.ascii_letters + string.digits+ string.punctuation + " ",

        "box_size": (256, 64),
        "box_image": None,
        "fill_color": BACKGROUND_BASE,
        "outline_color": None,
        "outline_width": 2,

        "cursor_visible": True,
        "cursor_active": True,
        "cursor_image": None,
        "cursor_color": LOW_LIGHT_GREEN,
        "cursor_size": None,
        "cursor_offset": 1,
        "cursor_blink": True,
        "blink_frequency": 350,

        "text_color": LOW_LIGHT_GREEN,
        "font_path": None,
        "font_size": 32,
        "left_margin": 4,

        "type_sound": None,
        "final_sound": None,
        "invalid_sound": None,

        "visible": True,
        "active": True,
        "clear_on_enter" : True,
        "inactive_on_enter" : False,
        "invisible_on_enter": False,
        "bindings":
                {"enter": (pg.K_RETURN, pg.K_KP_ENTER),
                "backspace": (pg.K_BACKSPACE,),
                "delete": (pg.K_DELETE,),
                "back": (pg.K_LEFT,),
                "forward": (pg.K_RIGHT,)}}