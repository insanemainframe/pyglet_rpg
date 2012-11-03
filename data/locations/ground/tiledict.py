#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import Counter, defaultdict

tiledict = defaultdict(lambda: 'grass',
            { (255,0,0): 'stone', 
            (0,255,0): 'grass',
            (128,128,0): 'bush',
            (0,0,255): 'water',
            (0,0,128): 'ocean',})
