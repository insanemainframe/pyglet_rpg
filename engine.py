#!/usr/bin/env python
# -*- coding: utf-8 -*-
from mathlib import *
from maplib import World, MetaMap
from config import TILESIZE, PLAYERSPEED, BLOCKTILES ,logger

class GameObject:
    @staticmethod
    def configure(world,rad):
        GameObject.world = world
        GameObject.size = world.size
        GameObject.rad = rad
        print 'create game', world.size

class Game(GameObject):
    def __init__(self, look_size):
        world = World()
        self.configure(world, look_size)

        self.player = Player(Point(self.size/2*TILESIZE, self.size/2*TILESIZE), look_size)

    def accept(self):
        "впервое обращение клиента, возвращает размер карты, позицию и первые тайлы "
        position = self.player.position
        land, objects = self.player.look()
        world_size = self.world.size
        return  world_size, position, land, ({'Player':(position,'player')},())
    
    def go(self, vector):
        move_vector = self.player.go(vector)
        land, objects = self.player.look()

        return move_vector, land, ({},{'Player':move_vector})
        
    
class Movable(MetaMap):
    def __init__(self, position, speed):
        self.vector  = Point(0,0)
        self.speed = speed
        self.position = position
        
    def move(self, vector):
        #если вектор на входе определен, до определяем вектор движения объекта
        if vector:
            self.vector = vector

        #если вектор движения не достиг нуля, то продолжить движение
        if self.vector:
            #проверка столкновения
            i,j = get_cross(self.position, self.vector)
            cross_tile =  self.map[i][j]
            if cross_tile in BLOCKTILES:
                self.vector = Point(0,0)
                return self.vector
            part = self.speed / abs(self.vector) # доля пройденного пути в векторе
            move_vector = self.vector * part if part<1 else self.vector
            self.vector = self.vector - move_vector
            self.position = self.position + move_vector
            return move_vector
        else:
            return self.vector
    


class Player(Movable, GameObject):
    def __init__(self, position, rad):
        Movable.__init__(self, position, PLAYERSPEED)
        self.rad = rad
        self.prev_looked = set()
        
    
    def go(self, vector):
        return self.move(vector)
    
    def look(self):
        #получаем видимые тайлы
        looked =self.world.look(self.position, self.rad)
        
        new_looked = looked - self.prev_looked

        self.prev_looked = looked
            

        return (new_looked, {})
            
