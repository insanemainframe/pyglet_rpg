#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from sys import exit


from share.mathlib import *
from share.ask_hostname import AskHostname

from clientside.network import Client
from clientside.input import InputHandle

from clientside.gui.gui_lib import DeltaTimerObject
from clientside.gui.window import GameWindow, GUIWindow
from clientside.gui.gui_elements import FPSDisplay, Stats, LoadingScreen

from clientside.view.view_objects import ObjectsView
from clientside.view.view_land import LandView
from clientside.view.view_static_objects import StaticObjectView

class Gui(GameWindow, DeltaTimerObject, Client, InputHandle, AskHostname, GUIWindow):
    accepted = False
    shift = Point(0,0)
    vector = Point(0,0)
    hostname = HOSTNAME
    def __init__(self, height, width):
        #инициализация родтельских классов
        AskHostname.__init__(self, HOSTNAME)
        GUIWindow.__init__(self, height, width)
        GameWindow.__init__(self, height, width)
        InputHandle.__init__(self)
        DeltaTimerObject.__init__(self)
        Client.__init__(self)
        
        self.objects = ObjectsView()
        self.stats = Stats()
        self.static_objects = StaticObjectView()
        
        #текст загрузки
        self.loading = LoadingScreen(self.center)
        
        #счетчик фпс
        self.fps_display = FPSDisplay()
        #
        self.accept()
    
    def accept(self):
        accept_data = self.wait_for_accept()
        if accept_data:
            world_size, position = accept_data
        
            print 'accepteed position %s ' % position
            
            self.land = LandView(world_size, position)
            
            from clientside.view.client_objects import MapAccess
            MapAccess.map = self.land.map
            
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
        for action, message in self.in_messages:
            #если произошел респавн игрока
            if action=='Respawn':
                new_position = message                
                self.set_camera_position(new_position)
                self.objects.clear()
            
            elif action=='MoveCamera':
                move_vector = message
                self.antilag_handle(move_vector)
                
            elif action=='LookLand':
                newtiles, observed = message
                self.land.insert(newtiles, observed)
                self.static_objects.filter(observed)
                self.objects.filter(observed)
                
            elif action=='LookObjects':
                events = message
                self.objects.insert(events)
            
            elif action=='LookStaticObjects':
                static_objects = message
                self.static_objects.insert_objects(static_objects)
                self.static_objects.update()
                
            elif action=='LookStaticEvents':
                static_objects_events = message
                self.static_objects.insert_events(static_objects_events)
                self.static_objects.update()
            
            elif action=='PlayerStats':
                self.stats.update(*message)
            else:
                print 'Unknown Action'
        self.objects.remove_timeouted()
        self.in_messages = []
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
            self.stats.draw()
            self.static_objects.draw()
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

