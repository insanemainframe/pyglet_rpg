#!/usr/bin/env python
# -*- coding: utf-8 -*-
from config import *
from server_logger import debug
from engine.errors import *

from engine.enginelib.meta import Solid

from exceptions import NotImplementedError


class Voxel(dict):
	def __init__(self):
		super(Voxel, self).__init__()

		self.__number = 0
		self.__solids = 0
		self.__blocked = 0


	def has_solid(self):
		return bool(self.__solids)

	def is_blocked(self):
		return bool(self.__blocked)

	def add_player(self, player):
		assert not hasattr(player, 'voxel')

		if  player.name not in self:
			if not self.__blocked:
				self.__number += 1
				if isinstance(player, Solid):
					self.__solids += 1
					if not player.is_passable():
						self.__blockers.append(player.name)
				dict.__setitem__(self, player.name, player)
				player.voxel = self
			else:
				raise AlreadyBlocked()
		else:
			raise RuntimeError('%s already in voxel')

	def pop_player(self, player):
		if player.name in self:
			self.__number -= 1
			if isinstance(player, solid):
				self.__solids -= 1
				if name in __blockers:
					self.__blockers.remove(name)
			dict.__delitem__(self, player.name)
			del player.voxel

		else:
			raise KeyError('%s not in voxel dict' % player)

	def block(self, name):
		if name not in self.__blockers:
			self.__blockers.append(name)
		else:
			raise AlreadyBlocked('<%s> already blocks voxel' % name)

	def __setitem__(self):
		raise NotImplementedError()

	def __delitem__(self, key):
		raise NotImplementedError()

