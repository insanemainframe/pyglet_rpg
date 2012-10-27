#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from share.mathlib import *
from collections import namedtuple

Event = namedtuple("Event", ('action', 'args', 'timeout'))
