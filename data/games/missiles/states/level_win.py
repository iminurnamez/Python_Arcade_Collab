import pygame as pg

from data.components.state_machine import _State
from data.core.tools import scaled_mouse_pos
from data.core import constants as prog_constants
from data.components.labels import Label, ButtonGroup
from data.components.special_buttons import NeonButton
from data.components.animation import Animation

from .. import constants
from ..ui import CityIcon
from ..level import Level


class LevelWin(_State):
    def __init__(self, controller):
        super(LevelWin, self).__init__(controller)

    def startup(self, persistent):
        self.persist = persistent
        self.animations = pg.sprite.Group()
        self.buttons = ButtonGroup()
        font = prog_constants.FONTS["Fixedsys500c"]
        color = constants.LOW_LIGHT_GREEN
        sr = constants.SCREEN_RECT
        NeonButton((373, 630), "Next Level", 32, self.next_level,
                    None, self.buttons)
        self.make_city_icons()
        total = sum((icon.current_points for icon in self.city_icons))
        points_text = "${}".format(total)
        self.points_label = Label(font, 32,
                    points_text, color, {"center": (sr.centerx, 200)})
        level_num = self.persist["player"].level_num
        self.title = Label(font, 48, "Level {} Complete".format(level_num),
                    color, {"midtop": (sr.centerx, 5)})

    def make_city_icons(self):
        level = self.persist["level"]
        player = self.persist["player"]
        self.city_icons = []
        for city in player.cities:
            points = 0
            if not city.damaged:
                points = city.population * 100
            cx = city.rect.centerx
            icon = CityIcon((cx, 300), points, city.image)
            self.city_icons.append(icon)
            if points:
                time_scale = points / 1000.
                dur = min(1000 + (points * time_scale), 5000)
                ani = Animation(current_points=points, duration=dur,
                            round_values=True)
                ani.start(icon)
                self.animations.add(ani)

    def next_level(self, *args):
        player = self.persist["player"]
        total = sum((icon.points for icon in self.city_icons))
        player.cash += total
        player.level_num += 1
        for city in player.cities:
            if city.damaged:
                city.kill()
            else:
                city.population += 1
        player.cities = [c for c in player.cities if not c.damaged]

        player.save()
        if player.level_num > 42:
            self.next = "GAME_WIN"
        else:
            self.next = "LEVEL_START"
            level = Level(player)
            self.persist["level"] = level
        self.done = True

    def get_event(self, event, scale):
        self.buttons.get_event(event)

    def update(self, surface, keys, current_time, dt, scale):
        self.animations.update(dt)
        total = sum((icon.current_points for icon in self.city_icons))
        points_text = "${}".format(total)
        if self.points_label.text != points_text:
            self.points_label.set_text(points_text)
        for icon in self.city_icons:
            icon.update()
        self.buttons.update(scaled_mouse_pos(scale))
        self.draw(surface)

    def draw(self, surface):
        surface.fill(constants.BACKGROUND_BASE)
        for icon in self.city_icons:
            icon.draw(surface)
        self.buttons.draw(surface)
        self.points_label.draw(surface)
        self.title.draw(surface)