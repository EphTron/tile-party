#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 23.05.17 15:26
@author: ephtron
"""

import logging

from lib.Player import Player
from lib.Level import Level

from tornado.concurrent import Future


class GameLogic:
    def __init__(self):
        """
        Constructor of the GameLogic 
        """
        # Event variables
        self.waiters = set()
        self.event_cache = []  # Todo: make event_cache a dict {}
        self.cache_size = 10

        # Game variables and dictonaries
        self.players = {}
        self.levels = {}

        # Init game
        self.create_level(4)

    def wait_for_events(self, cursor=None):
        """
        Constructs a Future event to return to our caller.
        :param cursor: int
        :return: future event_obj
        """
        result_future = Future()
        if cursor:
            new_count = 0
            for event in reversed(self.event_cache):
                if event.id == cursor:
                    break
                new_count += 1
            if new_count:
                result_future.set_result(self.event_cache[-new_count:])
                return result_future
        self.waiters.add(result_future)

        return result_future

    def cancel_wait(self, future):
        """
        Set an empty result to unblock any coroutines waiting.
        :param future: future event
        :return: 
        """
        self.waiters.remove(future)
        future.set_result([])

    def new_event(self, event_list):
        """
        Creates new events and 
        :param event_list: list of event_obj
        :return: 
        """
        logging.info("Sending new message to %r listeners", len(self.waiters))

        for future in self.waiters:
            future.set_result(event_list)
        self.waiters = set()
        self.event_cache.extend(event_list)

        # Todo: when event_cache is a dict - fill it
        # event = event_list[0]
        # self.event_cache[event['id']] = event_list
        if len(self.event_cache) > self.cache_size:
            self.event_cache = self.event_cache[-self.cache_size:]

    def create_player(self, player_name):
        """
        Creates a player and adds him to the player dict
        :param player_name: str 
        """
        _player = Player(player_name)
        self.players[_player.get_id()] = _player
        return _player.get_id()

    def remove_player(self, player_name=None, player_id=None):
        """
        Removes a player from the player dictonary
        :param player_name: str
        :param player_id: id
        :return: 
        """
        if player_id:
            if player_id in self.players:
                del self.player[player_id]
        elif player_name:
            if player_name in self.players.values():
                pass

    def get_player(self, player_id):
        """
        Returns player object with the corresponding id
        :param player_id: int
        :return: player_obj or None
        """
        if player_id in self.players:
            print(player_id, " in ", self.players)
            return self.players[player_id]
        else:
            print(player_id, " not in ", self.players)
            return None

    def get_players(self):
        """
        Return the dictonary with all players
        :return: 
        """
        return self.players

    def create_level(self, size):
        """
        Creates level object and adds it to the level dict 
        :param size: int 
        """
        _level = Level(size)
        print("added level", _level.id)
        self.levels[_level.get_id()] = _level

    def get_level(self, level_id):
        """
        Returns level bbject
        :param level_id: int
        :return: level_obj or None
        """
        if level_id in self.levels:

            return self.levels[level_id]
        else:
            print("error")
            return None
