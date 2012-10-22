#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from collections import defaultdict

class Equipment:
    def __init__(self):
        self.equipment = defaultdict(list)
        self.equipment_changed = False
    
    def add_item(self, item):
        item_type = item.__class__.__name__
        
        self.equipment_changed  = True
        
        self.bind(item)
        
        self.equipment[item_type].append(item)
    
    def pop_item(self, item_type):
        if item_type in self.equipment:
            item = self.equipment[item_type].pop()
            self.unbind(item)
        
    def apply_item(self, slot):
        try:
            item_type = self.equipment.keys()[slot]
            item = self.equipment[item_type].pop()
            
            item.effect()
            
            self.equipment_changed  = True
        except IndexError:
            pass
    
    def look_items(self):
        result = {}
        for item_type, item_list in self.equipment.items():
            if item_list:
                result[item_type] = len(item_list)
        return result
            
            

