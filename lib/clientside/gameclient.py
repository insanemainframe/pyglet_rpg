#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import TILESIZE

from share.packer import pack, unpack
from share.gameprotocol.client_requestes import *
from share.point import *
from clientside.socket_client import SocketClient

class GameClient(SocketClient):
    "полуение и распаковка сообщений, антилаг"  
    accept_message = False
    
    
    def __init__(self, parent, hostname):
        SocketClient.__init__(self, hostname)
        self.antilag= False
        self.antilag_shift = Point(0,0) 
        self.shift = Point(0,0)

        self.parent = parent

    def accept(self):
        print 'waiting for acception'
        while 1:
            self.socket_loop()
            if self.accepted:
                print 'accepted'
                return True

    def accept_(self, message):
        action, message = unpack(message)
        print 'accept_', action, message
        if action=='ServerAccept':
            print 'accepted'
            self.accepted = True
        else:
            print 'not accepted'
            raise Exception('not accepted')

    def update(self):
        self.socket_loop()


        
    def send_move(self, vector, destination = False):
        message = pack(Move(vector, destination))
        self.put_message(message)
        #предварительное движение
        if vector and not self.shift and not self.antilag:
                step = vector * ((TILESIZE/5) / abs(vector))
                if step<vector:
                    shift = step
                else:
                    shift = vector
                self.parent.antilag_init(shift)
                self.antilag_shift = shift
                self.antilag = True
        
    def send_ball(self, vector):
        message = pack(Strike(vector))
        self.put_message(message)
    
    def send_skill(self):
        message = pack(Skill())
        self.put_message(message)

    def send_apply_item(self, slot):
        message = pack(ApplyItem(slot))
        self.put_message(message)
        
    def read(self, package):
        if package:
            unpacked = unpack(package)
            if unpacked:
                action, message = unpacked
                self.in_messages.append((action, message))

    def on_close(self):
        self.parent.on_close()