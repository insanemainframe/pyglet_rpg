#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from share.point import Point
from engine.enginelib.meta import GameObject, Guided

from weakref import proxy, ProxyType


class Voxel:
	def __init__(self, cord):
		self.cord = cord
		self._players = {}


	def append(self, player):
		assert isinstance(player, ProxyType)
		
		if isinstance(player, Guided):  print 'voxel[%s].append %s' % (self.cord, player)

		self._players[player.name] = player
		player.voxel = proxy(self)

	def remove(self, player):
		if isinstance(player, Guided):  print 'voxel[%s].remove %s' % (self.cord, player)
		
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
		return self._players.values()+voxel._players.values()

	def __radd__(self, players_list):
		return players_list + self._players.values()

	def __len__(self):
		return len(self._players)

	def __nonzero__(self):
		return bool(self._players)

