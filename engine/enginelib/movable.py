#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from share.mathlib import *
from engine.enginelib.meta import *
from engine.enginelib.collissions import *
from engine.enginelib import wrappers


from math import hypot



class Movable(DynamicObject):
    "класс движущихся объектов"
    BLOCKTILES = []
    SLOWTILES = {}
    def __init__(self,  speed):
        self.vector  = Point()
        self.speed = speed
        self.move_vector = Point()
        self.moved = False
        self.stopped = 0
    
    @wrappers.alive_only()
    def move(self, vector=Point(), destination=False):
        labs = abs
        if not self.moved:
            self.moved = True
            if self.stopped>0:
                self.stopped-=1
            else:
                #если вектор на входе определен, до определяем вектор движения объекта
                if vector:
                    self.vector = vector
                #если вектор движения не достиг нуля, то продолжить движение
                
                if self.vector:
                    
                    #проверка столкновения
                    part = self.speed / labs(self.vector) # доля пройденного пути в векторе
                    move_vector = self.vector * part if part<1 else self.vector
                    #определяем столкновения с тайлами
                    new_cord = (self.position+move_vector)/TILESIZE
                    if self.cord!= new_cord:
                        move_vector = self._tile_collission(move_vector, destination)
                    
                    
                    self.vector = self.vector - move_vector
                    move_vector = move_vector
                else:
                    move_vector = self.vector
                
                if self.world_changed:
                        self.move_vector = Point()
                        self.vector = Point()

                if move_vector:
                    self.change_position(self.position+move_vector)
                    self.move_vector = move_vector
                
                    #добавляем событие
                    if self.move_vector:
                        self.add_event('move',  self.move_vector.get())
                    
                
    
    def _tile_collission(self, move_vector, destination):
        "определения пересечяения вектора с непрохоодимыми и труднопроходимыми тайлами"
        resist = 1
        for (i,j), cross_position in get_cross(self.position, move_vector):
            if 0<i<self.world.size and 0<j<self.world.size:
                cross_tile =  self.world.map[i][j]
                if cross_tile in self.BLOCKTILES:
                    move_vector = (cross_position - self.position)*0.90
                    self.vector = move_vector
                    #если объект хрупкий - отмечаем для удаления
                    self.tile_collission(cross_tile)
                    break
                if cross_tile in self.SLOWTILES:
                    resist = self.SLOWTILES[cross_tile]
                
                #опеределяем колиззии с объектами в данной клетке
                self.detect_collisions(Point(i,j))
                if self.world_changed:
                    break
            else:
                move_vector = Point()
                self.vector = move_vector
                break
        else:
            if destination and cross_tile:
                for player in self.world.tiles[cross_tile]:
                    if player.name==destination:
                        player.collission(self)
                        self.collission(player)

                
            
        move_vector *= resist
        return move_vector
        
    def detect_collisions(self, cord):
        for player in self.world.tiles[cord].copy():
            if player.name != self.name:
                player.collission(self)
                self.collission(player)
        
    
    def complete_round(self):
        self.moved = False

    def stop(self, time):
        "останавливает на опредленное времчя"
        self.stopped = time
    
    def abort_moving(self):
        self.vector = Point()
        self.move_vector = Point()
    

    
    @wrappers.alive_only()
    def update(self):
        if not self.moved and self.vector:
            self.move()
    
    def plus_speed(self, speed):
        self.speed+=speed
    

