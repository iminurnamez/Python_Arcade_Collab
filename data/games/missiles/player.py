import os
import json

from .buildings import City

class Player(object):
    def __init__(self, player_dict=None):
        if player_dict is not None:
            d = player_dict
        else:
            d = {
                "growth rate": .05,
                "cash": 500,
                "gun level": 1,
                "ammo": 0,
                "level num": 1,
                "cities": [],
                "dome": None}
        self.explosion_growth_rate = d["growth rate"]
        self.cash = d["cash"]
        self.gun_level = d["gun level"]
        self.explosion_radius = self.gun_level * 10
        self.ammo = d["ammo"]
        self.level_num = d["level num"]
        self.cities = []
        self.dome = d["dome"]
        for city_dict in d["cities"]:
            city = City(city_dict["midbottom"])
            city.population = city_dict["population"]
            self.cities.append(city)

    def save(self):
        cities = []
        for city in self.cities:
            if not city.damaged:
                info = {
                        "midbottom": city.rect.midbottom,
                        "population": city.population}
                cities.append(info)
        d = {
                "growth rate": self.explosion_growth_rate,
                "cash": self.cash,
                "gun level": self.gun_level,
                "ammo": self.ammo,
                "level num": self.level_num,
                "cities": cities,
                "dome": self.dome}
        p = os.path.join(".", "data", "games", "missiles",
                    "resources", "save.json")
        with open(p, "w") as f:
            json.dump(d, f)

    def clear_save(self):
        p = os.path.join(".", "data", "games", "missiles",
                    "resources", "save.json")
        try:
            os.remove(p)
        except:
            pass
