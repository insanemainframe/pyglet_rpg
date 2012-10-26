#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from engine.gameobjects.teleports import *
from engine.gameobjects.units import *
from engine.gameobjects.misc import *

from random import choice


items = [Lamp, Sceptre, HealPotion, Sword, Armor, Sceptre, SpeedPotion, Gold, Cloak]
    
def main(self):
    if not self.loaded:
        print('\t Creating teleports...')
        self.create_item(200, GetTeleport(UpStair,'underground'))
        
        print('\t Creating decorartions...')
        self.create_item(1000, Stone)
        self.create_item(1000, Mushroom)
        self.create_item(200, Stone)
        self.create_item(50, Rubble)
        self.create_item(300, choice(items))
        
        print('\t Creating monsters...')
        self.create_object(200, Bat)
        self.create_object(100, Zombie)
        self.create_object(100, Lych)
        self.create_object(100, Ghast)
        self.create_object(30, Cat)

