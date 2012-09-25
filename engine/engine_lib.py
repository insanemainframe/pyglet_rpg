#!/usr/bin/env python
# -*- coding: utf-8 -*-
from share.mathlib import *
from share.map import *
from mathlib import *
import game

#

class UnknownAction(Exception):
    pass


class ActionDenied(Exception):
    pass

class ActionError(Exception):
    def __init__(self, message):
        self.message = message
    
    def __str__(self):
        return 'ActionError: %s' % self.message
        
#####################################################################
class GameObject:
    alive = True
    def __init__(self, name, position):
        self.name = name
        self.position = position
    
    def handle_action(self, action, args):
        if hasattr(self, action):
            return getattr(self, action)(*args)
        else:
            raise ActionError('no action %s' % action)
    
    def update(self):
        pass
    
    def add_event(self, *args):
        game.add_event(self.name, *args)
    def handle_response(self):
        return []

#####################################################################



class Guided(GameObject):
    "управляемый игроком объекта"
    pass

#####################################################################

class MapObserver(MapTools):
    "класс объекта видящего карту"
    prev_looked = set()
    prev_observed = set()
    def __init__(self, look_size):
        MapTools.__init__(self, game.size, game.size)
        self.look_size = look_size
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
                                    object_type = 'Self'
                                new_updates[uid] = (name, object_type, position, action, args)

        new_looked = looked - self.prev_looked
        self.prev_looked = looked
        self.prev_observed = observed
        return new_looked, observed, new_updates
    

#####################################################################
class MovableShare:
    @staticmethod
    def new_player(player):
        if hasattr(MovableShare, 'position_list'):
            MovableShare.player_list[player.name] = player
        else:
            MovableShare.player_list = {}
    
    @staticmethod
    def update_player(player):
        MovableShare.player_list[player.name] = player
        for Player in MovableShare.player_list.values():
            distance = abs(Player.position - player.position)
            if distance <= Player.radius+player.radius:
                if isinstance(Player, Mortal) and isinstance(player,Deadly):
                    if player.fraction!=Player.fraction:
                        player.hit(Player.damage)
                        Player.collission()
                        if isinstance(Player, Fragile):
                            Player.REMOVE = True
        
        
    
    @staticmethod
    def remove_player(player):
        del MovableShare.player_list[player.name]
        
            
class Movable(MovableShare):
    "класс движущихся объектов"
    BLOCKTILES = []
    SLOWTILES = {}
    def __init__(self,  speed):
        self.vector  = NullPoint
        self.speed = speed
        self.move_vector = NullPoint
        self.prev_position = Point(-1,-1)
        self.moved = False
        self.new_player(self)
    
    
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
            #определяем столкновения с тайлами
            move_vector = self._tile_collission(move_vector)
            
            
            
            self.vector = self.vector - move_vector
            self.move_vector = move_vector
        else:
            self.move_vector = self.vector
        self.prev_position = self.position
        self.position+=self.move_vector
        
        self.moved = True
        
        altposition = self.position
        #добавляем событие
        self.add_event(self.prev_position, altposition, 'move', [self.move_vector.get()])
        self.update_player(self)
    
    def _tile_collission(self, move_vector):
        "определения пересечяения вектора с непрохоодимыми и труднопроходимыми тайлами"
        resist = 1
        crossed = get_cross(self.position, move_vector)
        for (i,j), cross_position in crossed:
            cross_tile =  game.world.map[i][j]
            if cross_tile in self.BLOCKTILES:
                move_vector = (cross_position - self.position)*0.99
                self.vector = move_vector
                #если объект хрупкий - отмечаем для удаления
                if isinstance(self, Fragile):
                    self.REMOVE = True
                break
            if cross_tile in self.SLOWTILES:
                resist = self.SLOWTILES[cross_tile]
        move_vector *= resist
        return move_vector
        
    
    def complete_round(self):
        self.moved = False
    
    def handle_request(self):
        return self.move_vector
    
    def update(self):
        if not self.moved:
            return self.move()
    def __del__(self):
        self.remove_player(self)
        print 'remove movable'
    
####################################################################

class Stalker:
    "объекты охотящиеся за игроками"
    def __init__(self, look_size):
        self.look_size = look_size
    
    def hunt(self):
        for player in game.players.values():
            if isinstance(player, Guided):
                distance = player.position - self.position
                if True: #abs(distance/TILESIZE)<self.look_size:
                    return player.position - self.position
        return None
        
class Deadly:
    "класс для живых объектов"
    def __init__(self, hp, heal_speed=0.01, death_time=20):
        self.hp_value = hp
        self.hp = hp
        self.heal_speed = heal_speed
        self.alive = True
        self.death_time = death_time
        self.death_time_value = death_time
    
    def hit(self, hp):
        self.hp-=hp
        if self.hp<=0:
            self.die()
            self.hp = self.hp_value
    
    def update(self):
        if self.alive:
            if self.hp<self.hp_value:
                self.hp+=self.heal_speed
        else:
            if self.death_time>0:
                self.death_time-=1
                self.add_event(self.position, NullPoint, 'die',  [])
            else:
                self.death_time = self.death_time_value
                self.REMOVE = True
    
    def die(self):
        self.alive = False


class Fragile:
    "класс для объекто разбивающихся при столкновении с тайлами"
    pass
    
class Mortal:
    "класс для объектов убивающих живых при соприкосновении"
    striker = None
    def __init__(self, damage=1):
        self.damage = damage
####################################################################

class Respawnable:
    "класс перерождающихся объектов"
    respawned = False
    def __init__(self, delay, distance):
        self.respawn_delay = delay
        self.respawn_distance = distance
        
    def remove(self):
        print 'respawning %s' % self.name
        new_position = game.choice_position(self, 10 ,self.position)
        vector = new_position - self.position
        self.position = new_position
        game.add_event(self.name, self.prev_position, NullPoint, 'remove')
        game.add_event(self.name, self.position, NullPoint, 'move', [NullPoint.get()])
        self.respawn_message = 'Respawn', self.position
        self.alive = True
        self.respawned = True
        return False

    
    def handle_response(self):
        print 'respawn_message %s' % self.name
        self.respawned = False
        return [self.respawn_message]

class DiplomacySubject:
    def __init__(self, fraction):
        self.fraction = fraction
####################################################################
class Temporary:
    "класс объекта с ограниченным сроком существования"
    def __init__(self, lifetime):
        self.lifetime = lifetime
    
    def update(self):
        self.lifetime-=1
