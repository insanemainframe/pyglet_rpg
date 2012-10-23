#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from engine.world.meta import MetaWorld
from engine.gameobjects.teleports import *
from engine.gameobjects.units import *
from engine.gameobjects.misc import *




class Ground(MetaWorld):
    "поверхность"
    mapname = 'ground'
    def __init__(self, name, game):
        MetaWorld.__init__(self, game, name)
    
    def start(self):
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


class UnderWorld(MetaWorld):
    "подземелье"
    mapname = 'underground'
    def __init__(self, name,  game):
        MetaWorld.__init__(self, game, name)
    
    def start(self):
        if not self.loaded:
            print('\t Creating teleports...')
            self.create_item(200, GetTeleport(Stair,'ground'))
            self.create_item(200, GetTeleport(DeepCave, 'underground2'))
            
            print('\t Creating decorartions...')
            self.create_item(1000, Mushroom)
            self.create_item(100, WaterFlower) 
            self.create_item(1000, Stone)
            self.create_item(50, Rubble)
            
            print('\t Creating monsters...')
            self.create_object(200, Bat)
            self.create_object(200, Zombie)
            self.create_object(50, Lych)
            self.create_object(50, Ghast)
            self.create_object(30, Cat)

class UnderWorld2(MetaWorld):
    "подземелье"
    mapname = 'underground2'
    def __init__(self, name,  game):
        MetaWorld.__init__(self, game, name)
    
    def start(self):
        if not self.loaded:
            print('\t Creating teleports...')
            self.create_item(200, GetTeleport(UpStair,'underground'))
            
            print('\t Creating decorartions...')
            self.create_item(1000, Stone)
            self.create_item(1000, Mushroom)
            self.create_item(200, Stone)
            self.create_item(50, Rubble)
            
            print('\t Creating monsters...')
            self.create_object(200, Bat)
            self.create_object(100, Zombie)
            self.create_object(100, Lych)
            self.create_object(100, Ghast)
            self.create_object(30, Cat)

