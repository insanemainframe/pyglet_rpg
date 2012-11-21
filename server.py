#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sys import path

path.append('lib/')


from config import HOSTNAME, PROFILE_SERVER, SERVER_PROFILE_FILE

from share.ask_hostname import ask_hostname
from serverside.game_server import GameServer

from server_logger import debug


def main():
    hostname = ask_hostname(HOSTNAME)
    server = GameServer(hostname, listen_num = 100)
    server.start()

if __name__ == '__main__':
	if PROFILE_SERVER:
		import cProfile
		debug('profile')
		cProfile.run('main()', SERVER_PROFILE_FILE)
        
	else:
		main()

	debug ('game process stopped')

