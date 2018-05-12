import os
import json

import pygame as pg

from data.components.state_machine import _State
from data.core.tools import scaled_mouse_pos
from data.core import constants as prog_constants
from data.components.labels import Label, FlashingText, ButtonGroup, Textbox2
from data.components.special_buttons import NeonButton

from .. import constants


class HighScores(_State):
    def __init__(self, controller):
        super(HighScores, self).__init__(controller)

    def startup(self, persistent):
        self.persist = persistent
        self.labels = []
        score = self.persist["player"].cash
        current_highs = self.load_high_scores()
        if len(current_highs) < 10:
            current_highs.append(("", score))
        elif current_highs[0][1] < score:
            current_highs[0] = ("", score)
        current_highs = sorted(current_highs, key=lambda x: x[1], reverse=True)
        self.make_high_scores_table(current_highs, score)
        self.labels.append(Label(prog_constants.FONTS["Fixedsys500c"],
                    64, "High Scores", constants.LOW_LIGHT_GREEN,
                    {"midtop": (464, 20)}))
        self.buttons = ButtonGroup()
        NeonButton((373, 630), "OK", 32, self.to_title, None, self.buttons)

    def make_high_scores_table(self, high_scores, score):
        font = prog_constants.FONTS["Fixedsys500c"]
        color = constants.LOW_LIGHT_GREEN
        left1, left2, top = 350, 500, 100
        placed = False
        self.name_label = None
        self.flasher = None
        self.textbox = None
        for i, info in enumerate(high_scores):
            name, high_score = info
            name_label = Label(font, 32, name, color, {"topleft": (left1, top)})
            if high_score == score and not placed and not name:
                placed = True
                label = FlashingText(font, 32, "{}".format(high_score),
                            color, {"topleft": (left2, top)}, 500)
                self.flasher = label
                self.name_label = name_label
                self.name_index = i
                validator = lambda x: len(x) == 3
                box_size = (96, 32)
                self.textbox = Textbox2({"topleft": (left1 - 4, top + 2)},
                            call=self.enter_name, box_size=box_size,
                            validator=validator, font_path=font)
            else:
                label = Label(font, 32, "{}".format(high_score), color,
                            {"topleft": (left2, top)})

            self.labels.extend([label, name_label])
            top += 40
        self.high_scores = high_scores

    def load_high_scores(self):
        p = os.path.join(".", "data", "games", "missiles",
                    "resources", "high_scores.json")
        try:
            with open(p, "r") as f:
                return sorted(json.load(f), key=lambda x: x[1])
        except IOError:
            return []

    def save_scores(self, scores):
        p = os.path.join(".", "data", "games", "missiles",
                    "resources", "high_scores.json")
        with open(p, "w") as f:
            json.dump(scores, f)

    def to_title(self, *args):
        if self.textbox is None:
            self.save_scores(self.high_scores)
            self.done = True
            self.next = "TITLE"

    def enter_name(self, name):
        self.name_label.set_text(name)
        score = self.high_scores[self.name_index][1]
        self.high_scores[self.name_index] = name, score
        self.textbox = None

    def get_event(self, event, scale):
        if self.textbox is not None:
            self.textbox.get_event(event)
        self.buttons.get_event(event)

    def update(self, surface, keys, current_time, dt, scale):
        if self.flasher is not None:
            self.flasher.update(current_time)
        if self.textbox is not None:
            self.textbox.buffer = "".join((x.upper() for x in self.textbox.buffer))
            self.textbox.update(dt)
        self.buttons.update(scaled_mouse_pos(scale))
        self.draw(surface)

    def draw(self, surface):
        surface.fill(constants.BACKGROUND_BASE)
        for label in self.labels:
            label.draw(surface)
        if self.textbox is not None:
            self.textbox.draw(surface)
        self.buttons.draw(surface)