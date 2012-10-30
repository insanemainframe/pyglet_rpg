#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sys import path
path.append('lib/')

from config import *
from client_config import *




def main():
	from share.ask_hostname import ask_hostname

	hostname = ask_hostname(HOSTNAME)

	from clientside.gui_client import GuiClient

	game = GuiClient(hostname, (900, 700))
	game.run()

if __name__=='__main__':
    if PROFILE_CLIENT:
        import cProfile
        cProfile.run('main()', CLIENT_PROFILE_FILE)
    else:
        main()

