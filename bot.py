#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sys import argv, exit as sys_exit, path
from os import _exit as os_exit
path.append('lib')

from clientside.gameclient import GameClient
from share.point import *
from share.ask_hostname import ask_hostname
from config import *
from time import sleep, time


from threading import Thread
from multiprocessing import Process, Event




from engine.mathlib import chance
from random import randrange



class Bot(GameClient, Process):
    def __init__(self, hostname, running):

        GameClient.__init__(self, self, hostname)
        Process.__init__(self)
        self.running = running
        
        self.shift = Point(0,0)
        self.antilag_init = lambda *args: args
        self.objects = BotObjects()
    
    def run(self):
        d = 1
        t = time()
        while not self.running.is_set():
            if not self.accepted:
                self.accept()
            else:
                
                sleep(ROUND_TIMER)
                self.update()
                for action, message in self.in_messages:
                    if action=='Respawn':
                        new_position = message                
                        self.objects.set_position(new_position)

                    elif action=='MoveCamera':
                        move_vector = message
                        self.objects.move_position(move_vector)

                    elif action=='LookObjects':
                        new_players, events, old_players = message
                        self.objects.add(new_players)
                        self.objects.remove(old_players)

                    elif action=='Newlocation':
                        wold_name, location_size, position, background = message
                        self.objects.set_position(position)

                self.in_messages = []
                self.objects.update()
                if time()-t>1:
                    if self.objects.vector:
                        self.send_move(self.objects.vector)
                    if self.objects.strike_vector:
                        self.send_ball(self.objects.strike_vector)
                    if not (self.objects.vector or self.objects.strike_vector):
                        d*=-1
                        x = randrange(-500, 500)
                        y = randrange(-500, 500)
                        if d>0:
                            self.send_move(Point(x,y))
                        else:
                            self.send_ball(Point(x,y))
                    if chance(10):
                        self.send_skill()

                    if chance(10):
                        self.send_apply_item(randrange(8))
                    t = time()


    def on_close(self, a=''):
        self.running.set()
        print 'close'
        sys_exit()
        os_exit() 



TELEPORTS = ['Cave', 'DeepCave', 'Stair', 'UpStair']
ITEMS = ['Lamp', 'Sceptre', 'HealPotion', 'Sword', 'Armor', 'Sceptre', 'SpeedPotion', 'Gold', 'Cloak']
MONSTERS = ['Bat', 'Zombie', 'Ghast', 'Lych']

class BotObjects:
    update_timer = 5
    def __init__(self):
        self.players = {}
        self.position = False
        self.vector = False
        self.strike_vector = False
        self.update_time = time()

    def set_position(self, position):
        self.position = position

    def move_position(self, vector):
        self.position+=vector

    def add(self, players):
        for gid, name, object_type, position, args in players:
            self.players[gid] = name, object_type, position, args

    def update(self):
        if time()> self.update_time+self.update_timer:
            
            for name, object_type, position, args in self.players.values():
                if object_type in TELEPORTS:
                    print 'teleport'
                    self.vector = position - self.position
                    if chance(30):  break

                elif object_type in ITEMS:
                    print 'item'
                    self.vector = position - self.position
                    if chance(30):  break

                elif object_type in MONSTERS:
                    print 'monster'
                    self.strike_vector = position - self.position
                    if chance(30):  break
            else:
                self.update_time = time()

    def remove(self, players):
        for gid, args in players:
            if gid in self.players:
                del self.players[gid]


def main():
    if len(argv)==2:
        n = int(argv[1])
    else:
        n = int(argv[2])

    hostname = ask_hostname(HOSTNAME)
    running = Event()

    for i in range(n):
        bot = Bot(hostname, running = running)
        bot.start()
        
    while not running.is_set():
        pass

if __name__=='__main__':
    main()
    
