#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 23.05.17 15:47
@author: ephtron
"""

class Player:

    instances = 0

    def __init__(self, player_name):
        self.name = player_name
        self.id = Player.instances
        Player.instances += 1

    def get_id(self):
        return self.id
