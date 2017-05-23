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
        self.current_map_id = None

    def to_json(self):
        """
        Creates class specific json encode file
        :return: json format 
        """
        json = {"id": self.id,
                "name": self.name,
                "current_map_id": self.current_map_id
                }
        print("json repr:", json)
        return json

    def get_id(self):
        """
        Returns the id of this player
        :return: int 
        """
        return self.id
