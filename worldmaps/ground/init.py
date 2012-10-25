#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from engine.gameobjects.teleports import *
from engine.gameobjects.units import *
from engine.gameobjects.misc import *


def main(self):
    if not self.loaded:
        print('Generating world, this can take a while...')
        print('\t Creating teleports...')
        self.create_item(200, GetTeleport(Cave, 'underground'))
        
        print('\t Creating decorartions...')
        self.create_item(1000, Stone)
        self.create_item(500, Mushroom)
        self.create_item(1000, Plant)
        self.create_item(7000, Flower)
        self.create_item(300, WaterFlower) 
        self.create_item(200, BigWaterFlower) 
        self.create_item(10000, AloneTree)
        self.create_item(1000, AloneBush)
        self.create_item(100, WindMill)
        
        
        print('\t Creating monsters...')
        self.create_object(100, Bat)
        self.create_object(500, Zombie)
        self.create_object(100, Lych)
        self.create_object(100, Ghast)
        self.create_object(30, Cat)

