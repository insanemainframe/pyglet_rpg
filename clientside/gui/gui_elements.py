#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from client_config import *


from clientside.gui.window import Label, ClockDisplay


FPSDisplay = ClockDisplay

class Stats:
    hp = 0
    hp_value = 0
    kills = 0
    speed = 0
    deaths = 0
    damage = 0
    gold = 0
    skills = 0
    invisible = 0
    
    def __init__(self, surface):
        self.surface = surface
        
        y = 1
        dy = -15
        h = 600 #surface.height
        x = 100
        
        hp_mess = 'hp: %s/%s' % (self.hp, self.hp_value)
        self.hp_display = self.label(hp_mess, x, h+y*dy)
        y+=1
                          
        kills_mess = 'kills: %s' % self.kills
        self.kills_display = self.label(kills_mess, x, h+y*dy)
        y+=1
                          
        deaths_mess = 'deaths: %s' % self.deaths
        self.deaths_display = self.label(deaths_mess, x, h+y*dy)
        y+=1
        
        gold_mess = 'gold %s' % self.gold
        self.gold_display = self.label(gold_mess, x, h+y*dy)
        y+=1
        
        speed_mess = 'speed: %s' % self.speed
        self.speed_display = self.label(speed_mess, x, h+y*dy)
        y+=1
        
        damage_mess = 'damage: %s' % self.damage
        self.damage_display = self.label(damage_mess, x, h+y*dy)
        y+=1
        
        skills_mess = 'skills: %s' % self.skills
        self.skills_display = self.label(skills_mess, x, h+y*dy)
        y+=1
        
        invisible_mess = 'invisible: %s' % self.invisible
        self.invisible_display = self.label(invisible_mess, x, h+y*dy)
        y+=1
        
        
    def label(self, text, x,y):
        return Label(self.surface,text,x,y)
                          
    def update(self, hp, hp_value, speed, damage, gold, kills, deaths, skills, invisible):
        self.hp = hp
        self.hp_value = hp_value
        self.deaths = deaths
        self.kills = kills
        self.gold = gold
        self.speed = speed
        self.damage = damage
        self.skills = skills
        self.invisible = invisible
        
        self.speed_display.text = 'speed: %s' % self.speed
        self.damage_display.text = 'damage: %s' % self.damage
        self.hp_display.text = 'hp: %s/%s' % (self.hp, self.hp_value)
        self.kills_display.text = 'kills: %s' % self.kills
        self.deaths_display.text = 'deaths: %s' % self.deaths
        self.gold_display.text = 'gold: %s' % self.gold
        self.skills_display.text = 'skills: %s' % self.skills
        self.invisible_display.text = 'invisible: %s' % self.invisible
        
    def draw(self):
        self.surface.draw_background(0,0,'rightside')
        self.hp_display.draw()
        self.kills_display.draw()
        self.deaths_display.draw()
        self.gold_display.draw()
        self.speed_display.draw()
        self.damage_display.draw()
        self.skills_display.draw()
        self.invisible_display.draw()

class WorldDisplay:
    def __init__(self, surface):
        self.surface = surface
        x = 100
        self.worldname = Label(self.surface, 'World: None',x,400)
        self.position = Label(self.surface, 'Position: None', x, 440)
        self.worldsize = Label(self.surface, 'Size: None', x, 420)
    
    def change(self, name, size, position):
        self.worldname.text = 'World: %s' % name
        self.worldsize.text = 'Size: %sx%s' % (size, size)
        self.position.text = 'Position: %s' % position
    
    def update(self, position):
        self.position.text = 'Position: %s' % position
    
    def draw(self):
        self.worldname.draw()
        self.position.draw()
        self.worldsize.draw()

class PlayersOnlineDisplay:
    def __init__(self, surface):
        self.surface = surface
        self.x = 100
        self.y = 380
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

class LoadingScreen:
    def __init__(self, surface,):
        self.surface = surface
        x,y = self.surface.center.get()
        
        self.label = Label(self.surface,'Waiting for server response', x,y)
        
    def draw(self):
        self.label.draw()

