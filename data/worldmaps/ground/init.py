#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from engine.gameobjects.teleports import *
from engine.gameobjects.units import *
from engine.gameobjects.misc import *
from engine.gameobjects.items import *

from random import choice


items = [Lamp, Sceptre, HealPotion, Sword, Armor, Sceptre, SpeedPotion, Gold, Cloak]


def generate(self):
        print('Generating world, this can take a while...')
        print('\t Creating teleports...')
        self.create_item(200, GetTeleport(Cave, 'underground'))
        
        print('\t Creating decorartions...')
        self.create_item(3000, Stone)
        self.create_item(2000, Mushroom)
        self.create_item(5000, Plant)
        self.create_item(20000, Flower)
        self.create_item(500, WaterFlower) 
        self.create_item(200, BigWaterFlower) 
        self.create_item(13000, AloneTree)
        self.create_item(1000, AloneBush)
        self.create_item(100, WindMill)

        self.create_item(100, choice(items))
        
def init(self):     
        print('\t Creating monsters...')
        self.create_object(100, Bat)
        self.create_object(500, Zombie)
        self.create_object(100, Lych)
        self.create_object(100, Ghast)
        self.create_object(100, Cat)

