#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pyglet
from pyglet.window.key import UP, DOWN, LEFT, RIGHT
from pyglet.image.codecs.png import PNGImageDecoder
from pyglet.gl import *

from time import time
from os import listdir


from engine import Game
from mathlib import Point
from maplib import ClientWorld
from config import *



class GameWindow():
    "разделяемое состояние элементов gui"
    @staticmethod
    def configure(size, timer_value):
        cls = GameWindow
        cls.timer_value = timer_value
        cls.size = size
        cls.window_size = size
        cls.center = Point(cls.window_size/2,cls.window_size/2)
        print 'window center',cls.center
        cls.rad = (size/2)
        cls.clock_setted = False
        cls.complete = 0
        
    @staticmethod
    def gentiles():
        names = listdir('data')
        cls = GameWindow
        cls.tiledict = {}
        for name in names:
            image = pyglet.image.load('data/%s' % name, decoder=PNGImageDecoder()).get_texture()
            cls.tiledict[name[:-4]] = image
    @staticmethod
    def create_tile(point, tilename):
        "создае тайл"
        #tile = pyglet.sprite.Sprite(GameWindow.tiledict[tilename])
        #tile.x, tile.y = point.round().get()
        #return tile
        return (tilename, point.get())
    @staticmethod
    def set_timer():
        cls = GameWindow
        #if cls.complete<1 and cls.clock_setted:
        #    #print 'not complete', cls.complete
        
        cls.clock = time()
        cls.complete = 0
        cls.clock_setted = True
    @staticmethod
    def complete_delta():
        cls = GameWindow
        if cls.complete<1:
            delta = 1-cls.complete
            cls.complete = 1
            return delta
        else:
            return 0
    @staticmethod
    def get_delta():
        "возвращзает отношение времени предыдщего вызова get_delta или set_timer к timer_value"
        cls = GameWindow
        if cls.clock_setted:
            cur_time = time()
            delta_time = cur_time-cls.clock
            part = delta_time/cls.timer_value
            cls.clock = cur_time
            if part+cls.complete<=1:
                cls.complete+=part
                return part
            else:
                part = 1-cls.complete
                cls.complete = 1
                return part
        else:
            return 0

        
        

class Gui(GameWindow, pyglet.window.Window): 
    def __init__(self,size, timer_value):
        pyglet.window.Window.__init__(self, size, size)
        print 'windowsize %s' %  size     
        self.configure(size, timer_value)
        self.gentiles()
        self.game = Game(self.rad/TILESIZE)
        self.objects = ObjectsView()
        self.shift = Point(0,0)
        
        self.fps_display = pyglet.clock.ClockDisplay()
        
        world_size, position, tiles, objects = self.game.accept()

        self.land = LandView(world_size, position, tiles)
        self.objects.insert(objects)
        
        

    def on_key_press(self, symbol, modifiers):
        "движение с помощью клавиатуры"
        if symbol==UP: self.vector = Point(0,41)
        elif symbol==DOWN: self.vector = Point(0,-40)
        elif symbol==LEFT: self.vector = Point(-40,0)
        elif symbol==RIGHT: self.vector = Point(40,0)
    
    def on_mouse_press(self, x, y, button, modifiers):
        "перехватывавем нажатие мышки"
        #левая кнопка - движение
        if button==1:
            vector = (Point(x,y) - self.center)
            self.vector = vector
    
    def update(self, dt):
        delta = self.get_delta()
        vector = self.shift*delta
        self.shift = self.shift - vector
        self.land.move_position(vector)
        self.land.update()
        
    def force_complete(self):
        "завершает перемщение по вектору"
        if self.shift:
            self.land.move_position(self.shift)
            self.shift = Point(0,0)
    
    def round_update(self, dt):
        "обращение к движку"
        self.force_complete()
        move_vector, newtiles, objects = self.game.go(self.vector)
        self.shift = move_vector

        self.vector = Point(0,0)
        self.land.update()
        self.land.insert(newtiles)
        self.objects.insert(objects)
        self.set_timer()
        logger.debug('>\n')

        
    def on_draw(self):
        "прорисовка спрайтов"
        #включаем отображение альфа-канала
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        self.clear()
        self.land.draw()
        self.objects.draw()
        self.fps_display.draw()

        
        
    def run(self):
        "старт"
        print 'loop'
        self.vector = Point(0,0)
        pyglet.clock.schedule(self.update)
        pyglet.clock.schedule_interval(self.round_update, self.timer_value)
        
        pyglet.app.run()

class Drawable:
     def draw(self):
        #[tile.draw() for tile in self.tiles]
        [self.tiledict[tilename].blit(x,y, width=TILESIZE, height=TILESIZE) for tilename, (x,y) in self.tiles]
    
class LandView(GameWindow, ClientWorld, Drawable):
    "представление карты на экране"
    def __init__(self, world_size, position, tiles = []):
        ClientWorld.__init__(self, world_size)
        self.tiles = []
        if tiles:
            self.insert(tiles)
        self.position = position
        logger.debug('LandView init: position %s' % self.position)
        
    def update(self):
        "обноление на каждом фрейме"
        looked = self.look_around(self.rad)
        logger.debug('looked len %s' % len(looked))
        self.tiles = [self.create_tile(point+self.center, tile_type) for point, tile_type in looked]
        #print 'tiles count', len(self.tiles )#[tile.position for tile in self.tiles]


    
class ObjectsView(GameWindow, Drawable):
    def __init__(self):
        self.tiles = []
    
    def insert(self, objects):
        for point, tilename in objects:
            #смещаем по центру
            point = point+self.center - Point(TILESIZE/2, TILESIZE/2)
            tile = self.create_tile(point, tilename)
            self.tiles.append(tile)




    
def main():
    g = Gui(size=600,timer_value = 0.1)
    g.run()
if __name__=='__main__':
    profile = 0
    if profile:
        import cProfile, pstats
        cProfile.run('main()', 'game_pyglet.stat')
        stats = pstats.Stats('game_pyglet.stat')
        stats.sort_stats('cumulative')
        stats.print_stats()
    else:
        main()

