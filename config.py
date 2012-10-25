#!/usr/bin/env python
# -*- coding: utf-8 -*-

#имя хоста по-умолчанию
HOSTNAME = '127.0.0.1'
#порт для отправки сообщений на сервер
IN_PORT = 8888
#порт для отправки сообщений клиенту
OUT_PORT = 8889

SERIALISATION = 'json'
ZLIB = False
#
TILESIZE = 60
LOCATIONSIZE = 6

#
ROUND_TIMER = 0.1
SERVER_TIMER = 0.1

PROFILE_SERVER = 1
SOCKET_SERVER_PROFILE = 1

SERVER_PROFILE_FILE = '/tmp/game_server.stat'
SOCKET_SERVER_PROFILE_FILE = '/tmp/socket_server.stat'

WORLD_PICKLE_PATH = 'worldmaps/%s/world.pickle'
WORLD_PERSISTENCE = False

WORLD_MUL = 100

LOOK_RADIUS = 10

