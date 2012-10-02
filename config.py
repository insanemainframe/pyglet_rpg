#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
HOSTNAME = '127.0.0.1' #имя хоста по-умолчанию
IN_PORT = 8888 #порт для отправки сообщений на сервер
OUT_PORT = 8889 #порт для отправки сообщений клиенту
#
SERIALISATION = 'json'
ZLIB = False
#
TILESIZE = 40
LOCATIONSIZE = 20

#
TILESDIR = 'images/'

#
ROUND_TIMER = 0.1
SERVER_TIMER = 0.1

PROFILE_CLIENT = 0
PROFILE_SERVER = 1

SERVER_PROFILE_FILE = '/tmp/game_server.stat'
CLIENT_PROFILE_FILE = '/tmp/game_client.stat'

