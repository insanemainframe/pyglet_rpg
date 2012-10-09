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
