#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sys import path, argv; path.append('./')
from config import SOCKET_SERVER_PROFILE_FILE

import pstats
if len(argv)>1:
    sort_value = argv[1]
else:
    sort_value = 'time'
stats = pstats.Stats(SOCKET_SERVER_PROFILE_FILE)
stats.sort_stats(sort_value)
stats.print_stats()
