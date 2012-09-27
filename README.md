python client-server rpg

REQUIRMENTS:

    server: python2.7, Linux. Or Windows with pyevent (http://code.google.com/p/pyevent/downloads/list)

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
    config.py - game settings

share/

    ask_hostname.py - asking hostname when server or client running
    
    mathlib.py - point class
    
    protocol_lib.py - data sending/receiving, packing/unpacking
    
    game_protocol.py -  methods of game protocol 
    
engine/

    engine.py - main game engine class
    
    game.py - game engine modules share state
	
	engine_lib.py - base game-objects classes
    
    game_objects/ - game-objects classes
	

    maplib.py - map tools

	mathlib.py - math, algorithms
    

    
clientside/

	network.py - clientside network classes
    
    client_objects.py -  clientside gameobject classes

	gui_lib.py - clientside interface tools

	
serverside/

	poll_lib.py - poll(epoll/libevent) poller class

	server_lib.py - socket server

tools/

    clean.sh - remove *.pyc files
    
    profile_server.py/profile_client.py - print profile stats sorted by key
    
