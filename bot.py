#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sys import argv, exit as sys_exit, path
from os import _exit as os_exit
path.append('lib')

from clientside.gameclient import GameClient
from share.mathlib import *
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
    
    def run(self):
        d = 1
        t = time()
        while not self.running.is_set():
            if not self.accepted:
                self.accept()
            else:
                
                sleep(ROUND_TIMER)
                self.update()
                self.in_messages = []
                if time()-t>1:
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

def main():
    if len(argv)==2:
        n = int(argv[1])
    else:
        n = int(argv[2])

    hostname = ask_hostname(HOSTNAME)
    running = Event()

    bots = [Bot(hostname, running = running) for i in range(n)]
    [bot.start() for bot in bots]
    [bot.join() for bot in bots]
        


if __name__=='__main__':
    main()
    
