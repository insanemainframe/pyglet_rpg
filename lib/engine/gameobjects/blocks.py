#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from server_logger import debug

from random import randrange

from engine.mathlib import Cord, Position, ChunkCord, chance

from engine.enginelib.meta import *
from engine.gameobjects.misc import Misc
from engine.gameobjects.items import Item



class MetaBlock(OverLand, Misc, Breakable, Solid):
    """docstring for ClassName"""
    corpse = None
    def __init__(self):
        Misc.__init__(self)
        Solid.mixin(self, False)
        Breakable.mixin(self, self.hp)
        self.set_corpse(self.corpse)

    def handle_remove(self):
        Breakable.handle_remove(self)
        

class BlockSeed(Savable):
    def mixin(self, block_type):
        assert isinstance(block_type, type)

        self.__block_type = block_type

    def effect(self):
        debug ('try seed')
        new_block = self.__block_type()

        chunk = self.get_owner().chunk
        location = self.get_owner().location
        cord = self.get_owner().cord + Cord(0,1)

        if new_block.verify_position(location, chunk, cord, False):
            position = cord.to_position()
            debug ('seed %s' % position)
            self.get_owner().location.new_object(new_block, position = position)
            return True
        return False

        def __save__(self):
            return (self.__block_type.__name__)

        @classmethod
        def __load__(cls, location, block_type_name):
            assert isinstance(block_type_name, str)
            assert block_type_name in locals()

            block_type = locals()[block_type_name]
            return block_type()

class Brick(BlockSeed, Item):
    def __init__(self):
        Item.__init__(self)
        BlockSeed.mixin(self, Rock)


        


class Rock(Groupable, MetaBlock):
    count = 1
    radius = TILESIZE
    hp = 20
    corpse = Brick
    group_chance = 99.5
    cord_binded = True



class Wood(BlockSeed, Item):
    def __init__(self):
        Item.__init__(self)
        BlockSeed.mixin(self, AloneTree)







class AloneTree(Groupable, MetaBlock):
    gen_counter = 0
    count = 5
    radius = TILESIZE
    hp = 20
    corpse = Wood
        

    




