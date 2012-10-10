#!/usr/bin/env python
# -*- coding: utf-8 -*-
from clientside.gui.window import  create_tile, create_label

from share.mathlib import Point, NullPoint
from clientside.view.objects_lib import StaticObject

from config import TILESIZE

Meta = StaticObject

        


class Corpse(StaticObject):
    tilename = 'corpse'

class Item(StaticObject):
    pass
    
class HealPotion(Item):
    tilename = 'heal_potion'

class SpeedPotion(Item):
    tilename = 'speed_potion'

class Sword(Item):
    tilename = 'sword'

class Gold(Item):
    tilename = 'gold'

class Armor(Item):
    tilename = 'armor'

class Sceptre(Item):
    tilename = 'sceptre'

class Cloak(Item):
    tilename = 'cloak'

class Cave(StaticObject):
    tilename = 'cave'

class Stair(StaticObject):
    tilename = 'stair'




class Misc(StaticObject):
    def __init__(self, name, position, number):
        StaticObject.__init__(self, name, position)
        self.number = number
    
    def draw(self):
        tilename = '%s_%s' % (self.tilename, self.number)
        return [create_tile(self.position, tilename, -1)]

class Mushroom(Misc):
    tilename = 'mushroom'

class Plant(Misc):
    tilename = 'plant'
    
class WaterFlower(Misc):
    tilename = 'water_flower'

class Stone(Misc):
    tilename = 'stone'
