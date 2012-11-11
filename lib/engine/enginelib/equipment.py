#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from engine.enginelib.meta import Container

from weakref import proxy, ProxyType
from collections import defaultdict

class Equipment(Container):
    def mixin(self, slots_num = 8):
        Container.mixin(self)
        
        self.slots_num = slots_num
        self.equipment = defaultdict(list)
        self._equipment_changed = False
    
    def handle_bind(self, item):
        item_type = item.__class__.__name__
        
        self._equipment_changed  = True
                
        self.equipment[item_type].append(proxy(item))

        return True
    
    def pop_item(self, item_type):
        if item_type in self.equipment:
            item = self.equipment[item_type].pop()
            self.unbind(item)
        
    def apply_item(self, item_type):
        try:
            item = self.equipment[item_type].pop()
            item.effect()

            self.pop_related(item.name)
            
            self._equipment_changed  = True
        except IndexError:
            pass
    
    def look_items(self):
        result = {}
        for item_type, item_list in self.equipment.items():
            if item_list:
                result[item_type] = len(item_list)
        self._equipment_changed = False
        return result

    def is_equipment_changed(self):
        return self._equipment_changed
            
            

