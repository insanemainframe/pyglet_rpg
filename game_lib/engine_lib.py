#!/usr/bin/env python
# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractproperty
from sys import path
path.append('../')


from game_lib.math_lib import *
from game_lib.map_lib import *
from game_lib import game


from config import *
from logger import ENGINELOG as LOG

class UnknownAction(Exception):
    pass


class ActionDenied(Exception):
    pass

#####################################################################
class GameObject:
    __metaclass__ = ABCMeta
    @abstractproperty
    def fragile():
        ""
    @abstractproperty
    def radius():
        ""
    @abstractproperty
    def crossing():
        ""
    @abstractproperty
    def guided():
        ""

#####################################################################
class MapObserver(MapTools):
    "класс объекта видящего карту"
    prev_looked = set()
    prev_observed = set()
    
    def look(self):
        "возвращает список координат видимых клеток из позиции position, с координаами относительно начала карты"
        position = self.position
        rad = self.look_size
        I,J = (position/TILESIZE).get()
        #
        new_updates = {}
        #
        observed = set()
        looked = set()
        for i in xrange(I-rad, I+rad):
            for j in xrange(J-rad, J+rad):
                diff = hypot(I-i,J-j) - rad
                if diff<0:
                    i,j = self.resize(i), self.resize(j)
                    try:
                        tile_type = game.world.map[i][j]
                    except IndexError, excp:
                        pass
                    else:
                        looked.add((Point(i,j), tile_type))
                        observed.add((i,j))
                        if (i,j) in game.updates:
                            for uid, (name, position, vector, action, args) in game.updates[(i,j)]:
                                if action=='move' and name==self.name:
                                    args = 'self'
                                new_updates[uid] = (name, position, vector, action, args)

        new_looked = looked - self.prev_looked
        self.prev_looked = looked
        self.prev_observed = observed
        return new_looked, observed, new_updates
    
    def get_observed(self):
        pass    

#####################################################################
class Movable:
    "класс движущихся объектов"
    def __init__(self, position, speed):
        self.vector  = NullPoint
        self.speed = speed
        self.position = position
        self.move_vector = NullPoint
        self.prev_position = Point(-1,-1)
        self.moved = False
        
    def move(self, vector=NullPoint):
        if self.moved:
            raise ActionDenied
        #если вектор на входе определен, до определяем вектор движения объекта
        if vector:
            self.vector = vector
        #если вектор движения не достиг нуля, то продолжить движение
        if self.vector:
            #проверка столкновения
            i,j = get_cross(self.position, self.vector)
            cross_tile =  game.world.map[i][j]
            
            if cross_tile in BLOCKTILES or (cross_tile in TRANSTILES and not self.crossing):
                self.vector = NullPoint
                self.move_vector = NullPoint
                if self.fragile:
                    self.REMOVE = True
            else:
                part = self.speed / abs(self.vector) # доля пройденного пути в векторе
                move_vector = self.vector * part if part<1 else self.vector
                self.vector = self.vector - move_vector
                self.move_vector = move_vector
        else:
            self.move_vector = self.vector
        self.prev_position = self.position
        self.position+=self.move_vector
        self.moved = True
        #name, position, vector, action, args
        return self.name, self.prev_position, self.move_vector, 'move', self.tilename
    
    def complete_round(self):
        self.moved = False
#####################################################################
class Striker:
    def __init__(self):
        self.striked = False
    
    def strike_ball(self, vector):
        if self.striked:
            raise ActionDenied
        else:
            ball_name = 'ball%s' % game.ball_counter
            game.ball_counter+=1
            ball = Ball(ball_name, self.position, vector, self.name)
            game.new_object(ball)
            self.striked = True
    
    def complete_round(self):
        self.striked = False
        
        
    
#####################################################################
class Player(Movable, MapObserver, Striker):
    "класс игрока"
    tilename = 'player'
    mortal = False
    human = True
    fragile = False
    crossing = False
    radius = TILESIZE/2
    guided = True
    prev_looked = set()
    alive = True
    striker = False
    
    def __init__(self, name, player_position, look_size):
        Movable.__init__(self, player_position, PLAYERSPEED)
        Striker.__init__(self)
        self.name = name
        self.look_size = look_size
    
    def go(self, vector):
        #self.steps.step(self.position)
        return self.move(vector)
    
    def respawn(self):
        new_position = game.choice_position()
        vector = new_position - self.position
        self.position = new_position
        update = (self.name, self.prev_position, NullPoint, 'remove')
        message = 'respawn', self.position
        return message, update
    
    def complete_round(self):
        Movable.complete_round(self)
        Striker.complete_round(self)


#####################################################################        
class Ball(Movable, MapObserver):
    "класс снаряда"
    crossing = True
    tilename = 'ball'
    mortal = True
    human = False
    guided = False
    fragile = True
    radius = TILESIZE/2
    lifetime = BALLLIFETIME
    def __init__(self, name, position, direct, striker_name):
        Movable.__init__(self, position, BALLSPEED)
        self.name = name
        self.striker =  striker_name
        one_step = Point(BALLSPEED,BALLSPEED)
        self.direct = direct*(abs(one_step)/abs(direct))

                    
    def go(self):
        return self.move(self.direct)
    

#####################################################################
if __name__=='__main__':
    GameShare()
    m = Movable(Point(3000,3000), PLAYERSPEED)
















            
