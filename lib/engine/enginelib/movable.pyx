#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from share.point cimport Point
from engine.enginelib.meta import DynamicObject, Impassable
from engine.enginelib.collissions import *
from engine.enginelib import wrappers


from math import hypot



cdef class Movable:
    "класс движущихся объектов"
    property move_vector:
        def __get__(Movable self):
            return self._move_vector 

    property vector:
        def __get__(Movable self):
            return self._vector 

    cdef Point _vector, _move_vector
    cdef int speed

    BLOCKTILES = []
    SLOWTILES = {}

    def __init__(Movable self,  speed):
        self._vector  = Point(0,0)
        self.speed = speed
        self._move_vector = Point(0,0)
        self._moved = False
        self._stopped = 0

    

    def flush(Movable self):
        self._move_vector = Point(0,0)
        self._vector = Point(0,0)
    
    def move(Movable self, vector=Point(0,0), destination=False):
        cdef Point move_vector
        if not self.alive:
            return 

        if not self._moved:
            self._moved = True
            if self._stopped>0:
                self._stopped-=1
            else:
                #если вектор на входе определен, до определяем вектор движения объекта
                if vector:
                    self._vector = vector
                #если вектор движения не достиг нуля, то продолжить движение
                
                if self._vector:
                    
                    #проверка столкновения
                    part = self.speed / abs(self._vector) # доля пройденного пути в векторе
                    move_vector = self._vector * part if part<1 else self._vector
                    #определяем столкновения с тайлами
                    new_cord = (self.position+move_vector)/TILESIZE

                    resist = 1
                    if self.cord!= new_cord:
                        move_vector, resist = self._tile_collission(move_vector, destination)
                    
                    
                    self._vector = self._vector - move_vector
                    move_vector = move_vector * resist
                else:
                    move_vector = self._vector
                
                if self.world_changed:
                        self._move_vector = Point(0,0)
                        self._vector = Point(0,0)

                if move_vector:
                    self.change_position(self.position+move_vector)
                    self._move_vector = move_vector
                
                    #добавляем событие
                    if self._move_vector:
                        self.add_event('move',  self._move_vector.get())
                    
                
    
    def _tile_collission(Movable self, Point move_vector, destination):
        "определения пересечяения вектора с непрохоодимыми и труднопроходимыми тайлами"
        cdef int resist, i,j, world_size

        world_size = self.world.size
        resist = 1
        for (i,j), cross_position in get_cross(self.position, move_vector):
            if 0<i<world_size and 0<j<world_size:
                cross_tile =  self.world.map[i][j]
                collission_result = self._detect_collisions(Point(i,j))

                if cross_tile in self.BLOCKTILES or collission_result:
                    move_vector = (cross_position - self.position)*0.90
                    self._vector = move_vector
                    self.tile_collission(cross_tile)
                    break

                if cross_tile in self.SLOWTILES:
                    resist = self.SLOWTILES[cross_tile]
                
                #опеределяем колиззии с объектами в данной клетке

                if self.world_changed:
                    break
            else:
                move_vector = Point(0,0)
                self._vector = move_vector
                break
        else:
            if destination and cross_tile:
                for player in self.world.tiles[cross_tile]:
                    if player.name==destination:
                        player.collission(self)
                        self.collission(player)

                
            
        return move_vector, resist
        
    def _detect_collisions(Movable self, Point cord):
        cdef set tile

        tile = self.world.tiles[cord].copy()
        for player in tile:
            if player.name != self.name:
                player.collission(self)
                self.collission(player)
                if isinstance(player, Impassable):
                    return True
        return False
        
    
    def complete_round(Movable self):
        self._moved = False

    def stop(Movable self, time):
        "останавливает на опредленное времчя"
        self._stopped = time
    
    def abort_moving(Movable self):
        self._vector = Point(0,0)
        self._move_vector = Point(0,0)
    

    
    @wrappers.alive_only()
    def update(Movable self):
        if not self._moved and self._vector:
            Movable.move(self)
    
    def plus_speed(Movable self, speed):
        self.speed+=speed
    

