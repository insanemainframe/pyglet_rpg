#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from engine.mathlib import Cord, Position, ChunkCord

from engine.enginelib.meta import GameObject, Guided
from engine.world.objects_containers import near_cords

from weakref import proxy, ProxyType


class Voxel:
	def __init__(self, chunk, cord):
		assert isinstance(cord, Cord)

		self.chunk = chunk
		self.cord = cord
		self._players = {}

		

	def create_links(self):
		cords = filter(self.chunk.location.is_valid_cord, [self.cord + cord for cord in near_cords])
		nears_cords = [(cord.to_chunk(), cord) for cord in cords]
		self.nears = [self.chunk.location[chunk_cord][cord] for chunk_cord, cord in nears_cords]


	def get_nears(self):
		return self.nears


	def append(self, player):
		assert isinstance(player, ProxyType)
		assert not hasattr(player, 'voxel')
		
		if isinstance(player, Guided) :  print ('voxel[%s].append %s' % (self.cord, player))

		self._players[player.name] = player
		player.voxel = proxy(self)
		player.cord_changed = True

	def remove(self, player):
		if isinstance(player, Guided):  print ('voxel[%s].remove %s' % (self.cord, player))
		player.cord_changed = True
		del self._players[player.name]
		del player.voxel

	def __contains__(self, player):
		assert isinstance(player, Guided)
		return player.name in self._players

	def __iter__(self):
		for name in self._players.copy():
			yield self._players[name]
		raise StopIteration

	def __add__(self, voxel):
		return self._players.values() + list(voxel._players.values())

	def __radd__(self, players_list):
		return players_list + list(self._players.values())

	def __len__(self):
		return len(self._players)

	def __nonzero__(self):
		return bool(self._players)

