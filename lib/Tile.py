#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 23.05.17 16:16
@author: ephtron
"""


class Tile:
    instances = 0

    def __init__(self, level_obj, x, y):
        """
        Constructor of a Tile
        In order to init all the neighbours call function 'set_neighbours'
        :param level_obj: Level_obj
        :param x: int - x position on the level grid
        :param y: int - y position on the level grid
        """
        self.id = Tile.instances
        Tile.instances += 1

        self.level = level_obj
        self.position = (x, y)
        self.neighbours = {"up": None,
                           "down": None,
                           "left": None,
                           "right": None
                           }
        self.neighbour_ids = {"up": None,
                              "down": None,
                              "left": None,
                              "right": None
                              }

    def to_json(self):
        """
        Creates class specific json encode file
        :return: json format 
        """
        json = {"id": self.id,
                "level_id": self.level.get_id(),
                "position": self.position,
                "neighbour_ids": self.neighbour_ids
                }
        print("json repr:", json)
        return json

    def get_id(self):
        """
        Returns id of this level
        :return: int 
        """
        return self.id

    def get_position(self):
        """
        Returns position of this tile in the level grid
        :return: (x, y) 
        """
        return self.position

    def get_neighbour(self, key):
        """
        Returns neighbouring tile object 
        :param key: accepts 'up', 'down', 'left' and 'right'
        :return: tile_obj or None
        """
        if key in ['up', 'down', 'left', 'right']:
            return self.neighbours[key]
        else:
            return None

    def get_neighbours(self):
        """
        Returns all neighbouring tiles in a list
        :return: list of tiles 
        """
        return self.neighbours.values()

    def set_neighbours(self, n_up, n_down, n_left, n_right):
        """
        Sets the neighbours of this tile
        Should be called after __init__ when the neighbouring tiles exist
        :param n_up: Tile_obj - neighbouring tile above this tile
        :param n_down: Tile_obj - neighbouring tile below this tile
        :param n_left: Tile_obj - neighbouring tile to the left of this tile
        :param n_right: Tile_obj - neighbouring tile to the right of this tile
        :return: 
        """
        self.neighbours['up'] = n_up
        self.neighbours['down'] = n_down
        self.neighbours['left'] = n_left
        self.neighbours['right'] = n_right

        if n_up is not None:
            self.neighbour_ids['up'] = n_up.get_id()
        if n_down is not None:
            self.neighbour_ids['down'] = n_down.get_id()
        if n_left is not None:
            self.neighbour_ids['left'] = n_left.get_id()
        if n_right is not None:
            self.neighbour_ids['right'] = n_right.get_id()
