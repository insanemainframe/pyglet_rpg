#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import Counter, defaultdict

tiledict = defaultdict(lambda: 'underground',
            { (255,0,0): 'stone', 
            (128,128,128): 'underground',
            (0,0,255): 'water',
            (0,0,128): 'ocean',})
