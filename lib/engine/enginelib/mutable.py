#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from server_logger import debug

from engine.mathlib import Cord, Position, ChunkCord
from engine.enginelib.meta import *

from engine.enginelib.collissions import *




class MutableObject(GameObject):
    "класс движущихся объектов"
    BLOCKTILES = []
    SLOWTILES = {}
    def __init__(self, name = None):
        GameObject.__init__(self, name)



        self.cord_changed = True
        self.position_changed = True
        self.location_changed = False


        self.__vector  = Position(0,0)
        self.__speed = 0
        self.__move_vector = Position(0,0)
        self.__moved = False
        self.__stopped = 0

        self.add_activity('MutableObject')



    

    def __change_position(self, new_position):
        "вызывается при смене позиции"
        assert isinstance(new_position, Position)
        
        if not new_position==self._position:
            self.chunk.change_position(proxy(self), new_position)

    def set_speed(self, speed):
        self.__speed = speed

    def update_speed(self, speed):
        self.__speed+=speed

    def get_speed(self):
        return self.__speed

    
    def get_move_vector(self):
        return self.__move_vector 

    def get_vector(self):
        return self.__vector 

    

    def flush(self):
        self.__move_vector = Position(0,0)
        self.__vector = Position(0,0)
    
    def move(self, vector=Position(0,0), destination=False):
        assert isinstance(vector, Position), vector
        
        success = True

        if vector:
            self.add_activity('MutableObject')

        if not self.__moved:
            self.__moved = True
            if self.__stopped>0:
                self.__stopped-=1
            else:
                #если вектор на входе определен, до определяем вектор движения объекта
                if vector:
                    self.__vector = vector
                #если вектор движения не достиг нуля, то продолжить движение
                
                if self.__vector:
                    
                    #проверка столкновения
                    part = self.__speed / abs(self.__vector) # доля пройденного пути в векторе
                    move_vector = self.__vector * part if part<1 else self.__vector
                    #определяем столкновения с тайлами
                    new_cord = (self.position+move_vector).to_cord()

                    resist = 1
                    if self.cord!= new_cord:
                        move_vector, resist, blocked = self._tile_collission(move_vector, destination)
                        success = not blocked
             
                    
                    
                    self.__vector = self.__vector - move_vector
                    move_vector = move_vector * resist
                else:
                    move_vector = self.__vector
                
                if self.location_changed:
                        self.__move_vector = Position(0,0)
                        self.__vector = Position(0,0)
                        success = False

                if move_vector:
                    self.__change_position(self.position+move_vector)
                    self.__move_vector = move_vector
                
                    #добавляем событие
                    if self.__move_vector:
                        self.add_event('move',  self.__move_vector.get())

        # if not self.__vector:
        #     self.pop_activity()
        return success
                    
                
    
    def _tile_collission(self, move_vector, destination):
        "определения пересечяения вектора с непрохоодимыми и труднопроходимыми тайлами"
        resist = 1
        blocked = False
        for (i,j), cross_position in get_cross(self.position, move_vector):
            if 0<i<self.location.size and 0<j<self.location.size:
                cross_tile =  self.location.get_tile(Cord(i,j))
                
                collission_result = self._voxel_collision(Cord(i,j))

                if cross_tile in self.BLOCKTILES or not collission_result:
                    move_vector = (cross_position - self.position)*0.90
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
                move_vector = Position(0,0)
                self.__vector = move_vector
                blocked = True
                break
        else:
            if destination:
                for player in self.location.get_tile(Cord(i,j)):
                    if player.name==destination:
                        player.collission(proxy(self))
                        self.collission(player)

                
            
        return move_vector, resist, blocked
        
    def _voxel_collision(self, cord):
        for player in self.location.get_voxel(cord):
            if isinstance(player, Solid) and player.name != self.name:
                player.collission(proxy(self))
                self.collission(player)
                if not player.is_passable():
                    return False
        return True
        
    
    

    def stop(self, time):
        "останавливает на опредленное времчя"
        self.__stopped = time
    
    def abort_moving(self):
        self.__vector = Position(0,0)
        self.__move_vector = Position(0,0)
    

    
    
    

    

    def complete_round(self):
        self.__moved = False
        self.cord_changed = False
        self.position_changed = False
        self.location_changed = False

        super(MutableObject, self).complete_round()
        

    def update(self, cur_time):
        if not self.__moved and self.__vector:
            MutableObject.move(self)





    def handle_change_location(self):
        pass

    def handle_respawn(self):
        pass




    

