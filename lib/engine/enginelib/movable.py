#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from server_logger import debug

from engine.mathlib import Cord, Position, ChunkCord
from engine.enginelib.meta import *

from engine.enginelib.collissions import *


class Movable(object):
    "класс движущихся объектов"
    BLOCKTILES = []
    SLOWTILES = {}

    def mixin(self, speed=0):

        self.__vector  = Position(0, 0)
        self.__speed = speed
        self.__move_vector = Position(0, 0)
        self.__moved = False
        self.__stopped = 0

        self.add_activity('Movable')

        self.destination = None


    def set_speed(self, speed):
        self.__speed = speed

    def update_speed(self, speed):
        self.__speed += speed

    def get_speed(self):
        return self.__speed
    
    def get_move_vector(self):
        return self.__move_vector 

    def get_vector(self):
        return self.__vector 

    def flush(self):
        self.__move_vector = Position(0, 0)
        self.__vector = Position(0, 0)

    def stop(self, time):
        "останавливает на опредленное времчя"
        self.__stopped = time
    
    def abort_moving(self):
        self.__vector = Position(0,0)
        self.__move_vector = Position(0,0)

    
    def move(self, vector=Position(0, 0), destination=False):
        assert isinstance(vector, Position), vector
        
        success = True

        if vector:
            self.add_activity('Movable')

        if destination:
            self.destination = destination

        if vector and not destination:
            self.destination = None

        if not self.__moved:
            self.__moved = True
            if self.__stopped > 0:
                self.__stopped -= 1
            else:
                #если вектор на входе определен, до определяем вектор движения объекта
                if vector:
                    self.__vector = vector

                #если вектор движения не достиг нуля, то продолжить движение
                if self.__vector:
                    
                    #проверка столкновения
                    part = self.__speed / abs(self.__vector) # доля пройденного пути в векторе
                    move_vector = self.__vector * part if part < 1 else self.__vector
                    #определяем столкновения с тайлами
                    new_cord = (self.position + move_vector).to_cord()

                    resist = 1
                    if self.cord != new_cord:
                        move_vector, resist, blocked = self._tile_collission(move_vector)
                        success = not blocked
                    
                    self.__vector = self.__vector - move_vector
                    move_vector = move_vector * resist
                    
                else:
                    move_vector = self.__vector
                
                if self.location_changed:
                        self.__move_vector = Position(0, 0)
                        self.__vector = Position(0, 0)
                        success = False

                if move_vector:
                    self.update_position(move_vector)

                    self.__move_vector = move_vector

                    if not self.__vector and self.destination:
                        self._get_object(True)
                
                    #добавляем событие
                    # if self.__move_vector:
                    #     self.add_event('move',  self.__move_vector.get())
        # if not self.__vector:
        #     self.pop_activity()
        return success
                     
    
    def _tile_collission(self, move_vector):
        "определения пересечяения вектора с непрохоодимыми и труднопроходимыми тайлами"
        resist = 1
        blocked = False

        for (i,j), cross_position in get_cross(self.position, move_vector):
            if self.location.is_valid_cord_2i(i, j):

                cross_tile =  self.location.get_tile_2i(i ,j)
                
                collission_result = self._voxel_collision(i, j)

                if cross_tile in self.BLOCKTILES or not collission_result:
                    move_vector = (cross_position - self.position) * 0.90
                    self.__vector = move_vector
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
                move_vector = Position(0, 0)
                self.__vector = move_vector
                blocked = True
                break

        return move_vector, resist, blocked
        
    def _get_object(self, force = False):
        assert self.destination

        for player in self.location.get_voxel(self.cord):
            if player.name == self.destination:
                player.collission(proxy(self))
                self.collission(player)
                self.destination = None
                break
        if force:
            for voxel in self.location.get_near_voxels(self.cord):
                for player in voxel.values():
                    if player.name == self.destination:
                        player.collission(proxy(self))
                        self.collission(player)
                        break
             
    def _voxel_collision(self, i, j):
        for player in self.location.get_voxel_2i(i, j):
            if isinstance(player, Solid) and player.name != self.name:
                player.collission(proxy(self))
                self.collission(player)

                if player.name == self.destination:
                    self.destination = None

                if not player.is_passable() or player.is_alive():
                    return True
                else:
                    return False

        return True
        

    def __update__(self, cur_time):
        if not self.__moved and self.__vector:
            Movable.move(self)

    def __complete_round__(self):
        self.__moved = False
        self.__move_vector = False


    def handle_change_location(self):
        self.flush()

    def handle_remove(self):
        self.flush()



    

