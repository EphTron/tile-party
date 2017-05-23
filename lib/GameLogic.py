#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 23.05.17 15:26
@author: ephtron
"""

from lib.Player import Player

class GameLogic:
    def __init__(self):
        self.players = {}
        self.tiles = {}

    def add_player(self, player_name):
        _player = Player(player_name)
        self.players[_player.get_id()] = Player

    def get_player_by_id(self, player_id):
        if player_id in self.players.keys():
            return self.players[player_id]




