#!/usr/bin/env python
# -*- coding: utf-8 -*-
from random import randrange

from math_lib import *
from map_lib import World

from config import TILESIZE, PLAYERSPEED, BLOCKTILES ,logger

class GameObject:
    "разделяемое состоние объектов карты"
    @staticmethod
    def init():
        cls = GameObject
        if not hasattr(cls,'created'):
            cls.world =  World()
            cls.size = cls.world.size
            cls.players = {}
            cls.new_objects = {}
            cls.object_updates = {}
            cls.created = True
            print 'create world', cls.world.size
    @staticmethod
    def init_player(name, player_position):
        cls = GameObject
        cls.players[name] = player_position
        

class Movable(GameObject):
    def __init__(self, position, speed):
        self.vector  = Point(0,0)
        self.speed = speed
        self.position = position
        self.move_vector = Point(0,0)
        
    def move(self, vector):
        #если вектор на входе определен, до определяем вектор движения объекта
        if vector:
            self.vector = vector

        #если вектор движения не достиг нуля, то продолжить движение
        if self.vector:
            #проверка столкновения
            i,j = get_cross(self.position, self.vector)
            cross_tile =  self.world.map[i][j]
            if cross_tile in BLOCKTILES:
                self.vector = Point(0,0)
            else:
                part = self.speed / abs(self.vector) # доля пройденного пути в векторе
                move_vector = self.vector * part if part<1 else self.vector
                self.vector = self.vector - move_vector
                self.move_vector = move_vector
        else:
            self.move_vector = self.vector
        self.position+=self.move_vector

class Player(Movable, GameObject):
    def __init__(self, name, player_position, look_size):
        Movable.__init__(self, player_position, PLAYERSPEED)
        self.name = name
        self.look_size = look_size
        self.new_objects[name] = {}
        self.object_updates[name] = {}
        self.prev_looked = set()

    def accept(self):
        """впервое обращение клиента, возвращает размер карты, позицию и первые тайлы"""
        looked = self.world.look(self.position, self.look_size)
        new_looked = looked - self.prev_looked
        self.prev_looked = looked
        
        world_size = self.world.size
        objects = {name:(player.position,'player') for name, player in self.players.items()}
        #оповещаем всех о своем появлении
        for name in self.players.keys():
            if name!=self.name:
                self.new_objects[name][self.name] = self.position
                
        return  world_size, self.position, looked, objects
    
    def go(self, vector):
        self.move(vector)
        for client, update_dict in self.object_updates.items():
            self.object_updates[client][self.name] = self.move_vector
    

        
    def look(self):
        #получаем новые видимые тайлы
        looked =self.world.look(self.position, self.look_size)
        new_looked = looked - self.prev_looked
        self.prev_looked = looked
        
        #ищем новые объекты
        new_objects = {}
        for name, position in self.new_objects[self.name].items():
            if name!=self.name:
                new_objects[name] = (position,'player')
        self.new_objects[self.name] = {}
        #ищем бновления объектов
        updates = self.object_updates[self.name]
        self.object_updates[self.name] = {}
        return self.move_vector, new_looked, new_objects, updates
    
    def __del__(self):
        del self.new_objects[self.name]
        del self.object_updates[self.name]
        #удаляем себя из списка объектов
        #оповещаем других игроков о выходе
        for client, update_dict in self.object_updates.items():
            self.object_updates[client][self.name] = 'remove'
        print '__del__ %s' % self.name
        
        
    

            
