#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from engine.world import MetaWorld
from engine.game_objects import *


class World(MetaWorld):
    "поверхность"
    def __init__(self, name, game):
        MetaWorld.__init__(self, game, name, 'ground')
    
    def start(self):
        self.create_item(200, GetTeleport(Cave, 'underground'))
        
        self.create_item(500, Stone)
        self.create_item(200, Mushroom)
        self.create_item(500, Plant)
        self.create_item(7000, Flower)
        self.create_item(300, WaterFlower) 
        self.create_item(200, BigWaterFlower) 
        self.create_item(300, AloneTree)
        
        self.create_object(100, Bat)
        self.create_object(500, Zombie)
        self.create_object(100, Lych)
        self.create_object(100, Ghast)
        self.create_object(30, Cat)


class UnderWorld(MetaWorld):
    "подземелье"
    def __init__(self, name,  game):
        MetaWorld.__init__(self, game, name,  'underground')
    
    def start(self):
        self.create_item(200, GetTeleport(Stair,'ground'))
        self.create_item(200, GetTeleport(DownCave, 'underground2'))
        
        self.create_item(1000, Mushroom)
        self.create_item(100, WaterFlower) 
        self.create_item(1000, Stone)
        self.create_item(50, Rubble)
        
        self.create_object(200, Bat)
        self.create_object(200, Zombie)
        self.create_object(50, Lych)
        self.create_object(50, Ghast)
        self.create_object(30, Cat)

class UnderWorld2(MetaWorld):
    "подземелье"
    def __init__(self, name,  game):
        MetaWorld.__init__(self, game, name,  'underground2')
    
    def start(self):
        self.create_item(200, GetTeleport(UpStair,'underground'))
        
        self.create_item(1000, Stone)
        self.create_item(1000, Mushroom)
        self.create_item(200, Stone)
        self.create_item(50, Rubble)
        
        self.create_object(200, Bat)
        self.create_object(100, Zombie)
        self.create_object(100, Lych)
        self.create_object(100, Ghast)
        self.create_object(30, Cat)

