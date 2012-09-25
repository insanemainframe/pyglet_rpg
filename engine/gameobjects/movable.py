#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from share.mathlib import *
from engine.engine_lib import *
from math import hypot, ceil,floor

from config import *

def intersec_point(A,B,C,D):
    "ищет точку пересечения двух векторов"
    vector = (B-A)
    if vector.y:
        div = vector.x.__truediv__(vector.y)
        divx = True
    elif vector.x:
        div = vector.y.__truediv__(vector.x)
        divx = False
    if C.x==D.x:
        x = C.x - A.x
        y = x/div if divx else x*div
        return A+ Point(x,y)
    elif C.y == D.y:
        y = C.y - A.y
        x = y*div if divx else y/div
        return A + Point(x,y)

def interception(A,B,C,D):
    "пересекаются ли отрезки"
    def ccw(A,B,C):
        return (C.y-A.y)*(B.x-A.x) > (B.y-A.y)*(C.x-A.x)
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)


def cross_tile(A, B, tilecord):
    "выдает соседние тайлы с которыми пересекается вектор и координаты пересечения"
    start = tilecord*TILESIZE
    null, CELL = 0 , TILESIZE
    cds = {tilecord + Point(0,1) : (start + Point(null ,CELL), start+Point(CELL,CELL)),
                tilecord + Point(1,0) : (start + Point(CELL, CELL), start + Point(CELL, null)),
                tilecord + Point(0,-1) : (start, start + Point(CELL, null)),
                tilecord + Point(-1,0) : (start, start + Point(null, CELL))}
    
    return [(ij, intersec_point(A,B,C, D)) for ij,(C, D) in cds.items() if interception(A,B,C,D)]
        

def get_cross(position, vector):
    "возвращает i,j пересекаемых векторов тайлов и координаты этих пересечений"
    end_cord = (position+vector)/TILESIZE #i,j конечнй точки
    results = []
    cur_tile = position/TILESIZE
    crossed = [cur_tile]
    while 1:
        counter = 0
        crossed_tiles = cross_tile(position, position+vector, cur_tile)
        #print 'loop', crossed_tiles, position, vector
        if crossed_tiles:
            for ij, cross in crossed_tiles:
                if not ij in crossed:
                    counter+=1
                    crossed.append(ij)
                    results.append((ij.get(), cross))
                    cur_tile = ij
                    if ij == end_cord:
                        return results
            if not counter:
                #print 'COUNTER BREAK'
                return results
        else:
            #print 'BREAK'
            return results
    return results

##########################################################


class MovableShare:
    @staticmethod
    def new_player(player):
        if hasattr(MovableShare, 'position_list'):
            MovableShare.player_list[player.name] = player
        else:
            MovableShare.player_list = {}
    
    @staticmethod
    def update_player(player):
        MovableShare.player_list[player.name] = player
        for Player in MovableShare.player_list.values():
            distance = abs(Player.position - player.position)
            if distance <= Player.radius+player.radius:
                if isinstance(Player, Mortal) and isinstance(player,Deadly):
                    if player.fraction!=Player.fraction:
                        player.hit(Player.damage)
                        Player.collission()
                        if isinstance(Player, Fragile):
                            Player.REMOVE = True
        
        
    
    @staticmethod
    def remove_player(player):
        del MovableShare.player_list[player.name]
        
            
class Movable(MovableShare):
    "класс движущихся объектов"
    BLOCKTILES = []
    SLOWTILES = {}
    def __init__(self,  speed):
        self.vector  = NullPoint
        self.speed = speed
        self.move_vector = NullPoint
        self.prev_position = Point(-1,-1)
        self.moved = False
        self.new_player(self)
    
    
    def move(self, vector=NullPoint):
        if self.moved:
            raise ActionDenied
        #если вектор на входе определен, до определяем вектор движения объекта
        if vector:
            self.vector = vector
        #если вектор движения не достиг нуля, то продолжить движение
        if self.vector:
            #проверка столкновения
            part = self.speed / abs(self.vector) # доля пройденного пути в векторе
            move_vector = self.vector * part if part<1 else self.vector
            #определяем столкновения с тайлами
            move_vector = self._tile_collission(move_vector)
            
            
            
            self.vector = self.vector - move_vector
            self.move_vector = move_vector
        else:
            self.move_vector = self.vector
        self.prev_position = self.position
        self.position+=self.move_vector
        
        self.moved = True
        
        altposition = self.position
        #добавляем событие
        self.add_event(self.prev_position, altposition, 'move', [self.move_vector.get()])
        self.update_player(self)
    
    def _tile_collission(self, move_vector):
        "определения пересечяения вектора с непрохоодимыми и труднопроходимыми тайлами"
        resist = 1
        crossed = get_cross(self.position, move_vector)
        for (i,j), cross_position in crossed:
            cross_tile =  game.world.map[i][j]
            if cross_tile in self.BLOCKTILES:
                move_vector = (cross_position - self.position)*0.99
                self.vector = move_vector
                #если объект хрупкий - отмечаем для удаления
                if isinstance(self, Fragile):
                    self.REMOVE = True
                break
            if cross_tile in self.SLOWTILES:
                resist = self.SLOWTILES[cross_tile]
        move_vector *= resist
        return move_vector
        
    
    def complete_round(self):
        self.moved = False
    
    def handle_request(self):
        return self.move_vector
    
    def update(self):
        if not self.moved:
            return self.move()
    def __del__(self):
        self.remove_player(self)
        print 'remove movable'

