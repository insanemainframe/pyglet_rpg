#!/usr/bin/env python
# -*- coding: utf-8 -*-

class MapTools:
    "методы работы с картой"
    def __init__(self, width, height):
        self.map_width = width
        self.map_height = height
        if height==width:
            self.map_size = height
    
    def resize_d(self, cord, dimension):
        "меняем координаты в случае превышения размера карты"
        if dimension=='width':
            size = self.map_width
        elif dimension=='height':
            size = self.map_height
        else:
            raise ValueError
        if cord < 0:
            return size + cord
        if cord > size:
            return size
        else:
            return cord    
    
    def resize(self, cord):
        "меняем координаты в случае превышения размера карты"
        if cord < 0:
            return self.map_size + cord
        if cord > self.map_size:
            return cord - self.map_size
        else:
            return cord      
    
