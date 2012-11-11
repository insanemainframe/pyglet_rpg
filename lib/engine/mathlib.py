# -*- coding: utf-8 -*-
from config import TILESIZE, CHUNK_SIZE

from random import random
from math import hypot, floor



from share.point import Point


########################################################################

def chance(n):
    n = n/100.0
    if random()<n:
        return True
    else:
        return False





    
class Position(Point):
	"класс точек и векторов"
	def to_cord(self):
		return Cord(*(self/TILESIZE).get())

	def to_chunk(self):
		return ChunkCord(*(self/TILESIZE/CHUNK_SIZE).get())

	def __add__(self, point):
	    assert isinstance(point, Position)
	    return Position(self.x + point.x, self.y + point.y)

	def __sub__(self, point):
	    "-"
	    assert isinstance(point, Position)
	    return Position(self.x - point.x, self.y - point.y)

	def __neg__(self):
	    return Position(-self.x, -self.y)
	    
	def __mul__(self, number):
	    '*'
	    return Position(self.x*number, self.y*number)

	def __div__( self,  number):
	    return Position(floor(self.x/number), floor(self.y/number))

	def __truediv__( self,  number):
	    return Position(floor(self.x/number), floor(self.y/number))

	def __repr__(self):
	    return "Position[%s:%s]" % self.get()

	


class Cord(Point):
	def to_position(self):
		return Position(*(self*TILESIZE).get())

	def to_chunk(self):
		return ChunkCord(*(self/CHUNK_SIZE).get())

	def __add__(self, point):
		assert type(self) is type(point)
		return Cord(self.x + point.x, self.y + point.y)

	def __sub__(self, point):
	    "-"
	    assert type(self) is type(point)
	    return Cord(self.x - point.x, self.y - point.y)

	def __neg__(self):
	    return Cord(-self.x, -self.y)
        
	def __mul__(self, number):
	    '*'
	    return Cord(self.x*number, self.y*number)

	def __div__( self,  number):
	    return Cord(floor(self.x/number), floor(self.y/number))

	def __truediv__( self,  number):
	    return Cord(floor(self.x/number), floor(self.y/number))

	def __repr__(self):
	    return "Cord[%s:%s]" % self.get()


	

class ChunkCord(Point):
	def to_cord(self):
		return Cord(*(self*CHUNK_SIZE).get())

	def to_position(self):
		return Position(*(self*CHUNK_SIZE*TILESIZE).get())

	def __add__(self, point):
	    assert type(self) is type(point)
	    return ChunkCord(self.x + point.x, self.y + point.y)

	def __sub__(self, point):
	    "-"
	    assert type(self) is type(point)
	    return ChunkCord(self.x - point.x, self.y - point.y)

	def __neg__(self):
	    return ChunkCord(-self.x, -self.y)
	    
	def __mul__(self, number):
	    '*'
	    return ChunkCord(self.x*number, self.y*number)

	def __div__( self,  number):
	    return ChunkCord(floor(self.x/number), floor(self.y/number))

	def __truediv__( self,  number):
	    return ChunkCord(floor(self.x/number), floor(self.y/number))

	def __repr__(self):
	    return "ChunkCord[%s:%s]" % self.get()

	

    
