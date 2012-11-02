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
        self.create_item(6000, Stone)
        self.create_item(2000, Mushroom)
        self.create_item(3000, Plant)
        self.create_item(12000, Flower)
        self.create_item(600, WaterFlower) 
        self.create_item(200, BigWaterFlower) 
        self.create_item(200, Reef)
        self.create_item(10000, AloneTree)
        self.create_item(1000, AloneBush)
        self.create_item(100, WindMill)

        self.create_item(100, choice(items))

        print('\t Creating monsters...')
        self.create_object(100, Bat)
        self.create_object(700, Zombie)
        self.create_object(100, Lych)
        self.create_object(100, Ghast)
        self.create_object(50, Cat)
        
        

