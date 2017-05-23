#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 23.05.17 16:27
@author: ephtron
"""
from lib.Tile import Tile


class Level:
    instances = 0

    def __init__(self, size):
        """
        Constructor of Level
        :param size: int - defines the grid size of the level
        """
        self.id = Level.instances
        Level.instances += 1
        self.size = size
        self.tiles = {}

        # create n x n tiles
        for y in range(0, self.size):
            for x in range(0, self.size):
                _tile = Tile(self, x, y)
                self.tiles[_tile.get_id()] = _tile

        # set neighbours for every tile
        for idx in self.tiles:
            n_up = None
            if idx - self.size >= 0:
                n_up = self.tiles[idx - self.size]

            n_down = None
            if idx + self.size < len(self.tiles):
                n_down = self.tiles[idx + self.size]

            n_left = None
            if idx - 1 >= 0:
                n_left = self.tiles[idx - 1]

            n_right = None
            if idx + 1 < len(self.tiles):
                n_right = self.tiles[idx + 1]

            self.tiles[idx].set_neighbours(n_up, n_down, n_left, n_right)

    def to_json(self):
        """
        Creates class specific json encode file
        :return: json format 
        """
        json = {"id": self.id,
                "size": self.size,
                "tiles": [self.tiles[idx].to_json() for idx in self.tiles]
                }
        print("json repr:", json)
        return json

    def get_id(self):
        """
        Returns id of this level
        :return: int 
        """
        return self.id

    def get_tiles(self):
        """
        Returns all tiles of this level
        :return: dict<Tile>
        """
        return self.tiles

    def get_tile(self, tile_id):
        """
        Returns tile object with this id 
        :param tile_id: int
        :return: tile_obj or None
        """
        if tile_id in self.tiles:
            return self.tiles[tile_id]
        else:
            return None
