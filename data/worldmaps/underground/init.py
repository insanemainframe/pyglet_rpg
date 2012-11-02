#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from engine.gameobjects.teleports import *
from engine.gameobjects.units import *
from engine.gameobjects.misc import *
from random import choice


items = [Lamp, Sceptre, HealPotion, Sword, Armor, Sceptre, SpeedPotion, Gold, Cloak]

    
def generate(self):
        print('\t Creating teleports...')
        self.create_item(200, GetTeleport(Stair,'ground'))
        self.create_item(200, GetTeleport(DeepCave, 'underground2'))
        
        print('\t Creating decorartions...')
        self.create_item(5000, Mushroom)
        self.create_item(100, WaterFlower) 
        self.create_item(5000, Stone)
        self.create_item(50, Rubble)
        self.create_item(200, Reef)

        self.create_item(200, choice(items))

        print('\t Creating monsters...')
        self.create_object(200, Bat)
        self.create_object(200, Zombie)
        self.create_object(50, Lych)
        self.create_object(50, Ghast)
        self.create_object(30, Cat)
