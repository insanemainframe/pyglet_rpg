#!/usr/bin/env python
# -*- coding: utf-8 -*-
from engine.engine_lib import *
from items import *
from config import *

#####################################################################
class Player(Movable, MapObserver, Striker, Guided, Respawnable, Deadly, DiplomacySubject):
    "класс игрока"
    radius = TILESIZE/2
    prev_looked = set()
    object_type = 'Player'
    speed = 40
    BLOCKTILES = ['stone', 'forest', 'ocean']
    SLOWTILES = {'water':0.5, 'bush':0.3}

    def __init__(self, name, player_position, look_size):
        GameObject.__init__(self, name, player_position)
        MapObserver.__init__(self, look_size)
        Movable.__init__(self, self.speed)
        Deadly.__init__(self, Corpse, 50)
        Striker.__init__(self,2, Ball)
        DiplomacySubject.__init__(self, self.name)
        Respawnable.__init__(self, 10, 30)
        
    def handle_action(self, action, args):
        if self.alive:
            GameObject.handle_action(self, action, args)
        
    def handle_response(self):
        if not self.respawned:
            move_vector = Movable.handle_request(self)
            new_looked, observed, updates = self.look()
    
            return [('Look', (move_vector, self.hp, new_looked, observed, updates, []))]
        else:
            return Respawnable.handle_response(self)

    
    def Strike(self, vector):
        self.strike_ball(vector)
    
    def Move(self, vector):
        Movable.move(self, vector)
    
    def Look(self):
        return MapObserver.look(self)
    
    def complete_round(self):
        Movable.complete_round(self)
        Striker.complete_round(self)
    
    def update(self):
        if self.alive:
            Movable.update(self)
            Striker.update(self)
        Deadly.update(self)
    

##################################################################### 
from random import randrange       

class MetaMonster(GameObject, Movable, Deadly, Respawnable, Stalker, Mortal, DiplomacySubject):
    radius = TILESIZE
    look_size = 10
    BLOCKTILES = ['stone', 'forest', 'ocean']
    SLOWTILES = {'water':0.5, 'bush':0.3}
    def __init__(self, name, player_position, speed):
        GameObject.__init__(self, name, player_position)
        Movable.__init__(self, speed)
        Stalker.__init__(self, self.look_size)
        Deadly.__init__(self, Corpse, self.hp)
        Mortal.__init__(self, 1)
        DiplomacySubject.__init__(self, 'monsters')
        Respawnable.__init__(self, 30, 30)
    
    def update(self):
        if self.alive:
            direct = self.hunt()
            if direct:
                self.move(direct)
            else:
                x = randrange(-self.speed, self.speed)
                y = randrange(-self.speed, self.speed)
                direct = Point(x,y)
                self.move(direct)
            Movable.update(self)
        Deadly.update(self)
    
    def complete_round(self):
        Movable.complete_round(self)
    
    def die(self):
        item = HealPotion(self.position)
        game.new_object(item)
        Deadly.die(self)
    
    def collission(self):
        pass

class Monster(MetaMonster, Mortal):
    hp = 3
    object_type = 'Zombie'
    def __init__(self, name, position):
        speed = 15
        Mortal.__init__(self, 2)
        MetaMonster.__init__(self, name, position, speed)
    

class Ghast(MetaMonster, Mortal):
    hp = 20
    object_type = 'Ghast'
    speed = 10
    def __init__(self, name, position):
        Mortal.__init__(self, 2)
        MetaMonster.__init__(self, name, position, self.speed)

class Lych(Monster, Striker, DiplomacySubject):
    object_type = 'Lych'
    def __init__(self, name, position):
        Monster.__init__(self, name, position)
        Striker.__init__(self, 10, DarkBall)
        DiplomacySubject.__init__(self, 'monsters')
    
    def update(self):
        direct = self.hunt()
        if direct:
            self.strike_ball(direct)
        else:
            x = randrange(-self.speed, self.speed)
            y = randrange(-self.speed, self.speed)
            direct = Point(x,y)
            self.move(direct)
        Movable.update(self)
        Striker.update(self)
        Deadly.update(self)
    
    def complete_round(self):
        Movable.complete_round(self)
        Striker.complete_round(self)
