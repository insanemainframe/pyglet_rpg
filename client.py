#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pyglet
from pyglet.gl import *

from math import hypot
from sys import exit
from collections import defaultdict

from game_lib.math_lib import Point, collinear
from game_lib.gui_lib import *
from game_lib.ask_hostname import AskHostname
from game_lib.map_lib import MapTools
from game_lib.client_lib import Client
from game_lib.protocol_lib import pack, unpack

from config import *
from game_lib.logger import CLIENTLOG as LOG

class Gui(GameWindow, DeltaTimerObject, Client, InputHandle, pyglet.window.Window, AskHostname):
    accepted = False
    shift = Point(0,0)
    vector = Point(0,0)
    hostname = HOSTNAME
    def __init__(self, height, width):
        #инициализация родтельских классов
        AskHostname.__init__(self, HOSTNAME)
        pyglet.window.Window.__init__(self, width, height)
        GameWindow.__init__(width, height)
        DeltaTimerObject.__init__(self)
        InputHandle.__init__(self)
        Client.__init__(self)
        
        self.objects = ObjectsView()
        
        #текст загрузки
        self.loading = LoadingScreen(self.center)
        
        #счетчик фпс
        self.fps_display = pyglet.clock.ClockDisplay()
        #
        self.accept()
    
    def accept(self):
        accept_data = self.wait_for_accept()
        if accept_data:
            world_size, position, tiles, observed, updates, steps = accept_data
        
            print 'accepteed position %s tiles %s' % (position, len(tiles))
    
            self.land = LandView(world_size, position, tiles, observed)
            self.objects.insert(updates)
            self.accepted = True
            self.loading = False
            #устанавливаем обновление на каждом кадре
            pyglet.clock.schedule_interval(self.round_update, self.timer_value)
            pyglet.clock.schedule(self.update)
        else:
            print 'Accepting failed'
    
    def update(self, dt):
        #перехвт ввода
        self.handle_input()
        #обработка соединения
        self.socket_loop()
        #нахождение проходимого на этом фрейме куска вектора
        delta = self.get_delta()
        vector = self.shift*delta
        if vector> self.shift:
            vector = self.shift
        self.shift = self.shift - vector
        #двигаем камеру
        self.land.move_position(vector)
        #обновляем карту и объекты
        self.land.update()
        self.objects.update(delta)
    
    def antilag_init(self, shift):
        "заранее перемещаем камеру по вектору движения"
        self.shift = shift
        if self.objects.focus_object:
            self.objects.antilag(self.antilag_shift)
    
    def antilag_handle(self, move_vector):
        "если камера была перемещена заранее - то вычитаем антилаг-смещение из смещения камеры, полученного с сервера"
        if self.antilag:
            vector = move_vector - self.antilag_shift 
            self.shift += vector
        else:
            self.shift += move_vector
        
        self.antilag = False
        self.antilag_shift = Point(0,0)
        
    def force_complete(self):
        "экстренно завершает все обновления"
        if self.shift:
            self.land.move_position(self.shift)
            self.shift = Point(0,0)
            self.land.update()
            self.objects.update(0)
    
    def round_update(self, dt):
        "обращение к движку"
        self.force_complete()
        for action, message in self.in_messages:
            #если произошел респавн игрока
            if action=='respawn':
                new_position = message
                print 'respawn from %s to %s' % (self.land.position,new_position )
                
                self.set_camera_position(new_position)
                self.objects.clear()
            elif action=='look':
                move_vector, newtiles, observed, updates, steps = message
                self.antilag_handle(move_vector)
                self.land.insert(newtiles, observed)
                self.objects.insert(updates)
        self.in_messages = []
        self.set_timer()

        
    def on_draw(self):
        "прорисовка спрайтов"
        #включаем отображение альфа-канала
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        #очищаем экран
        #self.clear()
        if self.accepted:
            self.land.draw()
            self.objects.draw()
        elif self.loading:
            self.loading.draw()
        self.fps_display.draw()
        
    def run(self):
        "старт"
        pyglet.app.run()
        name = hash(random())
        self.put_message(pack(name, 'client_accept'))
    
    def on_close(self):
        self.close_connection()
        exit()

########################################################################
class LandView(GameWindow,  Drawable, MapTools):
    "клиентская карта"
    def __init__(self, world_size, position, tiles=[], observed=[]):
        Drawable.__init__(self)
        size = world_size
        self.world_size = world_size
        self.map = defaultdict(lambda: defaultdict(lambda: 'fog'))
        self.tiles = []
        if tiles:
            self.insert(tiles, observed)
        self.set_camera_position(position)
        self.prev_position = position/2
        
    def move_position(self, vector):
        "перемещаем камеру"
        self.set_camera_position(self.position + vector)
        
    def insert(self, tiles, observed):
        "обновляет карту, добавляя новые тайлы, и видимые на этом ходе тайлы"
        self.observed = observed
        for point, tile_type in tiles:
            self.map[point.x][point.y] = tile_type
            
    def look_around(self):
        "список тайлов в поле зрения"
        rad_h = int(self.rad_h/TILESIZE)
        rad_w = int(self.rad_w/TILESIZE)
        
        I,J = (self.position/TILESIZE).get()

        range_i = xrange(I-rad_w-1, I+rad_w+2)
        range_j = xrange(J-rad_h-1, J+rad_h+2)
        return [((Point(i,j)*TILESIZE)-self.position,
            self.map[i][j]+'_fog' if not ((i,j) in self.observed or self.map[i][j]=='fog') else self.map[i][j]) 
            for j in range_j for i in range_i]
        
    def update(self):
        "обноление на каждом фрейме"
        #если положение не изменилось то ничего не делаем
        if not self.prev_position==self.position:
            looked = self.look_around()
            self.tiles = [create_tile(point+self.center, tile) for point, tile in looked]


########################################################################
class Object:
    "класс игрового объекта на карте"
    def __init__(self, name, position, tilename):
        print 'create %s' % name
        self.position = position
        self.name = name
        self._tilename = tilename
        self.tilename = tilename
        self.moving = False
        self.animation = 1
    
    def draw(self, shift):
        position = self.position - shift - Point(TILESIZE/2,TILESIZE/2)
        if self.moving:
            if self.animation>0:
                tilename = self.tilename+'_move'
            else:
                tilename = self.tilename+'_move_'
            self.animation*=-1
        else:
            tilename = self.tilename
        tiles = [create_tile(position, tilename)]
        if self.tilename not in ['ball','ball_move']:
                label = create_label(self.name, position)
                tiles.append(label)
        return tiles
    
    def update(self):
        if self.moving:
            self.moving = False
            
    def move(self, vector):
        if vector:
            self.moving = True
            self.position +=vector

    
    def __del__(self):
        print 'remove %s' % self.name
            

class ObjectsView(GameWindow, Drawable):
    "отображение объектов"
    def __init__(self):
        Drawable.__init__(self)
        self.objects = {}
        self.tiles = []
        self.updates = {}
        self.focus_object = False
    
    def antilag(self, shift):
        if self.focus_object:
            self.updates[self.focus_object]+=shift
    
    def insert(self, updates=[]):
        #обновления объектов
        self.updates = {name:update for name, update in self.updates.items() if name==self.focus_object}
        if updates:
            for name, position, vector, action, args in updates:
                if action=='move':
                    if name in self.updates:
                        self.updates[name] += vector
                    elif not name in self.updates:
                        self.updates[name] = vector
                        self.objects[name] =  Object(name, position,args)
                        if args=='self':
                            self.focus_object = name                         
                elif action=='remove':
                    self.remove_object(name)
        #убираем объекты, для которых не получено обновлений
        new_objects = {}
        for name in self.objects:
            if name in self.updates:
                new_objects[name] = self.objects[name]
        self.objects = new_objects

    def update(self, delta):
        if self.updates:
            for object_name, update in self.updates.items():
                if isinstance(update,Point):
                    vector = update
                    if delta:
                        move_vector = vector * delta
                        if move_vector>vector:
                            move_vector = vector
                    else:
                        move_vector = vector
                    if  vector:
                        self.objects[object_name].move(move_vector)
                        self.updates[object_name]-= move_vector

        #отображение объектов
        self.tiles = []
        for object_name, game_object in self.objects.items():
            self.tiles.extend(game_object.draw(self.position -self.center))
        #обновляем объекты
        [game_object.update() for game_object in self.objects.values()]
            
    
    def clear(self):
        self.objects = {}
        self.updates = {}
    
    def remove_object(self, name):
        if name in self.updates:
            del self.updates[name]
        if name in self.objects:
            del self.objects[name]

    


def main():
    g = Gui(600, 600)
    g.run()

if __name__=='__main__':
    if PROFILE_CLIENT:
        import cProfile, pstats
        cProfile.run('main()', '/tmp/game_pyglet.stat')
        stats = pstats.Stats('/tmp/game_pyglet.stat')
        stats.sort_stats('cumulative')
        stats.print_stats()
    else:
        main()

