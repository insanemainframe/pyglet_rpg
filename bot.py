#!/usr/bin/env python
# -*- coding: utf-8 -*-
from clientside.network import GameClient
from share.mathlib import *
from config import *
from time import sleep, time
from sys import argv, exit
from threading import Thread
from multiprocessing import Process


from engine.mathlib import chance
from random import randrange

class Bot(GameClient, Process):
    def __init__(self):
        self.hostname =  HOSTNAME 
        #
        GameClient.__init__(self)
        Process.__init__(self)
        
        self.wait_for_accept()
        print 'accepted'
        self.shift = NullPoint
        self.antilag_init = lambda *args: args
    def run(self):
        d = 1
        t = time()
        while 1:
            sleep(ROUND_TIMER)
            self.socket_loop()
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
                t = time()
    def on_close(self, a=''):
        exit()

def main():
    n = argv[1]

    for i in range(int(argv[1])):
        bot = Bot()
        bot.start()
        
    while 1:
        pass

if __name__=='__main__':
    main()
    
