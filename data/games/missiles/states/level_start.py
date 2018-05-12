import pygame as pg

from data.components.state_machine import _State
from data.core.tools import scaled_mouse_pos
from data.core import constants as prog_constants
from data.components.labels import Label, ButtonGroup
from data.components.special_buttons import NeonButton
from .. import constants
from ..tools import SmallNeonButton
from ..ui import CityIcon
from ..level import Level


class LevelStart(_State):
    def __init__(self, controller):
        super(LevelStart, self).__init__(controller)
        self.ammo_costs = {
            1: 15,
            10: 100,
            25: 225,
            50: 400,
            100: 700,
            1000: 5000}
        self.gun_costs = {
            2: 1000,
            3: 5000,
            4: 25000,
            5: 125000}
        self.dome_cost = 50000

    def startup(self, persistent):
        self.persist = persistent
        self.player = self.persist["player"]
        self.level = self.persist["level"]
        self.city_cost = 100
        self.buttons = ButtonGroup()
        self.city_button = None
        self.gun_button = None
        self.labels = []
        self.make_city_icons()
        self.make_level_labels()
        self.make_ammo_table()
        self.make_gun_button()
        self.make_city_button()
        self.make_dome_button()
        NeonButton((373, 630), "Start", 32, self.start, None, self.buttons)

    def make_city_icons(self):
        level = self.persist["level"]
        player = self.persist["player"]
        self.city_icons = []
        for city in player.cities:
            cx = city.rect.centerx
            icon = CityIcon((cx, 200), city.population,
                        city.image, city.population)
            self.city_icons.append(icon)

    def make_city_button(self):
        sr = constants.SCREEN_RECT
        color = constants.LOW_LIGHT_GREEN
        if self.city_button is not None:
            self.city_button.kill()
        open_slot = any((slot.occupant is None
                    for slot in self.level.city_slots))
        if open_slot and self.player.cash >= self.city_cost:
            self.city_button = SmallNeonButton((sr.centerx - 45, 275),
                    "${}".format(self.city_cost), 16,
                    self.add_city, None, self.buttons)

    def make_level_labels(self):
        font = prog_constants.FONTS["Fixedsys500c"]
        sr = constants.SCREEN_RECT
        color = constants.LOW_LIGHT_GREEN
        self.ammo_label = Label(font, 28, "Ammo {}".format(self.player.ammo),
                    color, {"midtop": (sr.centerx, 80)})
        self.cash_label = Label(font, 28, "${}".format(self.player.cash), color,
                    {"midtop": (sr.centerx, 50)})
        self.labels.extend([
                    self.cash_label, self.ammo_label,
                    Label(font, 48, "Level {}".format(self.level.level_num),
                                color, {"midtop": (sr.centerx, 5)}),
                    Label(font, 32, "Build City", color,
                                {"midtop": (sr.centerx, 230)}),
                    Label(font, 32, "Buy Ammo", color,
                                {"midbottom": (sr.centerx, 360)}),
                    Label(font, 32, "Buy Upgrades", color,
                                {"center": (sr.centerx, 460)})])

    def make_ammo_table(self):
        font = prog_constants.FONTS["Fixedsys500c"]
        color = constants.LOW_LIGHT_GREEN
        left, top = 198, 386
        for x in sorted(self.ammo_costs.keys()):
            b_text = "${}".format(self.ammo_costs[x])
            b = SmallNeonButton((left, top), b_text, 16, self.buy_ammo,
                        x, self.buttons)
            cx = b.rect.centerx
            self.labels.append(Label(font, 24, "{}".format(x),
                        color, {"midbottom": (cx, top)}))
            left += 110

    def make_gun_button(self):
        if self.gun_button is not None:
            self.gun_button.kill()
        self.gun_label = None
        if self.player.gun_level > 4:
            return
        font = prog_constants.FONTS["Fixedsys500c"]
        sr = constants.SCREEN_RECT
        color = constants.LOW_LIGHT_GREEN
        x = self.gun_costs[self.player.gun_level + 1]
        self.gun_label = Label(font, 24,
                    "Gun Level {}".format(self.player.gun_level + 1), color,
                    {"midbottom": (sr.centerx, 510)})
        self.gun_button = SmallNeonButton((sr.centerx - 45, 510),
                    "${}".format(x), 16, self.upgrade_gun, None, self.buttons)

    def make_dome_button(self):
        sr = constants.SCREEN_RECT
        font = prog_constants.FONTS["Fixedsys500c"]
        color = constants.LOW_LIGHT_GREEN
        offset = 100
        self.dome_label = None
        if self.player.dome:
            return
        if self.gun_label is not None:
            self.gun_label.rect.centerx = sr.centerx - offset
            self.gun_button.rect.centerx = sr.centerx - offset
        self.dome_label = Label(font, 24, "Shield Dome", color,
                    {"midbottom": (sr.centerx + offset, 510)})
        self.dome_button = SmallNeonButton((sr.centerx + offset - 45, 510),
                    "${}".format(self.dome_cost), 16, self.buy_dome, None,
                    self.buttons)

    def buy_dome(self, *args):
        if self.player.cash >= self.dome_cost:
            self.player.cash -= self.dome_cost
            self.player.dome = True
            self.dome_button.kill()
            self.dome_label = None
            self.make_gun_button()
            self.persist["level"] = Level(self.player)
            
    def buy_ammo(self, qty):
        price = self.ammo_costs[qty]
        if self.player.cash < price:
            return
        self.player.ammo += qty
        self.player.cash -= price

    def upgrade_gun(self, *args):
        price = self.gun_costs[self.player.gun_level + 1]
        if self.player.cash < price or self.player.gun_level > 4:
            return
        self.player.cash -= price
        self.player.gun_level += 1
        self.player.explosion_radius = 10 * self.player.gun_level
        self.make_gun_button()
        self.make_dome_button()

    def add_city(self, *args):
        if self.player.cash < self.city_cost:
            return

        added = self.level.add_city()
        if added:
            self.player.cash -= self.city_cost
            self.city_cost *= 2
            self.make_city_button()
            self.make_city_icons()

    def start(self, *args):
        self.done = True
        self.next = "GAME"

    def get_event(self, event, scale):
        if event.type == pg.QUIT:
            self.quit = True
        elif event.type == pg.KEYDOWN:
            if event.key == pg.K_ESCAPE:
                self.quit = True
        self.buttons.get_event(event)

    def update(self, surface, keys, current_time, dt, scale):
        pos = scaled_mouse_pos(scale)
        self.buttons.update(pos)
        ammo = "Ammo {}".format(self.player.ammo)
        if self.ammo_label and self.ammo_label.text != ammo:
            self.ammo_label.set_text(ammo)
        gun_text = "Gun Level {}".format(self.player.gun_level + 1)
        if self.gun_label and self.gun_label.text != gun_text:
            self.gun_label.set_text(gun_text)
        cash = "${}".format(self.player.cash)
        if self.cash_label.text != cash:
            self.cash_label.set_text(cash)
        self.draw(surface)

    def draw(self, surface):
        surface.fill(constants.BACKGROUND_BASE)
        for icon in self.city_icons:
            icon.draw(surface)
        self.buttons.draw(surface)
        for label in self.labels:
            label.draw(surface)
        if self.gun_label is not None:
            self.gun_label.draw(surface)
        if self.dome_label is not None:
            self.dome_label.draw(surface)