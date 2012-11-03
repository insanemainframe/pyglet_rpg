#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from client_config import *

from share.point import Point
from clientside.gui.window import Label, TextLabel, ClockDisplay, create_tile, create_label, GuiElement
from clientside.gui.gui_lib import Drawable
from clientside.client_objects import static_objects as item_types


from pyglet.window.key import *
from functools import partial

FPSDisplay = ClockDisplay



class Stat:
    j = 1
    dy = -15
    x = 30
    
    def __init__(self, surface, template):
        self.template = template
        self.label = Label(surface, template, self.x, self.y+Stat.j*self.dy, False)
        Stat.j+=1
        

    def update(self, *args):
        self.label.text = self.template % args

    def draw(self):
        self.label.draw()


class StatsDisplay(GuiElement):
    def __init__(self, surface):
        GuiElement.__init__(self, surface)
        Stat.y = 670
        stat = partial(Stat, surface)

        self.hp = stat('hp: %s/%s')
        self.kills = stat('kills: %s')
        self.speed = stat('speed: %s')
        self.deaths = stat('deaths: %s')
        self.damage = stat('damage: %s')
        self.gold = stat('gold: %s')
        self.skills = stat('skills: %s')
        self.invisible = stat('invisible: %s')
                                  
    def update(self, hp, hp_value, speed, damage, gold, kills, deaths, skills, invisible):
        self.hp.update(hp, hp_value)
        self.deaths.update(deaths)
        self.kills.update(kills)
        self.gold.update(gold)
        self.speed.update(speed)
        self.damage.update(damage)
        self.skills.update(skills)
        self.invisible.update(invisible)
        
    def draw(self):
        self.hp.draw()
        self.kills.draw()
        self.deaths.draw()
        self.gold.draw()
        self.speed.draw()
        self.damage.draw()
        self.skills.draw()
        self.invisible.draw()



class locationDisplay(GuiElement):
    x = 30
    template = """<font color=white>
                <br>location: %s
                <br>Size: %s 
                <br>Position: %s
                </font>"""
    def __init__(self, surface):
        GuiElement.__init__(self, surface)

        self.y = 500
        self.label = TextLabel(self.surface, self.template, self.x, self.y, 100)
        self.name, self.size = '', 0
        
    
    def change(self, name, size, position):
        self.label.text = self.template % (name, size, position)
        self.name = name
        self.size = size
    
    def update(self, position):
        self.label.text = self.template % (self.name, self.size, position)
    
    def draw(self):
        self.label.draw()



class EquipmentDisplay(Drawable, GuiElement):
    control_keys = [F1, F2, F3, F4, F5, F6, F7, F8]
    def __init__(self, surface):
        GuiElement.__init__(self, surface)
        Drawable.__init__(self)
        self.slots = {}
        self.key_to_num =  {k:i+1 for i,k in enumerate(self.control_keys)}
        
        self.x = 100
        self.y = 300
        self.dy = 40
        self.tilenames = {}
        for item_type_name in dir(item_types):
            item_type = getattr(item_types, item_type_name)
            if hasattr(item_type, 'tilename'):
                tilename = item_type.tilename
                type_name = item_type.__name__
                
                self.tilenames[type_name] = tilename
        
        self.title = Label(self.surface, 'Equipment:', self.x, self.y)
        self.tiles = []
    
    def update(self, items_dict):
        self.tiles = []
        
        yn = 0
        
        n = 1

        for item, number in items_dict.items():
            point = Point(self.x, self.y - yn*self.dy)
            tilename = self.tilenames[item]
            
            width = self.surface.tiledict[tilename].width
            height = self.surface.tiledict[tilename].height

            shift = Point(width, height/2)

            sprite = create_tile(point  - shift, tilename)
            label = create_label("F-%s [%s]" % (n, number), point)
            
            self.tiles.append(label)
            self.tiles.append(sprite)

            self.slots[n] = item
            
            yn+=1
            n+=1
    
    def on_key_press(self, symbol, modifiers):
        "движение с помощью клавиатуры"
        if symbol in self.control_keys:
            self.pressed[symbol] = True
            slot = self.key_to_num[symbol]
            if slot in self.slots:
                item_type = self.slots[slot]
                self.surface.window.client.send_apply_item(item_type)
            return True
        return False

    def draw(self):
        self.title.draw()
        Drawable.draw(self)
            

class PlayersOnlineDisplay(GuiElement):
    def __init__(self, surface):
        GuiElement.__init__(self, surface)
        self.x = 100
        self.y = 400
        self.title = Label(self.surface, 'Online:', self.x, self.y)
        self.plist = []
    
    def update(self, player_list):
        self.plist = []
        i = 0
        for player, frags in player_list:
            i+=1
            text = '%s [%s]' % (player,frags)
            label = Label(self.surface, text, self.x, self.y-i*15)
            self.plist.append(label)
        
    
    def draw(self):
        self.title.draw()
        [label.draw() for label in self.plist]


class LoadingScreen(GuiElement):
    def __init__(self, surface,):
        GuiElement.__init__(self, surface)
        x,y = self.surface.center.get()
        
        self.label = Label(self.surface,'Waiting for server response', x,y)
        
    def draw(self):
        self.label.draw()


class HelpScreen(GuiElement):
    control_keys = [H]
    help_file = 'data/help.html'
    text = '<font color="white">Press "H" for help</font>'
    def __init__(self, surface,):
        GuiElement.__init__(self, surface)
        x,y = 50, self.surface.height-50
        
        with open(self.help_file, 'r') as hfile:
            self.help_text = hfile.read()

        self.label = TextLabel(self.surface, self.text, x,y, self.surface.width)


    def on_key_press(self, symbol, modifiers):
        "движение с помощью клавиатуры"
        if symbol in self.control_keys:
            print 'pressed'
            if symbol in self.pressed:
                del self.pressed[symbol]
                self.label.text = self.text

            else:
                self.label.text = self.help_text
                self.pressed[symbol] = True
            return True
        return False

    def draw(self):
        self.label.draw()
