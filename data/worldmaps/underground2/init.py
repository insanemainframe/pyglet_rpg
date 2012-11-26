#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from share.logger import print_log

from engine.gameobjects.teleports import *
from engine.gameobjects.units import *
from engine.gameobjects.misc import *

from random import choice


items = [Lamp, Sceptre, HealPotion, Sword, Armor, Sceptre, SpeedPotion, Gold, Cloak]
    
def generate(self):
        print_log('\t Creating teleports...')
        self.create_item(150, GetTeleport(UpStair,'underground'))
        
        print_log('\t Creating decorartions...')
        self.create_item(10000, Stone)
        self.create_item(10000, Mushroom)
        self.create_item(200, Rubble)
        self.create_item(400, choice(items))

def init(self):     
        print_log('\t Creating monsters...')
        self.create_object(200, Bat)
        self.create_object(100, Zombie)
        self.create_object(100, Lych)
        self.create_object(100, Ghast)
        self.create_object(10, Cat)

