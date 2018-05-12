"""
This module contains some useful classes for text rendering and GUI elements,
such as buttons and text input boxes.

TODO: needs some cleaning up, consolidation, and documentation.
"""

import string
import textwrap

import pygame as pg

from data.core import tools
from .defaults import BUTTON_DEFAULTS, TEXTBOX_DEFAULTS, TEXTBOX_DEFAULTS2


__all__ = [
    "Label",
    "MultiLineLabel",
    "ButtonGroup",
    "Button",
    "TextBox",
    "Textbox2",
    "FlashingText"
]
    

LOADED_FONTS = {}


class Label(pg.sprite.Sprite):
    """
    Parent class all labels inherit from. Color arguments can use color names
    or an RGB tuple. rect_attr should be a dict with keys of pygame.Rect
    attribute names (strings) and the relevant position(s) as values.

    Creates a surface with text blitted to it (self.image) and an associated
    rectangle (self.rect). Label will have a transparent bg if
    bg is not passed to __init__.
    """
    def __init__(self, path, size, text, color, rect_attr, bg=None):
        super(Label, self).__init__()
        self.path, self.size = path, size
        if (path, size) not in LOADED_FONTS:
            LOADED_FONTS[(path, size)] = pg.font.Font(path, size)
        self.font = LOADED_FONTS[(path, size)]
        self.bg = tools.parse_color(bg)
        self.color = tools.parse_color(color)
        self.rect_attr = rect_attr
        self.set_text(text)

    def set_text(self, text):
        """
        Set the text to display.
        """
        self.text = text
        self.update_text()

    def update_text(self):
        """
        Update the surface using the current properties and text.
        """
        if self.bg:
            render_args = (self.text, True, self.color, self.bg)
        else:
            render_args = (self.text, True, self.color)
        self.image = self.font.render(*render_args)
        self.rect = self.image.get_rect(**self.rect_attr)

    def draw(self, surface):
        """
        Blit self.image to target surface.
        """
        surface.blit(self.image, self.rect)


class MultiLineLabel(object):
    """
    Creates a single surface with multiple labels blitted to it.
    """
    def __init__(self, path, size, text, color, rect_attr,
                 bg=None, char_limit=42, align="left", vert_space=0):
        attr = {"center": (0, 0)}
        lines = textwrap.wrap(text, char_limit)
        labels = [Label(path, size, line, color, attr, bg) for line in lines]
        width = max([label.rect.width for label in labels])
        spacer = vert_space*(len(lines)-1)
        height = sum([label.rect.height for label in labels])+spacer
        self.image = pg.Surface((width, height)).convert()
        self.image.set_colorkey(pg.Color("black"))
        self.image.fill(pg.Color("black"))
        self.rect = self.image.get_rect(**rect_attr)
        aligns = {"left"  : {"left": 0},
                  "center": {"centerx": self.rect.width//2},
                  "right" : {"right": self.rect.width}}
        y = 0
        for label in labels:
            label.rect = label.image.get_rect(**aligns[align])
            label.rect.top = y
            label.draw(self.image)
            y += label.rect.height+vert_space

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class ButtonGroup(pg.sprite.Group):
    """
    A sprite group to hold multiple buttons.
    """
    def get_event(self, event, *args, **kwargs):
        """
        Only passes events along to Buttons that are both active and visible.
        """
        check = (s for s in self.sprites() if s.active and s.visible)
        for s in check:
            s.get_event(event, *args, **kwargs)


class Button(pg.sprite.Sprite, tools._KwargMixin):
    _invisible = pg.Surface((1,1)).convert_alpha()
    _invisible.fill((0,0,0,0))

    def __init__(self, rect_style, *groups, **kwargs):
        super(Button, self).__init__(*groups)
        self.process_kwargs("Button", BUTTON_DEFAULTS, kwargs)
        self.rect = pg.Rect(rect_style)
        rendered = self.render_text()
        self.idle_image = self.make_image(self.fill_color, self.idle_image,
                                          rendered["text"])
        self.hover_image = self.make_image(self.hover_fill_color,
                                           self.hover_image, rendered["hover"])
        self.disable_image = self.make_image(self.disable_fill_color,
                                             self.disable_image,
                                             rendered["disable"])
        self.image = self.idle_image
        self.clicked = False
        self.hover = False

    def render_text(self):
        font, size = self.font, self.font_size
        if (font, size) not in LOADED_FONTS:
            LOADED_FONTS[font, size] = pg.font.Font(font, size)
        self.font = LOADED_FONTS[font, size]
        text = self.text and self.font.render(self.text, 1, self.text_color)
        hover = self.hover_text and self.font.render(self.hover_text, 1,
                                                     self.hover_text_color)
        disable = self.disable_text and self.font.render(self.disable_text, 1,
                                                       self.disable_text_color)
        return {"text" : text, "hover" : hover, "disable": disable}

    def make_image(self, fill, image, text):
        if not any((fill, image, text)):
            return None
        final_image = pg.Surface(self.rect.size).convert_alpha()
        final_image.fill((0,0,0,0))
        rect = final_image.get_rect()
        fill and final_image.fill(fill, rect)
        image and final_image.blit(image, rect)
        text and final_image.blit(text, text.get_rect(center=rect.center))
        return final_image

    def get_event(self, event):
        if self.active and self.visible:
            if event.type == pg.MOUSEBUTTONUP and event.button == 1:
                self.on_up_event(event)
            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                self.on_down_event(event)
            elif event.type == pg.KEYDOWN and event.key in self.bindings:
                self.on_down_event(event, True)
            elif event.type == pg.KEYUP and event.key in self.bindings:
                self.on_up_event(event, True)

    def on_up_event(self, event, onkey=False):
        if self.clicked and self.call_on_up:
            self.click_sound and self.click_sound.play()
            self.call and self.call(self.args or self.text)
        self.clicked = False

    def on_down_event(self, event, onkey=False):
        if self.hover or onkey:
            self.clicked = True
            if not self.call_on_up:
                self.click_sound and self.click_sound.play()
                self.call and self.call(self.args or self.text)

    def update(self, prescaled_mouse_pos):
        hover = self.rect.collidepoint(prescaled_mouse_pos)
        pressed = pg.key.get_pressed()
        if any(pressed[key] for key in self.bindings):
            hover = True
        if not self.visible:
            self.image = Button._invisible
        elif self.active:
            self.image = (hover and self.hover_image) or self.idle_image
            if not self.hover and hover:
                self.hover_sound and self.hover_sound.play()
            self.hover = hover
        else:
            self.image = self.disable_image or self.idle_image

    def draw(self, surface):
        surface.blit(self.image, self.rect)


class FlashingText(Label):
    def __init__(self, path, size, text, color, rect_attr, delay, *groups):
        super(FlashingText, self).__init__(path, size, text, color, rect_attr, *groups)
        self.raw_image = self.image.copy()        
        self.null_image = pg.Surface((1,1)).convert_alpha()
        self.null_image.fill((0,0,0,0))
        self.rect = self.image.get_rect(**rect_attr)
        self.blink = False
        self.timer = tools.Timer(delay)

    def update(self, now, *args):
        if self.timer.check_tick(now):
            self.blink = not self.blink
        self.image = self.raw_image if self.blink else self.null_image
    
        
class TextBox(tools._KwargMixin):
    def __init__(self, rect, **kwargs):
        super(TextBox, self).__init__()
        self.rect = pg.Rect(rect)
        self.buffer = []
        self.final = None
        self.rendered = None
        self.render_rect = None
        self.render_area = None
        self.blink = True
        self.blink_timer = 0.0
        self.accepted = string.ascii_letters+string.digits+string.punctuation+" "
        self.process_kwargs("TextBox", TEXTBOX_DEFAULTS, kwargs)
        
        if (self.font, size) not in LOADED_FONTS:
            LOADED_FONTS[(self.font, size)] = pg.font.Font(path, size)
        self.font = LOADED_FONTS[(path, size)]
        
    def get_event(self,event, mouse_pos):
        if event.type == pg.KEYDOWN and self.active:
            if event.key in (pg.K_RETURN,pg.K_KP_ENTER):
                self.execute()
            elif event.key == pg.K_BACKSPACE:
                if self.buffer:
                    self.buffer.pop()
            elif event.unicode in self.accepted:
                self.buffer.append(event.unicode)
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(mouse_pos)

    def execute(self):
        if self.command:
            self.command(self.id,self.final)
        self.active = not self.inactive_on_enter
        if self.clear_on_enter:
            self.buffer = []

    def update(self):
        new = "".join(self.buffer)
        if new != self.final:
            self.final = new
            self.rendered = self.font.render(self.final, True, self.font_color)
            self.render_rect = self.rendered.get_rect(x=self.rect.x+2,
                                                      centery=self.rect.centery)
            if self.render_rect.width > self.rect.width-6:
                offset = self.render_rect.width-(self.rect.width-6)
                self.render_area = pg.Rect(offset,0,self.rect.width-6,
                                           self.render_rect.height)
            else:
                self.render_area = self.rendered.get_rect(topleft=(0,0))
        if pg.time.get_ticks()-self.blink_timer > 200:
            self.blink = not self.blink
            self.blink_timer = pg.time.get_ticks()

    def draw(self,surface):
        outline_color = self.active_color if self.active else self.outline_color
        outline = self.rect.inflate(self.outline_width*2, self.outline_width*2)
        surface.fill(outline_color,outline)
        surface.fill(self.color,self.rect)
        if self.rendered:
            surface.blit(self.rendered,self.render_rect,self.render_area)
        if self.blink and self.active:
            curse = self.render_area.copy()
            curse.topleft = self.render_rect.topleft
            surface.fill(self.font_color,(curse.right+1,curse.y,2,curse.h))

            
class Textbox2(pg.sprite.Sprite, tools._KwargMixin):
    """
    Allows the user to type and enter text. Textboxes accept a number
    of keyword arguments to allow customization of a textbox's appearance
    and behavior. Keywords for which no value is provided will use the values
    in TEXTBOX_DEFAULTS. 
    
    ARGS
    
    rect_attr: a dict of pygame.Rect attributes used to position the textbox
                   on the screen, ex. {"midtop": (100, 100)} 
    groups: sprite groups for the textbox to be added to
    
    KWARGS
    all color args accept pygame.Color objects, RGB tuples or colorname strings
    
    active: whether the textbox should respond to events
    visible: whether the textbox should be visible on the screen
    call: callback function called on enter
              user-entered text will be passed as the sole argument
    validator: function to validate textbox input
                      called on enter
    accept: string of valid characters
    box_size: width, height of textbox in pixels
    box_image: image to be used for textbox
                          if None, a rect will be drawn instead
    fill_color: fill color of textbox, ignored if box_image is not None
    outline_color: box outline color, set equal to fill_color for no outline
    outline_width: outline thickness in pixels

    font_path: path to font file, font objects are cached to LOADED_FONTS
    font_size: font size for text to be rendered at
    text_color: color for text to be rendered ine visible
    left_margin: number of pixels to offset text by
    cursor_image: image to use for the cursor
                           if None, a cursor image will be created
    cursor_color: color for created cursor image
                         ignored if cursor_image is not None
    cursor_size: width, height of cursor
                        defaults to font_size//4, font_size
    cursor_offset: width in pixels of space between text and cursor
    cursor_blink: whether the cursor should blink
    blink_frequency: cursor blink frequency in milliseconds
                                 ignored if cursor_blink is False

    type_sound: Sound object to be played on typing a valid character
    final_sound: Sound object to be played on enter command
    invalid_sound: Sound object to be played on typing an invalid character
    clear_on_enter: whether the input buffer should be cleared on enter
    inactive_on_enter: whether to deactivate textbox on enter 
    invisible_on_enter: whether to set visible to False on enter
    bindings: dict for mapping textbox commands to keyboard keys
                  dict should have a key for each of Textbox's commands:
                      "enter": finalize text input
                      "backspace": remove the character to the left of the cursor
                      "delete": remove the character to the right of the ciursor
                      "back": move the cursor left
                      "forward": move the cursor right
                  dict values should be sequences of pygame key constants
    """
    _invisible = pg.Surface((1,1)).convert_alpha()
    _invisible.fill((0,0,0,0))

    def __init__(self, rect_attr, *groups, **kwargs):
        super(Textbox2, self).__init__(*groups)
        self.rect_attr = rect_attr
        color_args = ("text_color", "cursor_color", "fill_color", "outline_color")
        for c_arg in color_args:
            if c_arg in kwargs and kwargs[c_arg] is not None:
                 kwargs[c_arg] = _parse_color(kwargs[c_arg])
        self.process_kwargs("Textbox", TEXTBOX_DEFAULTS2, kwargs)
        if self.box_image is None:
            self.make_box_image()
        else:
            self.rect = self.box_image.get_rect(**self.rect_attr)
        self.cursor_active = True
        if self.cursor_image is None:
            if self.cursor_size is None:
                self.cursor_size = max(1, self.font_size // 4), self.font_size
            self.make_cursor_image()
        self.bound_keys = []
        for v in self.bindings.values():
            self.bound_keys.extend(list(v))
        self.commands = {
            "enter": self.enter,
            "backspace": self.backspace,
            "back": self.back,
            "forward": self.forward}

        self.buffer = ""
        self.buffer_index = 0
        self.final = None
        self.timer = 0
        self.buffer_label = Label(self.font_path, self.font_size, self.buffer,
                    self.text_color, {"midleft": (self.left_margin, self.rect.h // 2)})

    def make_box_image(self):
        self.box_image = pg.Surface(self.box_size)
        self.box_image.fill(self.fill_color)
        self.rect = self.box_image.get_rect(**self.rect_attr)
        if self.outline_color:
            pg.draw.rect(self.box_image, self.outline_color,
                              self.box_image.get_rect(), self.outline_width)

    def get_event(self, event):
        if self.active and event.type == pg.KEYDOWN:
            for command in self.bindings:
                if event.key in self.bindings[command]:
                    self.commands[command]()
            if event.unicode in self.accept and event.key not in self.bound_keys:
                head = self.buffer[:self.buffer_index]
                tail = self.buffer[self.buffer_index:]
                self.buffer = head + event.unicode + tail
                self.buffer_index += 1
                self.type_sound and self.type_sound.play()

    def update(self, dt):
        if self.cursor_blink:
            self.timer += dt
            if self.timer >= self.blink_frequency:
                self.timer -= self.blink_frequency
                self.cursor_active = not self.cursor_active
        self.buffer_label.set_text(self.buffer)
        if not self.visible:
            self.image = Textbox._invisible
        else:    
            self.make_image()

    def make_image(self):
        self.image = self.box_image.copy()
        self.buffer_label.draw(self.image)
        if self.cursor_active:
            left = self.buffer_label.rect.right + self.cursor_offset
            if self.buffer_index < len(self.buffer):
                percent = float(self.buffer_index) / len(self.buffer)
                left -= int(self.buffer_label.rect.w * (1 - percent))
            midleft = (left, self.buffer_label.rect.centery)
            rect = self.cursor_image.get_rect(midleft=midleft)
            self.image.blit(self.cursor_image, rect)

    def make_cursor_image(self):
        self.cursor_image = pg.Surface((self.cursor_size))
        self.cursor_image.fill(self.cursor_color)

    def clear(self):
        self.buffer = ""

    def enter(self):
        self.final = self.buffer
        if self.clear_on_enter:
            self.clear()
        if self.inactive_on_enter:
            self.active = False
        if self.invisible_on_enter:
            self.visible = False
        if self.call is not None:
            if self.validator is None or self.validator(self.final):
                self.call(self.final)
                self.final_sound and self.final_sound.play()
            else:
                self.invalid_sound and self.invalid_sound.play()
        else:
            self.final_sound and self.final_sound.play()

    def backspace(self):
        if self.buffer_index > 0:
            self.buffer_index -= 1
            head = self.buffer[:self.buffer_index]
            tail = self.buffer[self.buffer_index + 1:]
            self.buffer = head + tail
            self.type_sound and self.type_sound.play()
        
    def delete(self):
        head = self.buffer[:self.buffer_index + 1]
        tail = self.buffer[self.buffer_index + 2:]
        self.buffer = head + tail
        self.type_sound and self.type_sound.play()
        
    def back(self):
        if self.buffer_index > 0:
            self.buffer_index -= 1
            self.type_sound and self.type_sound.play()
        
    def forward(self):
        if self.buffer_index < len(self.buffer):
            self.buffer_index += 1
            self.type_sound and self.type_sound.play()
            
    def draw(self, surface):
        surface.blit(self.image, self.rect)
            