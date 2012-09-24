#!/usr/bin/env python
# -*- coding: utf-8 -*-
from game_lib.math_lib import *
from game_lib.map_lib import *
from game_lib import game
from game_lib.engine_lib import *


from config import TILESIZE


#####################################################################
#####################################################################
class Striker:
    def __init__(self, strike_speed, shell):
        self.strike_shell = shell
        self.strike_counter = 0
        self.strike_speed = strike_speed
    
    def strike_ball(self, vector):
        if self.strike_counter==0:
            ball_name = 'ball%s' % game.ball_counter
            game.ball_counter+=1
            ball = self.strike_shell(ball_name, self.position, vector, self.fraction)
            game.new_object(ball)
            self.strike_counter+=self.strike_speed
            
            
    def update(self):
        if self.strike_counter>0:
            self.strike_counter -=1
    
    def complete_round(self):
        self.striked = False
    
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
        Deadly.__init__(self, 50)
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
    
            return [('look', (move_vector, self.hp, new_looked, observed, updates, []))]
        else:
            return Respawnable.handle_response(self)

    
    def ball(self, vector):
        self.strike_ball(vector)
    
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
        Deadly.__init__(self, self.hp)
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
    
#####################################################################        
class Ball(Temporary, Movable,GameObject, Fragile, Mortal, DiplomacySubject):
    "класс снаряда"
    radius = TILESIZE/2
    object_type = 'Ball'
    speed = 60
    BLOCKTILES = ['stone', 'forest']
    def __init__(self, name, position, direct, fraction):
        GameObject.__init__(self, name, position)
        Movable.__init__(self, self.speed)
        Temporary.__init__(self, 10)
        Mortal.__init__(self, 2)
        DiplomacySubject.__init__(self, fraction)
        one_step = Point(self.speed, self.speed)
        self.direct = direct*(abs(one_step)/abs(direct))
        self.alive = True
        self.explode_time = 7
    
    def update(self):
        if self.alive:
            Movable.move(self, self.direct)
            Movable.update(self)
            Temporary.update(self)
        else:
            if self.explode_time>0:
                self.explode()
                self.explode_time-=1
            else:
                self.REMOVE
    
    def collission(self):
        self.alive = False
    
    def remove(self):
        return True
    
    def explode(self):
        self.add_event(self.position, NullPoint, 'explode', [])
                    


class DarkBall(Ball):
    radius = TILESIZE/3
    object_type = 'DarkBall'
    speed = 30
    
    
