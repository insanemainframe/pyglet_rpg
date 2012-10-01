#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from client_config import *


from clientside.window import GameWindow, create_tile, Label, ClockDisplay


FPSDisplay = ClockDisplay

class Stats(GameWindow):
    hp = 0
    hp_value = 0
    kills = 0
    speed = 0
    deaths = 0
    damage = 0
    gold = 0
    skills = 0
    
    def __init__(self):

        
        hp_mess = 'hp: %s/%s' % (self.hp, self.hp_value)
        self.hp_display = self.label(hp_mess, 70, 20)
                          
        kills_mess = 'kills: %s' % self.kills
        self.kills_display = self.label(kills_mess, 70, 40)
                          
        deaths_mess = 'deaths: %s' % self.deaths
        self.deaths_display = self.label(deaths_mess, 70, 60)
        
        gold_mess = 'gold %s' % self.gold
        self.gold_display = self.label(gold_mess, 70, 80)
        
        speed_mess = 'speed: %s' % self.speed
        self.speed_display = self.label(speed_mess, 70, 100)
        
        damage_mess = 'damage: %s' % self.damage
        self.damage_display = self.label(damage_mess, 70, 120)
        
        skills_mess = 'skills: %s' % self.skills
        self.skills_display = self.label(skills_mess, 70, 140)
        
        
    def label(self, text, x,y):
        return Label(text,x,y)
                          
    def update(self, hp, hp_value, speed, damage, gold, kills, deaths, skills):
        self.hp = hp
        self.hp_value = hp_value
        self.deaths = deaths
        self.kills = kills
        self.gold = gold
        self.speed = speed
        self.damage = damage
        self.skills = skills
        
        self.speed_display.text = 'speed: %s' % self.speed
        self.damage_display.text = 'damage: %s' % self.damage
        self.hp_display.text = 'hp: %s/%s' % (self.hp, self.hp_value)
        self.kills_display.text = 'kills: %s' % self.kills
        self.deaths_display.text = 'deaths: %s' % self.deaths
        self.gold_display.text = 'gold: %s' % self.gold
        self.skills_display.text = 'skills: %s' % self.skills
        
    def draw(self):
        self.hp_display.draw()
        self.kills_display.draw()
        self.deaths_display.draw()
        self.gold_display.draw()
        self.speed_display.draw()
        self.damage_display.draw()
        self.skills_display.draw()



class LoadingScreen:
    def __init__(self, point):
        x,y = point.get()
        self.label = Label('Waiting for server response', x,y)
        
    def draw(self):
        self.label.draw()

