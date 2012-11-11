# -*- coding: utf-8 -*-
from config import TILESIZE, CHUNK_SIZE

from random import random
from math import hypot, floor


from cpython cimport bool
from share.point cimport Point


########################################################################

cpdef bool chance(float n):
	n = n/100.0
	if random()<n:
		return True
	else:
		return False





    
cdef class Position(Point):
	"класс точек и векторов"
	cpdef Cord to_cord(Position self):
		return Cord(*(self/TILESIZE).get())

	cpdef ChunkCord to_chunk(Position self):
		return ChunkCord(*(self/TILESIZE/CHUNK_SIZE).get())

	def __add__(Position self, Position point):
		return Position(self.x + point.x, self.y + point.y)

	def __sub__(Position self, Position point):
		return Position(self.x - point.x, self.y - point.y)

	def __neg__(Position self):
		return Position(-self.x, -self.y)
	    
	def __mul__(Position self, number):
		return Position(self.x*number, self.y*number)

	def __div__(Position self,  number):
		return Position(floor(self.x/number), floor(self.y/number))

	def __truediv__(Position self,  number):
		return Position(floor(self.x/number), floor(self.y/number))

	def __repr__(Position self):
		return "Position[%s:%s]" % self.get()

	


cdef class Cord(Point):
	cpdef Position to_position(Cord self):
		return Position(*(self*TILESIZE).get())

	cpdef ChunkCord to_chunk(Cord self):
		return ChunkCord(*(self/CHUNK_SIZE).get())

	def __add__(Cord self, Cord point):
		return Cord(self.x + point.x, self.y + point.y)

	def __sub__(Cord self, Cord point):
		"-"
		return Cord(self.x - point.x, self.y - point.y)

	def __neg__(Cord self):
		return Cord(-self.x, -self.y)
	    
	def __mul__(Cord self, number):
		'*'
		return Cord(self.x*number, self.y*number)

	def __div__(Cord self,  number):
		return Cord(floor(self.x/number), floor(self.y/number))

	def __truediv__(Cord self,  number):
		return Cord(floor(self.x/number), floor(self.y/number))

	def __repr__(Cord self):
		return "Cord[%s:%s]" % self.get()


	

cdef class ChunkCord(Point):
	cpdef Cord to_cord(ChunkCord self):
		return Cord(*(self*CHUNK_SIZE).get())

	cpdef Position to_position(ChunkCord self):
		return Position(*(self*CHUNK_SIZE*TILESIZE).get())

	def __add__(ChunkCord self, ChunkCord point):
		return ChunkCord(self.x + point.x, self.y + point.y)

	def __sub__(ChunkCord self, ChunkCord point):
		"-"
		return ChunkCord(self.x - point.x, self.y - point.y)

	def __neg__(ChunkCord self):
		return ChunkCord(-self.x, -self.y)
	    
	def __mul__(ChunkCord self, number):
		'*'
		return ChunkCord(self.x*number, self.y*number)

	def __div__(ChunkCord self,  number):
		return ChunkCord(floor(self.x/number), floor(self.y/number))

	def __truediv__(ChunkCord self,  number):
		return ChunkCord(floor(self.x/number), floor(self.y/number))

	def __repr__(ChunkCord self):
		return "ChunkCord[%s:%s]" % self.get()

	

    
