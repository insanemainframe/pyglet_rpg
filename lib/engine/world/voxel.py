#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *

from share.point import Point
from engine.enginelib.meta import GameObject

from weakref import ProxyType

Voxel = list

class Voxel:
	def __init__(self):
		self._players = {}

	def append(self, player):
		assert isinstance(player, ProxyType)

		self._players[player.name] = player

	def remove(self, player):
		name = player.name
		if name in self._players:
			del self._players[name]

	def __contains__(self, player):
		assert isinstance(player, GameObject)
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

