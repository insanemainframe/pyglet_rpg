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
    def move(self, vector=NullPoint):
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
                    self.move_vector = move_vector
                else:
                    self.move_vector = self.vector
                self.change_position(self.position+self.move_vector)
                
                
                #добавляем событие
               
                if self.position_changed:
                    self.add_event( 'move',  self.move_vector.get())
                    self._detect_collisions(self)
                
    
    def _tile_collission(self, move_vector):
        "определения пересечяения вектора с непрохоодимыми и труднопроходимыми тайлами"
        resist = 1
        crossed = get_cross(self.position, move_vector)
        for (i,j), cross_position in crossed:
            if 0<i<self.world.size and 0<j<self.world.size:
                cross_tile =  self.world.map[i][j]
                if cross_tile in self.BLOCKTILES:
                    move_vector = (cross_position - self.position)*0.99
                    self.vector = move_vector
                    #если объект хрупкий - отмечаем для удаления
                    self.tile_collission(cross_tile)
                    break
                if cross_tile in self.SLOWTILES:
                    resist = self.SLOWTILES[cross_tile]
            else:
                move_vector = NullPoint
                self.vector = move_vector
                break
                
            
        move_vector *= resist
        return move_vector
    
    @wrappers.player_filter_alive
    def _detect_collisions(self, player):
        solids = self.location.get_solids_list()
        
        
        for Player in solids:
            if Player.name != self.name:
                distance = abs(Player.position - player.position)
                if distance <= Player.radius+player.radius:
                    Player.collission(player)
                    player.collission(Player)
    
    def complete_round(self):
        self.moved = False

    def stop(self, time):
        "останавливает на опредленное времчя"
        self.stopped = time
    
    def abort_moving(self):
        self.vector = NullPoint
        self.move_vector = NullPoint
    

    
    @wrappers.alive_only()
    def update(self):
        if not self.moved and self.vector:
            self.move()
    
    def plus_speed(self, speed):
        self.speed+=speed
    

