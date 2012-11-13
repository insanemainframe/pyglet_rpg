#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from share.mathlib cimport Point
from cpython cimport bool

from engine.enginelib.meta import DynamicObject, Impassable

from engine.enginelib.collissions import get_cross
from engine.enginelib import wrappers


from math import hypot



cdef class Movable:
    "класс движущихся объектов"
    cdef Point _vector
    cdef int speed
    cdef Point _move_vector
    cdef bool _moved
    cdef int _stopped

    cpdef mixin(Movable self,  int speed):
        self._vector  = Point(0,0)
        self.speed = speed
        self._move_vector = Point(0,0)
        self._moved = False
        self._stopped = 0

    property move_vector:
        def __get__(Movable self):
            return self._move_vector 

    property vector:
        def __get__(Movable self):
            return self._vector 

    cpdef  flush(Movable self):
        self._move_vector = Point(0,0)
        self._vector = Point(0,0)
    
    cpdef move(Movable self, Point vector, destination=False):
        cdef Point move_vector, new_cord

        labs = abs
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
                    part = self.speed / labs(self._vector) # доля пройденного пути в векторе
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
                    
                
    
    cdef tuple _tile_collission(Movable self, Point move_vector, destination):
        "определения пересечяения вектора с непрохоодимыми и труднопроходимыми тайлами"
        cdef int resist, i,j
        cdef Point cross_position

        resist = 1
        for (i,j), cross_position in get_cross(self.position, move_vector):
            if 0<i<self.world.size and 0<j<self.world.size:
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
        
    cdef bool _detect_collisions(Movable self, Point cord):
        for player in self.world.tiles[cord].copy():
            if player.name != self.name:
                player.collission(self)
                self.collission(player)
                if isinstance(player, Impassable):
                    return True
        return False
        
    
    cpdef _complete_move(Movable self):
        self._moved = False

    cpdef stop(Movable self, time):
        "останавливает на опредленное времчя"
        self._stopped = time
    
    cpdef  abort_moving(Movable self):
        self._vector = Point(0,0)
        self._move_vector = Point(0,0)
    

    
    cpdef  _update_move(Movable self):
        if self._vector:
            Movable.move(self, Point(0,0))
    
    cpdef  plus_speed(Movable self, speed):
        self.speed+=speed
    

