Python multiplayer client-server hack-and-slash game, using pyglet(or pygame wrapper) and non-blocking sockets. Just for fun and self-education.
Tiles grabbed from [wesnoth](http://www.wesnoth.org/) and [other internets](http://images.google.com/)


REQUIRMENTS:
    
server: python2.7

client: python 2.6>= [python-pyglet](http://pyglet.org/download.html) [version for windows](http://celeron.55.lt/~celeron55/random/2011-08/pyglet-1.1.4-py27quickfix.msi)

if you want to build extensions with [cython](http://cython.org/): cython, python-dev, gcc


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

building c-extensions(optional)

````
./tools/compile.sh
````


CONTROL:


    left mouse click or arrow keys(with right shift for acceleration) for move

    right mouse click for shooting
    
    SPACE for special ability

    F[1-8] to use items in slots


