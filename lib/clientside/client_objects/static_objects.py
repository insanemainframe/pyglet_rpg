#!/usr/bin/env python
# -*- coding: utf-8 -*-
from clientside.gui.window import  create_tile, create_label

from share.point import Point
from clientside.client_objects.objects_lib import *

from config import TILESIZE

Meta = StaticObject

        


class Corpse(StaticObject):
    tilename = 'corpse'

class Item(StaticObject):
    def draw(self):
        return [create_tile(self.position, self.tilename, 1, self.hovered)]
    
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

class Wood(Item):
    tilename = 'wood'

class Brick(Item):
    tilename = 'brick'







class Teleport(StaticObject):
    def draw(self):
        return [create_tile(self.position, self.tilename, -1, self.hovered)]


class Cave(Teleport):
    tilename = 'cave'

class DeepCave(Teleport):
    tilename = 'cave_deep'

class Stair(Teleport):
    tilename = 'stair'

class UpStair(Teleport):
    tilename = 'stair'

class DownCave(Teleport):
    tilename = 'cave'

class Lamp(Item):
    tilename = 'lamp'


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

class BigWaterFlower(Misc):
    tilename = 'big_water_flower'

class Reef(Misc):
    tilename = 'reef'


class Flower(Misc):
    tilename = 'flower'

class Stone(Misc):
    tilename = 'stone'

class Rubble(Misc):
    tilename = 'rubble'


class AloneBush(Misc):
    tilename = 'alone_bush'

class WindMill(Misc):
    tilename = 'windmill'


class AloneTree(Misc, Breakable):
    tilename = 'alone_tree'

class Rock(Misc, Breakable):
    tilename = 'rock'