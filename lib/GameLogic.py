#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 23.05.17 15:26
@author: ephtron
"""

from lib.Player import Player
from lib.Level import Level


class GameLogic:
    def __init__(self):
        """
        Constructor of the GameLogic 
        """
        self.players = {}
        self.levels = {}

        self.create_level(4)

    def create_player(self, player_name):
        """
        Creates a player and adds him to the player dict
        :param player_name: str 
        """
        _player = Player(player_name)
        self.players[_player.get_id()] = Player

    def get_player(self, player_id):
        """
        Returns player object with the corresponding id
        :param player_id: int
        :return: player_obj or None
        """
        if player_id in self.players.keys():
            return self.players[player_id]
        else:
            return None

    def create_level(self, size):
        """
        Creates level object and adds it to the level dict 
        :param size: int 
        """
        _level = Level(size)
        self.levels[_level.get_id()] = _level

    def get_level(self, level_id):
        """
        Returns level bbject
        :param level_id: int
        :return: level_obj or None
        """
        if level_id in self.levels.keys():
            return self.levels[level_id]
        else:
            return None
