#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from share.mathlib import *
from engine.engine_lib import *
from collissions import *


from math import hypot



##########################################################

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
    def move(self, vector=Point()):
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
                    part = self.speed / abs(self.vector) # доля пройденного пути в векторе
                    move_vector = self.vector * part if part<1 else self.vector
                    #определяем столкновения с тайлами
                    if move_vector:
                        move_vector = self._tile_collission(move_vector)
                    
                    
                    
                    self.vector = self.vector - move_vector
                    move_vector = move_vector
                else:
                    move_vector = self.vector
                
                if move_vector:
                    self._detect_collisions(move_vector)
                    
                self.change_position(self.position+move_vector)
                self.move_vector = move_vector
                
                
                #добавляем событие
               
                if self.position_changed:
                    self.add_event( 'move',  self.move_vector.get())
                    
                
    
    def _tile_collission(self, move_vector):
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
            else:
                move_vector = Point()
                self.vector = move_vector
                break
                
            
        move_vector *= resist
        return move_vector
    
    def _detect_collisions(self, move_vector):
        solids = self.location.get_solids_list()
        
        dists = []
        for Player in solids:
            if Player.name != self.name:
                distance = abs(Player.position - self.position)
                if distance <= Player.radius+self.radius:
                    dists.append((distance, Player.radius))
                    Player.collission(self)
                    self.collission(Player)

    
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
    

