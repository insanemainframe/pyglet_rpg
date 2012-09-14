#!/usr/bin/env python
# -*- coding: utf-8 -*-
from random import randrange

from sys import path
path.append('../')

from game_lib.math_lib import *
from game_lib.map_lib import *

from config import *

class GameObject(World, Map, MapObject):
    "разделяемое состоние объектов карты"
    created = False
    def __init__(self):
        cls = GameObject
        World.__init__(self)
        
        cls.steps = Steps(self.size)
        cls.players = {}
        cls.new_objects = {}
        cls.object_updates = {}
        cls.created = True
        print 'created world', self.size
    @staticmethod
    def choice_position():
        cls = GameObject
        while 1:
            start = cls.size/2 - cls.size/10
            end = cls.size/2 + cls.size/10
            position = Point(randrange(start, end), randrange(start, end))
            i,j = position.get()
            if not cls.map[i][j] in BLOCKTILES:
                position = position*TILESIZE
                return position        

class Movable(GameObject):
    def __init__(self, position, speed):
        self.vector  = Point(0,0)
        self.speed = speed
        self.position = position
        self.move_vector = Point(0,0)
        self.prev_position = False
        
    def move(self, vector):
        #если вектор на входе определен, до определяем вектор движения объекта
        if vector:
            self.vector = vector
        #если вектор движения не достиг нуля, то продолжить движение
        if self.vector:
            #проверка столкновения
            i,j = get_cross(self.position, self.vector)
            cross_tile =  self.map[i][j]
            
            if cross_tile in BLOCKTILES or (cross_tile in TRANSTILES and not self.crossing):
                self.vector = Point(0,0)
                self.move_vector = Point(0,0)
                if self.fragile:
                    del self.players[self.name]
            else:
                part = self.speed / abs(self.vector) # доля пройденного пути в векторе
                move_vector = self.vector * part if part<1 else self.vector
                self.vector = self.vector - move_vector
                self.move_vector = move_vector
        else:
            self.move_vector = self.vector
        self.prev_position = self.position
        self.position+=self.move_vector
        #оповещаем других освоем движении
        return self.move_vector

class Player(Movable):
    tilename = 'player'
    fragile = False
    crossing = False
    guided = True
    prev_looked = set()
    alive = True
    striker = False
    def __init__(self, name, player_position, look_size):
        Movable.__init__(self, player_position, PLAYERSPEED)
        self.name = name
        self.look_size = look_size
    
    def go(self, vector):
        #self.steps.step(self.position)
        return self.move(vector)
        
    def _look(self):
        #ищем новые объекты
        new_objects = {}
        for name, (position, tilename) in self.new_objects[self.name].items():
            if name!=self.name:
                new_objects[name] = (position, tilename)
        self.new_objects[self.name] = {}
        #ищем бновления объектов
        updates = self.object_updates[self.name]
        self.object_updates[self.name] = {}
        #steps
        steps = [] #self.steps.look(self.position, self.look_size)
        return self.move_vector, new_looked, new_objects, updates, steps
    
    def respawn(self):
        new_position = self.choice_position()
        for client in self.players:
            if self.players[client].guided:
                self.object_updates[client][self.name] = new_position - self.position
        self.position = new_position
        return self.position
    
    def __del__(self):
        #удаляем себя из списка объектов
        del self.new_objects[self.name]
        del self.object_updates[self.name]
        #оповещаем других игроков о выходе
        for client, update_dict in self.object_updates.items():
            self.object_updates[client][self.name] = 'remove'
        
        
class Ball(Movable, GameObject):
    crossing = True
    tilename = 'ball'
    guided = False
    fragile = True
    def __init__(self, name, position, direct, striker_name):
        Movable.__init__(self, position, BALLSPEED)
        self.lifetime = BALLLIFETIME
        self.name = name
        self.striker =  striker_name
        one_step = Point(BALLSPEED,BALLSPEED)
        self.direct = direct*(abs(one_step)/abs(direct))
        self.radius = BALLRADIUS
        #оповещаем
        self.alarm()
    
    def collision(self):
        for name, player in self.players.items():
            if player.guided and name!=self.striker:
                dist = abs(self.position-player.position)
                if dist<self.radius:
                    self.players[name].alive= False
                    print 'BOMB %s' % name
    def go(self):
        result = self.move(self.direct)
        self.collision()
        return result
    
    def __del__(self):
        for client, update_dict in self.object_updates.items():
            self.object_updates[client][self.name] = 'remove'
        
        
class Game(GameObject):
    updates = {}
    new_objects = {}
    ball_counter=0
    def __init__(self):
        GameObject.__init__(self)
    
    def create_player(self, name):
        self.players[name] = Player(name, self.choice_position(), 7)
        player =  self.players[name]
        world_size = self.size
        position = player.position
        #
        self.new_objects[name] = (position, player.tilename)
        #обзор
        tiles = [(Point(i,j), tilename) for ((i,j), tilename) in player.look()]
        #новые объекты
        s_name, s_tilename, s_position = name, player.tilename, player.position
        objects = {name:(s_position, s_tilename+'_self' if name==s_name else s_tilename)
                    for name, player in self.players.items()}
        return world_size, position, tiles, objects, []
    
    def process_action(self, messages):
        "совершаем действия игроками, возвращает векторы игрокам и устанавливает обновления"
        #print 'process_action'
        self.updates = {}
        for name, player in self.players.items():
            if player.guided:
                try:
                    for action, message in messages[name]:
                        vector = None
                        if action=='move_message':
                             vector = message
                        elif action=='ball_message':
                            self.strike_ball(message)
                        self.updates[name] = player.go(vector)
                except:
                    print 'guided action error %s' % messages[name]
            else:
                if player.lifetime:
                    self.updates[name] = player.go()
                    player.lifetime-=1
                else:
                    #если срок жизни кончился - убиваем
                    del self.players[name]
                    self.updates[name] = 'remove'
        
        #print 'process_action complete'
    
    def process_look(self):
        "смотрим"
        #print 'process_look'
        messages = {}
        for name, player in self.players.items():
            tiles = player.look()
            new_objects = self.new_objects
            updates = {}
            print 'looking for updates'
            for ((i,j), tilename) in tiles:
                updates.update(self.filter_updates(i,j))
            print 'looking for updates complete'
            new_looked = tiles # - player.prev_looked
            player.prev_looked = tiles
            move_vector = player.move_vector
            #
            updates = self.updates
            #
            message = (move_vector, new_looked, new_objects, updates, [])
            print 'move %s' % move_vector
            messages[name]=(('look', message))
        #print 'process_look complete'
        self.new_objects = {}
        return messages
    
    def filter_updates(self, i,j):
        #print 'filter update'
        updates = {}
        for name, vector in self.updates.items():
            if vector/TILESIZE==Point(i,j):
                updates[name] = vector
        #print 'filter_update complete'
        return updates
    
    def strike_ball(self,name, vector):
        name = 'ball%s' % self.ball_counter
        self.ball_counter+=1
        position = self.players[client_name].position
        self.players[name] = Ball(name, position, vector, client_name)
    
    def close_player(self,name):
        print 'close_player'
        del self.players[name]
        del self.updates[name]
        for player_name in self.players:
            self.updates[player_name][name] = 'remove'
        print 'close_player complete'



























            
