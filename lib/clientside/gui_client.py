#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from client_config import *



print 'Loading modules...'
#вьюверы для карты, объектов, статики
from clientside.view.view_objects import ObjectsView
from clientside.view.view_land import LandView

#класс точки
from share.point import *

from clientside.gameclient import GameClient
from clientside.input import InputHandle

from clientside.gui.gui_lib import DeltaTimerObject
from clientside.gui import window
from clientside.gui.gui_elements import *
from clientside.gui import surfaces
  



class GuiClient(DeltaTimerObject, InputHandle, window.GUIWindow):
    accepted = False
    vector = Point(0,0)
    def __init__(self, hostname, (height, width)):
        #инициализация родтельских классов
        window.GUIWindow.__init__(self, height, width)
        InputHandle.__init__(self)
        DeltaTimerObject.__init__(self)

        #клиент игры
        self.client = GameClient(self,hostname)

        gs_size = 700
        #поверхности
        self.gamesurface = surfaces.GameSurface(self, 0,0,gs_size, gs_size)
        self.rightsurface = surfaces.StatsSurface(self, gs_size, 0, height, width-gs_size)
        self.surfaces = [self.gamesurface, self.rightsurface]
        
        self.location_display = locationDisplay(self.rightsurface)
        self.stats = StatsDisplay(self.rightsurface)
        self.plist = PlayersOnlineDisplay(self.rightsurface)
        self.equipment = EquipmentDisplay(self.rightsurface)


        self.land = LandView(self, self.gamesurface)
        self.objects = ObjectsView(self, self.gamesurface)

        
        #текст загрузки
        self.loading = LoadingScreen(self.gamesurface)
        
        #счетчик фпс
        self.fps_display = FPSDisplay()
        #хелп
        self.help_display = HelpScreen(self.gamesurface)
        
        self.first_look = True

        self.accepted = False

        #устанавливаем обновления на каждом кадре
        self.set_round_update(lambda delta: self.round_update(delta), self.timer_value)
        self.set_update(lambda delta: self.update(delta))
    
    def new_location(self, name, location_size, position, background):
        "создание нового мира"
        self.land.set_location(location_size, position, background)
        self.location_display.change(name, location_size, position)
        
        from clientside.client_objects.objects_lib import MapAccess
        MapAccess.map = self.land.map
    

    
    def update(self, dt):
        "вызывается на каждом фрейме"
        #обработка соединения
        if self.accepted:
            self.client.update()
        else:
            self.client.accept()
            self.accepted = True
        #перехвт ввода
        self.handle_input()

        

        #нахождение проходимого на этом фрейме куска вектора
        delta = self.get_delta()
        vector = self.client.shift*delta
        if vector> self.client.shift:
            vector = self.client.shift
        self.client.shift = self.client.shift - vector

        #двигаем камеру
        self.land.move_position(vector)
        self.location_display.update(self.gamesurface.position)

        #обновляем карту и объекты
        
        self.objects.update(delta)

        new_position = self.objects.get_focus_position()

        self.land.update()
    

    def antilag_init(self, shift):
        "заранее перемещаем камеру по вектору движения"
        self.client.shift = shift
        if self.objects.focus_object:
            self.objects.antilag(self.client.antilag_shift)
    

    def antilag_handle(self, move_vector):
        "если камера была перемещена заранее - то вычитаем антилаг-смещение из смещения камеры, полученного с сервера"
        if self.client.antilag:
            vector = move_vector - self.client.antilag_shift 
            self.client.shift += vector
        else:
            self.client.shift += move_vector
        
        self.client.antilag = False
        self.client.antilag_shift = Point(0,0)
        

    def force_complete(self):
        "экстренно завершает все обновления"
        if self.client.shift:
            self.land.move_position(self.client.shift)
            self.client.shift = Point(0,0)
            self.land.update()
            self.objects.force_complete()
    

    def round_update(self, dt):
        "обработка данных полученных с сервера"
        self.force_complete()
        self.objects.round_update()
  
        
        for action, message in self.client.get_messages():
            #если произошел респавн игрока
            if action=='Respawn':
                new_position = message                
                self.gamesurface.set_camera_position(new_position)
            
            elif action=='MoveCamera':
                move_vector = message
                self.antilag_handle(move_vector)
                
            elif action=='LookLand':
                newtiles, observed = message
                self.land.insert(newtiles, observed)
                if self.first_look:
                    self.land.update(self.first_look)
                    self.first_look = False
                
            
            elif action=='LookObjects':
                new_players, events, old_players = message
                self.objects.insert_objects(new_players, old_players)
                self.objects.insert_events(events)
                self.objects.clear()
                

                
                
            
            elif action=='PlayerStats':
                self.stats.update(*message)
            
            elif action == 'PlayersList':
               self.plist.update(message)
            
            elif action == 'EquipmentDict':
                self.equipment.update(message)
            
            elif action=='NewLocation':
                wold_name, location_size, position, background = message
                self.new_location(wold_name, location_size, position, background)
            
            else:
                print 'Unknown Action:%s' % action
        
        
        self.set_timer()

        
    def on_draw(self):
        "прорисовка спрайтов"
        #очищаем экран
        self.clear()
        #включаем отображение альфа-канала
        self.enable_alpha()
        
        self.land.draw()
        self.objects.draw()
        
        

        #отрисовка бара
        self.rightsurface.draw_background(0,0,'rightside')
        self.stats.draw()
        self.location_display.draw()
        self.plist.draw()
        self.equipment.draw()
        


        self.help_display.draw()
        self.fps_display.draw()
    

        
    def run(self):
        "старт"
        self.run_app()
    

    def on_close(self):
        self.client.close_connection()
        exit()

