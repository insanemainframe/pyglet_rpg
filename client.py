#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from sys import exit


from share.mathlib import *
from share.ask_hostname import AskHostname

from clientside.network import GameClient
from clientside.input import InputHandle

from clientside.gui.gui_lib import DeltaTimerObject
from clientside.gui import window
from clientside.gui.gui_elements import FPSDisplay, Stats, LoadingScreen, WorldDisplay

from clientside.view.view_objects import ObjectsView
from clientside.view.view_land import LandView
from clientside.view.view_static_objects import StaticObjectView

class Gui(DeltaTimerObject, GameClient, InputHandle, AskHostname, window.GUIWindow):
    accepted = False
    shift = Point(0,0)
    vector = Point(0,0)
    hostname = HOSTNAME
    def __init__(self, height, width):
        #инициализация родтельских классов
        AskHostname.__init__(self, HOSTNAME)
        window.GUIWindow.__init__(self, height, width)
        InputHandle.__init__(self)
        DeltaTimerObject.__init__(self)
        GameClient.__init__(self)
        
        self.gamesurface = window.GameSurface(0,0,600, 600)
        self.rightsurface = window.StatsSurface(600, 0, height, width-600)
        
        self.world_display = WorldDisplay(self.rightsurface)
        
        self.stats = Stats(self.rightsurface)
       
        
        #текст загрузки
        self.loading = LoadingScreen(self.gamesurface)
        
        #счетчик фпс
        self.fps_display = FPSDisplay()
        #
        self.first_look = True
        self.accept()
    
    def new_world(self, name, world_size, position, background):
        self.land = LandView(self.gamesurface, world_size, position, background)
        self.objects = ObjectsView(self.gamesurface)
        self.static_objects = StaticObjectView(self.gamesurface)
        
        self.world_display.change(name, world_size, position)
        
        from clientside.view.client_objects import MapAccess
        MapAccess.map = self.land.map
    
    def accept(self):
        accept_data = self.wait_for_accept()
        if accept_data:
            wold_name, world_size, position, background = accept_data
            self.new_world(wold_name, world_size, position, background)            
            
            
            self.accepted = True
            self.loading = False
            #устанавливаем обновления на каждом кадре
            self.set_round_update(self.round_update, self.timer_value)
            self.set_update(self.update)
            
            return True
            
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
        self.world_display.update(self.gamesurface.position)
        #обновляем карту и объекты
        self.land.update()
        
        self.objects.update(delta)
        self.static_objects.update()
    
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
            self.objects.force_complete()
    
    def round_update(self, dt):
        "обработка данных полученных с сервера"
        self.force_complete()
        self.objects.round_update()
        self.static_objects.round_update()
        
        for action, message in self.pop_messages():
            #если произошел респавн игрока
            if action=='Respawn':
                new_position = message                
                self.gamesurface.set_camera_position(new_position)
                self.objects.clear()
                self.static_objects.clear()
            
            elif action=='MoveCamera':
                move_vector = message
                self.antilag_handle(move_vector)
                
            elif action=='LookLand':
                newtiles, observed = message
                self.land.insert(newtiles, observed)
                if self.first_look:
                    self.land.update(self.first_look)
                    self.first_look = False
                
            
            elif action=='LookPlayers':
                objects = message
                self.objects.insert_objects(objects)
                
                
            
            elif action=='LookEvents':
                events = message
                self.objects.insert_events(events)
                self.objects.clear()
                
            
            elif action=='LookStaticObjects':
                static_objects = message
                self.static_objects.insert_objects(static_objects)
                
            elif action=='LookStaticEvents':
                static_objects_events = message
                self.static_objects.insert_events(static_objects_events)
            
            elif action=='PlayerStats':
                self.stats.update(*message)
            
            elif action=='NewWorld':
                wold_name, world_size, position, background = message
                self.new_world(wold_name, world_size, position, background)
            else:
                print 'Unknown Action:%s' % action
        
        
        self.objects.filter()
        self.set_timer()

        
    def on_draw(self):
        "прорисовка спрайтов"
        #очищаем экран
        self.clear()
        #включаем отображение альфа-канала
        self.enable_alpha()
        
        if self.accepted:
            self.land.draw()
            self.objects.draw()
            
            self.static_objects.draw()
            self.stats.draw()
            self.world_display.draw()
        
        elif self.loading:
            self.loading.draw()
        self.fps_display.draw()
        
    def run(self):
        "старт"
        self.run_app()
    
    def on_close(self):
        self.close_connection()
        exit()

########################################################################




########################################################################


    


def main():
    g = Gui(800, 600)
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

