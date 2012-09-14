#!/usr/bin/env python
# -*- coding: utf-8 -*-
from random import randrange

from sys import path
path.append('../')

from game_lib.math_lib import *
from game_lib.map_lib import *

from config import *

class GameObject(World, Map):
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
        self.prev_position = Point(-1,-1)
        
    def move(self, vector=Point(0,0)):
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
        
        return self.move_vector

class Player(Movable, GameObject, MapObserver):
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
    
    def respawn(self):
        new_position = self.choice_position()
        for client in self.players:
            if self.players[client].guided:
                self.object_updates[client][self.name] = new_position - self.position
        self.position = new_position
        return self.position

        
        
class Ball(Movable, GameObject, MapObserver):
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
        s_name =  name
        objects = {name:(player.position, player.tilename+'_self' if name==s_name else player.tilename)
                    for name, player in self.players.items()}
        return world_size, position, tiles, objects, []
    
    def process_action(self):
        "совершаем действия игроками, возвращает векторы игрокам и устанавливает обновления"
        self.updates = {}
        for name, player in self.players.items():
            if player.guided:
                vector = Point(0,0)
                if self.client_requestes[name]:
                    action, message = self.client_requestes[name].pop()
                    if action=='move_message':
                         vector = message
                    elif action=='ball_message':
                        self.strike_ball(name, message)
                self.updates[name] = player.go(vector)
            else:
                if player.lifetime:
                    self.updates[name] = player.go()
                    player.lifetime-=1
                else:
                    #если срок жизни кончился - убиваем
                    del self.players[name]
                    self.updates[name] = 'remove'
            #очищаем
            self.client_requestes[name] = []
    
    def process_look(self):
        "смотрим"
        messages = {}
        for name, player in self.players.items():
            if player.guided:
                new_objects = self.new_objects
                updates = {}
                #lloking fo map
                if player.prev_position == player.position:
                    new_looked = []
                    
                else:
                    self.f_updates = []
                    tiles = player.look()
                    new_looked = tiles  - player.prev_looked
                    new_looked = [(Point(i,j),tilename) for (i,j), tilename in new_looked]
                    player.prev_looked = tiles
    
                move_vector = player.move_vector
                updates = self.updates
                #
                message = (move_vector, new_looked, new_objects, updates, [])
                self.client_responses[name].append((('look', message)))
        self.new_objects = {}
        self.updates = {}
        return messages
    
    def filter_updates(self, i,j):
        self.updates = {}
        for name, vector in self.updates.items():
            if isinstance(vector, Point):
                if vector/TILESIZE==Point(i,j):
                    updates[name] = vector
        return updates
    
    def strike_ball(self,player_name, vector):
        ball_name = 'ball%s' % self.ball_counter
        self.ball_counter+=1
        player_position = self.players[player_name].position
        ball = Ball(ball_name, player_position, vector, player_name)
        self.players[ball_name] = ball
        self.new_objects[ball_name] = (player_position, ball.tilename)
    
    def close_player(self,name):
        print 'close_player'
        self.updates[name]= 'remove'
        try:
            del self.players[name]
            del self.updates[name]
        except KeyError:
            print 'close_player keyerrror %s' % str(name)

        print 'close_player complete'



if __name__=='__main__':
    GameObject()
    m = Movable(Point(3000,3000), PLAYERSPEED)
    m.fragile = False
    m.crossing = True
    V = Point(-200,-200)
    v = m.move(V)
    while 1:
        mv = m.move(Point(0,0))
        v+=mv
        print 'mself.move_vector %s' % m.move_vector
        print 'mself.vector %s' % m.vector
        
        raw_input()

















            
