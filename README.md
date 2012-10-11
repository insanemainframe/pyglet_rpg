Python multiplayer client-server hack-and-slash game, using pyglet(or pygame wrapper) and non-blocking sockets. Just for fun and self-education.
Tiles grabbed from [wesnoth](http://www.wesnoth.org/)


REQUIRMENTS:
    
server: python2.7

client: python 2.6>= [python-pyglet](http://pyglet.org/download.html) recomended  or [pygame](http://www.pygame.org/download.shtml)

RUN:
````
python server.py
````

for game server

````
python client.py
````

for game client


and enter hostname

or use '-d' for default hostname, defined in config.py

````
python server.py -d
````

````
python client.py -d
````


CONTROL:


    left mouse click or arrow keys(with right shift for acceleration) for move

    right mouse click for shooting
    
    SPACE for special ability



FILES:

    client.py - game client

    server.py - game server
    
    bot.py [number] - bots for testig server

    mapgen.py - map loading and generation(future)
    
    config.py - game settings

share/

    ask_hostname.py - asking hostname when server or client running
    
    mathlib.py - point class
    
    protocol_lib.py - data sending/receiving, packing/unpacking
    
    game_protocol.py -  methods of game protocol 
    
engine/

    engine.py - providing interface to engine 
    
    game.py - game engine singleton
	
	engine_lib.py - base game-objects classes
    
    game_objects/ - game-objects classes
	

    maplib.py - map tools

	mathlib.py - math, algorithms
    

    
clientside/

	network.py - clientside network classes
    
    objects_lib.py - base classes for clientside objects
    
    client_objects.py -  clientside gameobject classes
    
    static_objects.py - static objects classes
    
	gui_lib.py - clientside interface tools
    
    gui_elements.py - gui elements
    
    input.py - keyboard/mouse input handling
    
    view_lib.py - viewer's lib
    
    view_land.py - map terrain view
    
    view_objects.py - dynamic objects view
    
    view_static objects.py - static objects view
    
    window.py - import clientside game engine
    
    pyglet_window.py - pyglet engine
    
    pygame_window.py - pygame engine


	
serverside/

	multiplexer.py - poll(epoll/libevent) or select I/O-events multiplexer class

	server_lib.py - socket server

tools/

    clean.sh - remove *.pyc files
    
    profile_server.py/profile_client.py - print profile stats sorted by key
    
