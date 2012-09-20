python client-server rpg

DEPENDING:

    server: python2.7, linux or windows with pyevent (http://code.google.com/p/pyevent/downloads/list)

    client: python 2.7, python-pyglet (http://pyglet.org/download.html)

RUN:

    python server.py

    for game server
    
    python client.py

    for game client
    
    enter hostname

    or use '-d' for default hostname, defined in cofig.py	

CONTROL:

    left mouse click or arrow keys(with right shift for acceleration) for move

    right mouse click for shooting

FILES:

client.py - game client

server.py - game server

mapgen.py - map loading and generation(future)
config.py - game configuration

game_lib/

	ask_hostname.py - asking hostname when server or client running

	engine_lib.py - game-objects classes

	engine.py - main game engie class
    
    game_protocol.py  - packaging/unpackaging game messages
    
    game.py - game engine share state
    
    map_lib.py - map tools

	math_lib.py - math, algorithms
    
    protocol_lib.py - data packaging and exhange
    
clientside/

	network.py - clientside network classes
    
    client_objects.py -  clientside gameobject classes

	gui_lib.py - clientside interface tools

	
serverside/

	poll_lib.py - poll(epoll/libevent) poller class

	server_lib.py - socket server

