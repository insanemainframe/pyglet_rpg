#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pyglet
from pyglet.gl import *

from math import hypot
from sys import exit

from game_lib.math_lib import Point
from game_lib.gui_lib import *
from game_lib.map_lib import Map
from game_lib.client_lib import Client
from game_lib.protocol_lib import *

from config import *

class Gui(GameWindow, DeltaTimerObject, Client, InputHandle, pyglet.window.Window, AskHostname): 
    def __init__(self, height, width):
        #инициализация родтельских классов
        AskHostname.__init__(self)
        pyglet.window.Window.__init__(self, width, height)
        DeltaTimerObject.__init__(self)
        InputHandle.__init__(self)
        Client.__init__(self)
        
        self.configure(width, height)
        self.gentiles()
        self.objects = ObjectsView()
        self.shift = Point(0,0)
        self.vector = Point(0,0)
        
        #текст загрузки
        self.loading = LoadingScreen(self.center)
        
        #счетчик фпс
        self.fps_display = pyglet.clock.ClockDisplay()
                
        #net
        self.accepted = False
    
    def accept(self):
        if not self.accepted:
            data = self.wait_for_accept()
            if data:
                world_size, position, tiles, objects = data
            
                print 'accepteed position %s tiles %s' % (position, len(tiles))
        
                self.land = LandView(world_size, position, tiles)
                self.objects.insert(objects)
                self.accepted = True
                self.loading = False
                return True
            else:
                return False
        else:
            return True
    
    
    def update(self, dt):
        if self.accept():
            self.loop()
            delta = self.get_delta()
            vector = self.shift*delta
            if vector> self.shift:
                vector = self.shift
            self.shift = self.shift - vector
            self.land.move_position(vector)
            self.land.update()
            self.objects.update(delta)
        
    def force_complete(self):
        "завершает перемщение по вектору"
        if self.shift:
            self.land.move_position(self.shift)
            self.shift = Point(0,0)
            self.land.update()
            self.objects.update(0)
    
    def round_update(self, dt):
        "обращение к движку"
        if self.accept():
            self.force_complete()
            #net
            
            for message in self.in_messages:
                move_vector, newtiles, objects, objects_update = message
                self.shift += move_vector
        
                self.land.update()
                self.land.insert(newtiles)
                self.objects.insert(objects, objects_update)
            self.in_messages = []
            self.set_timer()
            logger.debug('>\n')
        

        
    def on_draw(self):
        "прорисовка спрайтов"
        #включаем отображение альфа-канала
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.clear()
        if self.loading:
            self.loading.draw()
        if self.accept():
            self.land.draw()
            self.objects.draw()
        self.fps_display.draw()
        
    def run(self):
        "старт"
        pyglet.clock.schedule(self.update)
        pyglet.clock.schedule_interval(self.round_update, self.timer_value)
        pyglet.app.run()
    
    def on_close(self):
        self.close_connection()
        exit()


class LandView(GameWindow,  Drawable, Map):
    "клиентская карта"
    def __init__(self, world_size, position, tiles = []):
        Drawable.__init__(self)
        size = world_size
        self.world_size = world_size
        self.map = [[None for j in xrange(size)] for i in xrange(size)]
        self.tiles = []
        if tiles:
            self.insert(tiles)
        self.set_camera_position(position)
        self.prev_position = position/2
        
    def move_position(self, vector):
        "перемещаем камеру"
        self.set_camera_position(self.position + vector)
        
        
    def insert(self, tiles):
        "обновляет карту, добавляя новые тайлы, координаты - расстояние от стартовой точки"
        for point, tile_type in tiles:
            self.map[point.x][point.y] = tile_type
            
    def look_around(self):
        "список тайлов в поле зрения (координаты в тайлах от позиции камеры, тип)"
        rad_h = int(self.rad_h/TILESIZE)+2
        rad_w = int(self.rad_w/TILESIZE)+2
        
        I,J = (self.position/TILESIZE).get()
        looked = set()
        for i in xrange(I-rad_w, I+rad_w):
            for j in xrange(J-rad_h, J+rad_h):
                i,j = self.resize_d(i,'height'), self.resize_d(j,'width')
                try:
                    tile_type = self.map[i][j]
                except IndexError:
                    tile_type = False
                if not tile_type:
                    tile_type = 'fog'
                point = (Point(i,j)*TILESIZE)-self.position
                looked.add((point, tile_type))
        i, j = self.position.get()
        return looked
        
    def update(self):
        "обноление на каждом фрейме"
        #если положение не изменилось то ничего не делаем
        if self.prev_position==self.position:
            return
        looked = self.look_around()
        self.tiles = [create_tile(point+self.center, tile_type) for point, tile_type in looked]



class ObjectsView(GameWindow, Drawable):
    def __init__(self):
        Drawable.__init__(self)
        self.objects = {}
        self.tiles = []
        self.updates = {}
    
    def insert(self, new_objects, updates=None):
        if updates:
            for object_name, vector in updates.items():
                if object_name in self.updates:
                    if isinstance(vector,Point):
                        self.updates[object_name] += vector
                    else:
                        self.updates[object_name] = vector
                else:
                     self.updates[object_name] = vector
        if new_objects:
            for object_name, (position, tilename) in new_objects.items():
                self.objects[object_name] = {'position':position,'tilename': tilename}

            
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
                            self.objects[object_name]['position']+= move_vector
                            self.updates[object_name]-= move_vector
                else:
                    self.remove_object(object_name)

        
        #отображение объектов
        self.tiles = []
        for object_name, game_object in self.objects.items():
            point = game_object['position']
            tilename = game_object['tilename']
            position = point - self.position +self.center - Point(TILESIZE/2,TILESIZE/2)
            tile = create_tile(position, tilename)
            self.tiles.append(tile)
            label = create_label(object_name, position)
            self.tiles.append(label)
    def remove_object(self, name):
        del self.updates[name]
        del self.objects[name]
    




    
def main():
    g = Gui(480, 680)
    g.run()

if __name__=='__main__':
    if PROFILE:
        import cProfile, pstats
        cProfile.run('main()', '/tmp/game_pyglet.stat')
        stats = pstats.Stats('/tmp/game_pyglet.stat')
        stats.sort_stats('cumulative')
        stats.print_stats()
    else:
        main()

