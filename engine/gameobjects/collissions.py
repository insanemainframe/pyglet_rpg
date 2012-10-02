#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sys import path; path.append('../../')

from share.mathlib import *
from math import hypot

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

#if (playerx > blockminx) and (playery < blockmaxx) and (playery > blockminy) and (playery < blockmaxy) then collission

def get_tile(cord):
    "выдает отрезки сторон квадрата"
    a = cord*TILESIZE
    A = (cord + Point(0,1))*TILESIZE
    
    b = A
    B = (cord + Point(1,1))*TILESIZE
    
    c = B
    C = (cord + Point(1,0))*TILESIZE
    
    d = a
    D = C
    return ((a,A),(b,B), (c,C),(d,D))
    
def tile_intersec(player, tilemin, tilemax):
    return player.x>tilemin.x and player.y<tilemax.y and player.y>tilemin.y and player.y<tilemax.y

def get_cross2(position, vector):
    A = (position)/TILESIZE
    B = (position+Point(0,vector.y))/TILESIZE
    C = (position + vector)/TILESIZE
    D = (position + Point(vector.x,0))/TILESIZE
    print 'A %s B %s C %s D %s'%(A,B,C,D)
    tiles = []
    for i in range(B.x, C.x):
        for j in range(A.y, B.y):
            tiles.append(Point(i,j))
    crossed = []
    for cord in tiles:
        tile_sides = get_tile(cord)
        for C,D in tile_sides:
            if interception(position,vector,C,D):
                crossed.append(cord)
                break
                
    return crossed

def get_cross(position, vector):
    "возвращает i,j пересекаемых векторов тайлов и координаты этих пересечений"
    end_cord = (position+vector)/TILESIZE #i,j конечнй точки
    results = []
    cur_tile = position/TILESIZE
    crossed = [cur_tile]
    while 1:
        counter = 0
        crossed_tiles = cross_tile(position, position+vector, cur_tile)
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


print get_cross2(Point(10*TILESIZE,10*TILESIZE), Point(-3*TILESIZE, -4*TILESIZE))
