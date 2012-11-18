#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from server_logger import debug

from engine.enginelib.meta import Container

from weakref import proxy, ProxyType
from collections import defaultdict

class Equipment(Container):
    def mixin(self, slots_num = 8):
        Container.mixin(self)
        self.__equipment_changed = True
    
    def handle_bind(self, item):
        self.__equipment_changed = True

    def handle_unbind(self, item):
        self.__equipment_changed = True

    def popitem(self, item_type):
        if item_type in self.equipment:
            item = self.equipment[item_type].pop()
            self.unbind(item)
        
    def apply_item(self, item_type):
        item = self.pop_related(item_type)
        if item:                
            if not item.effect():
                self.add_related(item)
                

    
    def look_items(self):
        result = self.get_related_dict()
        return result

    def is_equipment_changed(self):
        return self.__equipment_changed
            
            

