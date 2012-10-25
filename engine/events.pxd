#!/usr/bin/env python
# -*- coding: utf-8 -*-
from share.mathlib cimport Point

cdef class Event:
    cdef str name
    cdef str object_type
    cdef Point position
    cdef public Point cord
    cdef str action
    cdef tuple args
    cdef int timeouted

    

