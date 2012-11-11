# -*- coding: utf-8 -*-
from cpython cimport bool
from share.point cimport Point

cdef class Position(Point):
	cpdef Cord to_cord(Position self)
	cpdef ChunkCord to_chunk(Position self)


cdef class Cord(Point):
	cpdef Position to_position(Cord self)
	cpdef ChunkCord to_chunk(Cord self)


cdef class ChunkCord(Point):
	cpdef Cord to_cord(ChunkCord self)
	cpdef Position to_position(ChunkCord self)

	

	

    
