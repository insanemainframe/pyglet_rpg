#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from server_logger import debug

from share.point import *
from collections import namedtuple


Event = namedtuple("Event", ('action', 'args'))
ObjectTuple = namedtuple('ObjectTuple', ['gid', 'name', 'object_type', 'position', 'args'])
OnlineTuple = namedtuple('OnlineTuple', ['name', 'frags'])