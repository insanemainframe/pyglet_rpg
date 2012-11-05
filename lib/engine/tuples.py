#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from share.point import *
from collections import namedtuple


Event = namedtuple("Event", ('action', 'args', 'timeout'))
ObjectTuple = namedtuple('ObjectTuple', ['gid', 'name', 'object_type', 'position', 'args'])
OnlineTuple = namedtuple('OnlineTuple', ['name', 'frags'])