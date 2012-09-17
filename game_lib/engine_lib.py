#!/usr/bin/env python
# -*- coding: utf-8 -*-
from random import randrange
from collections import defaultdict
from abc import ABCMeta, abstractproperty
from sys import path
path.append('../')


from game_lib.math_lib import *
from game_lib.map_lib import *

from config import *
from logger import ENGINELOG as LOG

#####################################################################
class GameShare(World, MapTools):
    "разделяемое состоние объектов карты"
    new_objects = {}
    def __init__(self):
        cls = GameShare
        World.__init__(self)
        
        cls.steps = Steps(self.size)
        cls.players = {}
        cls.updates = defaultdict(list)
        print 'created game: world size %s' % self.size
    @staticmethod
    def add_update(name, prev_position, move_vector, tilename):
        map_position = (prev_position/TILESIZE).get()
        GameShare.updates[map_position].append((name, ( prev_position, move_vector, tilename)))
            
    
    @staticmethod
    def choice_position():
        cls = GameShare
        while 1:
            start = cls.size/2 - 7
            end = cls.size/2 + 7
            position = Point(randrange(start, end), randrange(start, end))
            i,j = position.get()
            if not cls.map[i][j] in BLOCKTILES+TRANSTILES:
                position = position*TILESIZE
                return position

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
class MapObserver(MapTools, GameShare):
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
                        tile_type = self.map[i][j]
                    except IndexError, excp:
                        pass
                    else:
                        looked.add((Point(i,j), tile_type))
                        observed.add((i,j))
                        if (i,j) in self.updates:
                            for name,(position, vector, tilename) in self.updates[(i,j)]:
                                if name==self.name:
                                    tilename = 'self'
                                new_updates[name] = (position, vector, tilename)

        new_looked = looked - self.prev_looked
        self.prev_looked = looked
        self.prev_observed = observed
        return new_looked, observed, new_updates
    
    def get_observed(self):
        pass    

#####################################################################
class Movable(GameShare):
    "класс движущихся объектов"
    def __init__(self, position, speed):
        self.vector  = Point(0,0)
        self.speed = speed
        self.position = position
        self.move_vector = Point(0,0)
        self.prev_position = Point(-1,-1)
        
    def move(self, vector=Point(0,0)):
        #если вектор на входе определен, до определяем вектор движения объекта
        if vector:
            self.vector = vector
        #если вектор движения не достиг нуля, то продолжить движение
        if self.vector:
            #проверка столкновения
            i,j = get_cross(self.position, self.vector)
            cross_tile =  self.map[i][j]
            
            if cross_tile in BLOCKTILES or (cross_tile in TRANSTILES and not self.crossing):
                self.vector = Point(0,0)
                self.move_vector = Point(0,0)
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
        
        return self.name, self.prev_position, self.move_vector, self.tilename

#####################################################################
class Player(Movable, MapObserver, GameShare):
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
        self.name = name
        self.look_size = look_size
    
    def go(self, vector):
        #self.steps.step(self.position)
        return self.move(vector)
    
    def respawn(self):
        new_position = self.choice_position()
        vector = new_position - self.position
        self.position = new_position
        return vector, self.position


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
















            
