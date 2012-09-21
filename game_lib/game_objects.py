#!/usr/bin/env python
# -*- coding: utf-8 -*-
from game_lib.math_lib import *
from game_lib.map_lib import *
from game_lib import game
from game_lib.engine_lib import *


from config import *


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
            ball = self.strike_shell(ball_name, self.position, vector, self.name)
            game.new_object(ball)
            self.strike_counter+=self.strike_speed
            
            
    def update(self):
        if self.strike_counter>0:
            self.strike_counter -=1
    
    def complete_round(self):
        self.striked = False
    
#####################################################################
class Player(Movable, MapObserver, Striker, Guided, Respawnable, Human):
    "класс игрока"
    radius = TILESIZE/2
    prev_looked = set()
    alive = True
    object_type = 'Player'
    BLOCKTILES = ['stone', 'forest', 'ocean']
    SLOWTILES = {'water':0.5, 'bush':0.3}

    def __init__(self, name, player_position, look_size):
        GameObject.__init__(self, name)
        MapObserver.__init__(self, look_size)
        Movable.__init__(self, player_position, PLAYERSPEED)
        Striker.__init__(self,5, Ball)
        
    
    def handle_response(self):
        if not self.respawned:
            move_vector = Movable.handle_request(self)
            new_looked, observed, updates = self.look()
    
            return [('look', (move_vector, new_looked, observed, updates, []))]
        else:
            return Respawnable.handle_response(self)
    
    def ball(self, vector):
        self.strike_ball(vector)
    
    def complete_round(self):
        Movable.complete_round(self)
        Striker.complete_round(self)
    
    def update(self):
        Movable.update(self)
        Striker.update(self)
    
    def die(self):
        return None, None

##################################################################### 
from random import randrange       

class Monster(GameObject, Movable, Human, Respawnable, Stalker):
    speed = 20
    object_type = 'Player'
    radius = TILESIZE
    look_size = 10
    BLOCKTILES = ['stone', 'forest', 'ocean']
    SLOWTILES = {'water':0.5, 'bush':0.3}
    def __init__(self, name, player_position):
        GameObject.__init__(self, name)
        Movable.__init__(self, player_position, self.speed)
        Stalker.__init__(self, self.look_size)
    
    def update(self):
        direct = self.hunt()
        if direct:
            self.move(direct)
        else:
            x = randrange(-self.speed, self.speed)
            y = randrange(-self.speed, self.speed)
            direct = Point(x,y)
            self.move(direct)
        Movable.update(self)
    
    def complete_round(self):
        Movable.complete_round(self)
        
class Lych(Monster, Striker):
    def __init__(self, name, position):
        Monster.__init__(self, name, position)
        Striker.__init__(self, 10, Arrow)
    
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
    
    def complete_round(self):
        Movable.complete_round(self)
        Striker.complete_round(self)
    
#####################################################################        
class Ball(Temporary, Movable,GameObject, Fragile, Mortal):
    "класс снаряда"
    radius = TILESIZE/2
    object_type = 'Ball'
    speed = BALLSPEED
    BLOCKTILES = ['stone', 'forest']
    def __init__(self, name, position, direct, striker_name):
        GameObject.__init__(self, name)
        Movable.__init__(self, position, BALLSPEED)
        Temporary.__init__(self, BALLLIFETIME)
        self.striker =  striker_name
        one_step = Point(self.speed, self.speed)
        self.direct = direct*(abs(one_step)/abs(direct))
    
    def update(self):
        Movable.move(self, self.direct)
        Movable.update(self)
        Temporary.update(self)
                    
    def die(self):
        game.add_event(self.position, NullPoint, 'explode', [])

class Arrow(Ball):
    radius = TILESIZE/3
    object_type = 'Ball'
    speed = BALLSPEED/2
    
