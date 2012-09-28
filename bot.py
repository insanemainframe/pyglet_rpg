#!/usr/bin/env python
# -*- coding: utf-8 -*-
from clientside.network import Client
from share.mathlib import *
from config import *
from time import sleep
from sys import argv
from threading import Thread
from multiprocessing import Process



from random import randrange

class Bot(Client, Process):
    def __init__(self):
        self.hostname = HOSTNAME
        Client.__init__(self)
        Process.__init__(self)
        
        self.wait_for_accept()
        print 'accepted'
        self.shift = NullPoint
        self.antilag_init = lambda *args: args
    def run(self):
        d = 1
        while 1:
            self.socket_loop()
            self.in_messages = []
            sleep(1)
            d*=-1
            x = randrange(-40, 40)
            y = randrange(-40, 40)
            if d:
                self.send_move(Point(x,y))
            else:
                self.send_ball(Point(x,y))
9
for i in range(int(argv[1])):
    bot = Bot()
    bot.start()
    
while 1:
    pass
    
