#!/usr/bin/env python
# -*- coding: utf-8 -*-
from random import randrange

from sys import path
path.append('../')

from game_lib.math_lib import *
from game_lib.map_lib import World, Steps

from config import *

class GameObject:
    "разделяемое состоние объектов карты"
    created = False
    @staticmethod
    def init():
        cls = GameObject
        if not cls.created:
            cls.world =  World()
            cls.size = cls.world.size
            cls.steps = Steps(cls.size)
            cls.players = {}
            cls.new_objects = {}
            cls.object_updates = {}
            cls.created = True
            print 'created world', cls.world.size
    @staticmethod
    def init_player(name, player_position):
        cls = GameObject
        cls.players[name] = player_position
    
    def alarm(self):
        "ововестить остальных о своем появлении"
        for name, player in self.players.items():
            if name!=self.name and player.guided:
                if name==self.striker:
                    tilename = self.tilename+'_self'
                else:
                    tilename = self.tilename
                self.new_objects[name][self.name] = (self.position, tilename)
    @staticmethod
    def choice_position():
        cls = GameObject
        while 1:
            start = cls.size/2 - cls.size/10
            end = cls.size/2 + cls.size/10
            position = Point(randrange(start, end), randrange(start, end))
            i,j = position.get()
            if not cls.world.map[i][j] in BLOCKTILES:
                position = position*TILESIZE
                return position
        
        

class Movable(GameObject):
    def __init__(self, position, speed):
        self.vector  = Point(0,0)
        self.speed = speed
        self.position = position
        self.move_vector = Point(0,0)
        self.prev_position = False
        
    def move(self, vector):
        #если вектор на входе определен, до определяем вектор движения объекта
        if vector:
            self.vector = vector
        #если вектор движения не достиг нуля, то продолжить движение
        if self.vector:
            #проверка столкновения
            i,j = get_cross(self.position, self.vector)
            cross_tile =  self.world.map[i][j]
            
            if cross_tile in BLOCKTILES or (cross_tile in TRANSTILES and not self.crossing):
                self.vector = Point(0,0)
                self.move_vector = Point(0,0)
                if self.fragile:
                    del self.players[self.name]
            else:
                part = self.speed / abs(self.vector) # доля пройденного пути в векторе
                move_vector = self.vector * part if part<1 else self.vector
                self.vector = self.vector - move_vector
                self.move_vector = move_vector
        else:
            self.move_vector = self.vector
        self.prev_position = self.position
        self.position+=self.move_vector
        #оповещаем других освоем движении
        for client, update_dict in self.object_updates.items():
            if self.players[client].guided:
                self.object_updates[client][self.name] = self.move_vector

class Player(Movable):
    tilename = 'player'
    fragile = False
    crossing = False
    guided = True
    prev_looked = set()
    alive = True
    striker = False
    def __init__(self, name, player_position, look_size):
        Movable.__init__(self, player_position, PLAYERSPEED)
        self.name = name
        self.look_size = look_size
        self.new_objects[name] = {}
        self.object_updates[name] = {}
        self.alarm()

    def accept(self):
        """впервое обращение клиента, возвращает размер карты, позицию и первые тайлы"""
        looked = self.world.look(self.position, self.look_size)
        self.prev_looked = looked
        
        objects = {name:(player.position, self.tilename+'_self' if name==self.name else self.tilename)
                    for name, player in self.players.items()}
        
        steps =  [] #steps = self.steps.look(self.position, self.look_size)
        print '%s accept %s' % (self.name, self.position)
        return  self.world.size, self.position, looked, objects, []
    
    def go(self, vector=Point(0,0)):
        self.move(vector)
        self.steps.step(self.position)
        
    def look(self):
        #получаем новые видимые тайлы
        if self.prev_position == self.position:
            new_looked = [] #self.prev_looked
        else:
            looked =self.world.look(self.position, self.look_size)
            new_looked = looked - self.prev_looked
            self.prev_looked = looked
        
        #ищем новые объекты
        new_objects = {}
        for name, (position, tilename) in self.new_objects[self.name].items():
            if name!=self.name:
                new_objects[name] = (position, tilename)
        self.new_objects[self.name] = {}
        #ищем бновления объектов
        updates = self.object_updates[self.name]
        self.object_updates[self.name] = {}
        #steps
        steps = [] #self.steps.look(self.position, self.look_size)
        return self.move_vector, new_looked, new_objects, updates, steps
    
    def respawn(self):
        new_position = self.choice_position()
        for client in self.players:
            if self.players[client].guided:
                self.object_updates[client][self.name] = new_position - self.position
        self.position = new_position
        return self.position
    
    def __del__(self):
        #удаляем себя из списка объектов
        del self.new_objects[self.name]
        del self.object_updates[self.name]
        #оповещаем других игроков о выходе
        for client, update_dict in self.object_updates.items():
            self.object_updates[client][self.name] = 'remove'
        
        
class Ball(Movable, GameObject):
    crossing = True
    tilename = 'ball'
    guided = False
    fragile = True
    def __init__(self, name, position, direct, striker_name):
        Movable.__init__(self, position, BALLSPEED)
        self.lifetime = BALLLIFETIME
        self.name = name
        self.striker =  striker_name
        one_step = Point(BALLSPEED,BALLSPEED)
        self.direct = direct*(abs(one_step)/abs(direct))
        self.radius = BALLRADIUS
        #оповещаем
        self.alarm()
    
    def collision(self):
        for name, player in self.players.items():
            if player.guided and name!=self.striker:
                dist = abs(self.position-player.position)
                if dist<self.radius:
                    self.players[name].alive= False
                    print 'BOMB %s' % name
    def go(self):
        self.move(self.direct)
        self.collision()
    
    def __del__(self):
        for client, update_dict in self.object_updates.items():
            self.object_updates[client][self.name] = 'remove'
        
        
        

            
