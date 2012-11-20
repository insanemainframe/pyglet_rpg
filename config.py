#!/usr/bin/env python
# -*- coding: utf-8 -*-
import tempfile
from os.path import join

TMP = tempfile.gettempdir()

#имя хоста по-умолчанию
HOSTNAME = '127.0.0.1'
IN_PORT = 8888
OUT_PORT = 8889
# SERIALIZATION_TYPE = 'json'
SERIALIZATION_TYPE = 'marshal'

SERIALIZATION_FILE_TYPE = 'marshal'
USE_ZLIB = True


ACCEPT_NUMBER = 0
TILESIZE = 60
CHUNK_SIZE = 6
ROUND_TIMER = 0.1
SERVER_TIMER = 0.1
PLAYER_LOOK_RADIUS = 9
RECT_FOV = True

###
LOCATION_PATH = 'data/locations/%s/'
LOCATION_PERSISTENCE = True
SAVE_LOCATION = True
LOCATION_FILE = 'location.%s.zlib' % SERIALIZATION_FILE_TYPE
MAP_FILE = 'map.%s.zlib' % SERIALIZATION_FILE_TYPE
MAP_IMAGE = 'map.png'
MAP_DICT = 'tiledict.py'
LOCATION_MUL = 1
MAP_ZLIB = True


LOG_FILE = '/tmp/server_game.log'

PROFILE_SERVER = 1
SOCKET_SERVER_PROFILE = 1

SERVER_PROFILE_FILE = join(TMP,'/tmp/game_server.stat')
SOCKET_SERVER_PROFILE_FILE = join(TMP,'/tmp/socket_server.stat')

TEST_MODE = True

DEBUG = False
DEBUG_WEAK_REFS = True
DEBUG_REFS = False