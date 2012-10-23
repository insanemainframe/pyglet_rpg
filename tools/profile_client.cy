#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sys import path, argv; path.append('../')
from config import CLIENT_PROFILE_FILE

import pstats
if len(argv)>1:
    sort_value = argv[1]
else:
    sort_value = 'time'
stats = pstats.Stats(CLIENT_PROFILE_FILE)
stats.sort_stats('cumulative')
stats.print_stats()
