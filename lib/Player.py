#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 23.05.17 15:47
@author: ephtron
"""


class Player:
    instances = 0

    def __init__(self, player_name):
        """
        Constructor of a player
        :param player_name: str 
        """
        self.id = Player.instances
        Player.instances += 1
        self.name = player_name
        self.current_tile = None

    def to_json(self):
        """
        Creates class specific json encode file
        :return: json format 
        """
        _json = {"id": self.id,
                 "name": self.name
                 }
        if self.current_tile:
            _json["current_tile_id"] = self.current_tile.get_id()
        else:
            _json["current_tile_id"] = None

        print("json repr:", _json)
        return _json

    def get_id(self):
        """
        Returns the id of this player
        :return: int 
        """
        return self.id

    def get_name(self):
        """
        Returns the name of this player
        :return: str 
        """
        return self.name

    def set_current_tile(self, tile_obj):
        """
        Set the current tile the player is on
        :param tile_obj: 
        """
        # Todo: (Later Addon) add a check if the player was able to move onto this tile
        self.current_tile = tile_obj
