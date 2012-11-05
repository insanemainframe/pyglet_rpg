#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from share.point import *
from engine.enginelib.meta import *
from engine.enginelib.collissions import *




class Movable(GameObject):
    "класс движущихся объектов"
    BLOCKTILES = []
    SLOWTILES = {}
    def __init__(self,  speed):
        self._vector  = Point(0,0)
        self.speed = speed
        self._move_vector = Point(0,0)
        self._moved = False
        self._stopped = 0

    @property
    def move_vector(self):
        return self._move_vector 

    @property
    def vector(self):
        return self._vector 

    def flush(self):
        self._move_vector = Point(0,0)
        self._vector = Point(0,0)
    
    def move(self, vector=Point(0,0), destination=False):
        assert isinstance(vector, Point)
        
        success = True

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
                        move_vector, resist, blocked = self._tile_collission(move_vector, destination)
                        success = not blocked
             
                    
                    
                    self._vector = self._vector - move_vector
                    move_vector = move_vector * resist
                else:
                    move_vector = self._vector
                
                if self.location_changed:
                        self._move_vector = Point(0,0)
                        self._vector = Point(0,0)
                        success = False

                if move_vector:
                    self.change_position(self.position+move_vector)
                    self._move_vector = move_vector
                
                    #добавляем событие
                    if self._move_vector:
                        self.add_event('move',  self._move_vector.get())
        return success
                    
                
    
    def _tile_collission(self, move_vector, destination):
        "определения пересечяения вектора с непрохоодимыми и труднопроходимыми тайлами"
        resist = 1
        blocked = False
        for (i,j), cross_position in get_cross(self.position, move_vector):
            if 0<i<self.location.size and 0<j<self.location.size:
                cross_tile =  self.location.map[i][j]
                collission_result = self._detect_collisions(i,j)

                if cross_tile in self.BLOCKTILES or collission_result:
                    move_vector = (cross_position - self.position)*0.90
                    self._vector = move_vector
                    self.tile_collission(cross_tile)
                    blocked = True
                    break

                if cross_tile in self.SLOWTILES:
                    resist = self.SLOWTILES[cross_tile]
                
                #опеределяем колиззии с объектами в данной клетке

                if self.location_changed:
                    blocked = True
                    break
            else:
                move_vector = Point(0,0)
                self._vector = move_vector
                blocked = True
                break
        else:
            if destination:
                for player in self.location.get_voxel(i,j):
                    if player.name==destination:
                        player.collission(proxy(self))
                        self.collission(player)

                
            
        return move_vector, resist, blocked
        
    def _detect_collisions(self, i,j):
        for player in self.location.get_voxel(i,j):
            if player.name != self.name:
                player.collission(proxy(self))
                self.collission(player)
                if isinstance(player, Impassable):
                    return True
        return False
        
    
    def complete_round(self):
        self._moved = False

    def stop(self, time):
        "останавливает на опредленное времчя"
        self._stopped = time
    
    def abort_moving(self):
        self._vector = Point(0,0)
        self._move_vector = Point(0,0)
    

    def update(self):
        if not self._moved and self._vector:
            Movable.move(self)
    
    def plus_speed(self, speed):
        self.speed+=speed
    

