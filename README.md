python client-server rpg

dependencies:
    server: python2.7, linux or windows with pyevent (http://code.google.com/p/pyevent/downloads/list)
    client: python 2.7, python-pyglet (http://pyglet.org/download.html)

run:
    python server.py

    for game server
    
    python game.py

    for game client
    
    enter hostname
    or use '-d' for default hostname, defined in cofig.py	

control:
    left mouse click or arrow keys for move
    right mouse click for shooting

files:

client.py - game client
server.py - game server

mapgen.py - map loading and generation(future)
config.py - game configuration

game_lib/
	ask_hostname.py - asking hostname when server or client running
	client_lib.py - clientside network classes
	engine_lib.py - game engine classes
	engine.py - main game engie class
	game_protocol.py  - packaging/unpackaging game messages
	game.py - game engine share state
	gui_lib.py - clientside interface tools
	map_lib.py - map tools
	math_lib.py - math, algorithms
	poll_lib.py - poll(epoll/libevent) poller class
	protocol_lib.py - data packaging and exhange
	server_lib.py - socket server

