#!/usr/bin/env python
# -*- coding: utf-8 -*-
from game_lib.math_lib import *
from game_lib.map_lib import *
from game_lib import game
from game_lib.engine_lib import *


from config import *


#####################################################################

class MapObserver(MapTools):
    "класс объекта видящего карту"
    prev_looked = set()
    prev_observed = set()
    
    def look(self):
        "возвращает список координат видимых клеток из позиции position, с координаами относительно начала карты"
        position = self.position
        rad = self.look_size
        I,J = (position/TILESIZE).get()
        #
        new_updates = {}
        #
        observed = set()
        looked = set()
        for i in xrange(I-rad, I+rad):
            for j in xrange(J-rad, J+rad):
                diff = hypot(I-i,J-j) - rad
                if diff<0:
                    i,j = self.resize(i), self.resize(j)
                    try:
                        tile_type = game.world.map[i][j]
                    except IndexError, excp:
                        pass
                    else:
                        looked.add((Point(i,j), tile_type))
                        observed.add((i,j))
                        if (i,j) in game.updates:
                            for uid, (name, object_type, position, action, args) in game.updates[(i,j)]:
                                if name==self.name:
                                    object_type = 'self'
                                new_updates[uid] = (name, object_type, position, action, args)

        new_looked = looked - self.prev_looked
        self.prev_looked = looked
        self.prev_observed = observed
        return new_looked, observed, new_updates
    

#####################################################################
class Movable:
    "класс движущихся объектов"
    BLOCKTILES = []
    SLOWTILES = {}
    def __init__(self, position, speed):
        self.vector  = NullPoint
        self.speed = speed
        self.position = position
        self.move_vector = NullPoint
        self.prev_position = Point(-1,-1)
        self.moved = False
        
    def move(self, vector=NullPoint):
        if self.moved:
            raise ActionDenied
        #если вектор на входе определен, до определяем вектор движения объекта
        if vector:
            self.vector = vector
        #если вектор движения не достиг нуля, то продолжить движение
        if self.vector:
            #проверка столкновения
            part = self.speed / abs(self.vector) # доля пройденного пути в векторе
            move_vector = self.vector * part if part<1 else self.vector
            #
            crossed = get_cross(self.position, move_vector)
            #print 'crossed', crossed
            resist = 1
            for (i,j), cross_position in crossed:
                cross_tile =  game.world.map[i][j]
                if cross_tile in self.BLOCKTILES:
                    move_vector = (cross_position - self.position)*0.99
                    self.vector = move_vector
                    #если объект хрупкий - отмечаем для удаления
                    if self.fragile:
                        self.REMOVE = True
                    break
                if cross_tile in self.SLOWTILES:
                    resist = self.SLOWTILES[cross_tile]
            move_vector *= resist
            self.vector = self.vector - move_vector
            self.move_vector = move_vector
        else:
            self.move_vector = self.vector
        self.prev_position = self.position
        self.position+=self.move_vector
        self.moved = True
        #name, position, vector, action, args
        altposition = self.position
        #добавляем событие
        game.add_update( self.name, self.prev_position, altposition, 'move', [self.move_vector.get()])
    
    def complete_round(self):
        self.moved = False
    
    def handle_request(self):
        return self.move_vector
    
    def update(self):
        if not self.moved:
            return self.move()
####################################################################
class Respawnable:
    "класс перерождающихся объектов"
    respawned = False
    def respawn(self):
        new_position = game.choice_position(Player)
        vector = new_position - self.position
        self.position = new_position
        game.add_update(self.name, self.prev_position, NullPoint, 'remove')
        game.add_update(self.name, self.position, NullPoint, 'move', [NullPoint.get()])
        self.respawn_message = 'respawn', self.position
        self.alive = True
        self.respawned = True

    
    def handle_response(self):
        if self.respawned:
            self.respawned = False
            return [self.respawn_message]
        else:
            print 'Respawned error'
    
####################################################################
class Temporary:
    "класс объекта с ограниченным сроком существования"
    def __init__(self, lifetime):
        self.lifetime = lifetime
    
    def update(self):
        self.lifetime-=1
#####################################################################
class Striker:
    def __init__(self, strike_speed):
        self.strike_counter = 0
        self.strike_speed = strike_speed
    
    def strike_ball(self, vector):
        if self.strike_counter>self.strike_speed:
            raise ActionDenied
        else:
            ball_name = 'ball%s' % game.ball_counter
            game.ball_counter+=1
            ball = Ball(ball_name, self.position, vector, self.name)
            game.new_object(ball)
            self.strike_counter+=1
            
            
    def update(self):
        self.strike_counter = 0
    
    def complete_round(self):
        self.striked = False
        
        
    
#####################################################################
class Player(Movable, MapObserver, Striker, Guided, Respawnable):
    "класс игрока"
    tilename = 'player'
    mortal = False
    human = True
    fragile = False
    radius = TILESIZE/2
    prev_looked = set()
    alive = True
    object_type = 'Player'
    BLOCKTILES = ['stone', 'forest', 'ocean']
    SLOWTILES = {'water':0.5, 'bush':0.3}

    
    def __init__(self, name, player_position, look_size):
        GameObject.__init__(self, name)
        Movable.__init__(self, player_position, PLAYERSPEED)
        Striker.__init__(self,1)
        self.name = name
        self.look_size = look_size
    
    def handle_response(self):
        if not self.respawned:
            move_vector = Movable.handle_request(self)
            new_looked, observed, updates = self.look()
    
            return [('look', (move_vector, new_looked, observed, updates, []))]
        else:
            return Respawnable.handle_response(self)
    
    def ball(self, vector):
        self.strike_ball(vector)
    
    def complete_round(self):
        Movable.complete_round(self)
        Striker.complete_round(self)
    
    def update(self):
        Movable.update(self)
        Striker.update(self)
    
    def die(self):
        return None, None


#####################################################################        
class Ball(Temporary, Movable,GameObject):
    "класс снаряда"
    tilename = 'ball'
    mortal = True
    human = False
    guided = False
    fragile = True
    radius = TILESIZE/2
    object_type = 'Ball'
    BLOCKTILES = ['stone', 'forest']
    def __init__(self, name, position, direct, striker_name):
        GameObject.__init__(self, name)
        Movable.__init__(self, position, BALLSPEED)
        Temporary.__init__(self, BALLLIFETIME)
        self.striker =  striker_name
        one_step = Point(BALLSPEED,BALLSPEED)
        self.direct = direct*(abs(one_step)/abs(direct))
    
    def update(self):
        Movable.move(self, self.direct)
        Movable.update(self)
        Temporary.update(self)
                    
    def die(self):
        game.add_update(self.position, NullPoint, 'explode', [])
