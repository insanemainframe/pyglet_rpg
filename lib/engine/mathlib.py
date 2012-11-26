# -*- coding: utf-8 -*-
from math import hypot


from share.mathlib import *

from config import *
from share.logger import print_log


########################################################################
from random import random

def chance(n):
    n = n/100.0
    if random()<n:
        return True
    else:
        return False

