Python multiplayer client-server hack-and-slash game, using pyglet(or pygame wrapper) and non-blocking sockets. Just for fun and self-education.
Tiles grabbed from [wesnoth](http://www.wesnoth.org/)


REQUIRMENTS:
    
server: python2.7

client: python 2.6>= [python-pyglet](http://pyglet.org/download.html) 

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

    F[1-8] to use items in slots


