#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from cpython cimport bool

cdef class Point:
    cdef public int x
    cdef public int y
    cpdef tuple get(Point self)
    cpdef bool in_radius(self, Point point, float radius)
    
    
        


