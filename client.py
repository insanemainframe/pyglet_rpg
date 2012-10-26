#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sys import path
path.append('lib/')

from config import *
from client_config import *


from clientside.gui_client import GuiClient
from share.ask_hostname import ask_hostname


def main():
    hostname = ask_hostname(HOSTNAME)
    game = GuiClient(hostname, (900, 700))
    game.run()

if __name__=='__main__':
    if PROFILE_CLIENT:
        import cProfile
        cProfile.run('main()', CLIENT_PROFILE_FILE)
    else:
        main()

