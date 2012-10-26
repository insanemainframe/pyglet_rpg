#!/usr/bin/env python
# -*- coding: utf-8 -*-

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from os import walk
from os.path import basename, join


ext_modules = []


for root, subfolders, files in walk('.'):
        for pyx_file in files:
        	if pyx_file[-4:] == '.pyx':
        		pyx_file = join(root, pyx_file)

        		name = basename(pyx_file)
        		
        		extension  = Extension(name, [pyx_file])
        		ext_modules.append(extension)








setup(
  name = 'pyglet rpg',
  cmdclass = {'build_ext': build_ext},
  ext_modules = ext_modules
)