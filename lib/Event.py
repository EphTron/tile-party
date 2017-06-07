#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Jun 06.06.17 22:38
@author: ephtron
"""

import uuid


class Event:
    def __init__(self):
        self.id = str(uuid.uuid4())
        self.type = ""
        self.body = ""

    def to_json(self):
        """
        Encodes class to a specific json file
        :return: json format 
        """
        json = {"id": self.id,
                "type": self.type,
                "body": self.body
                }
        return json


class PlayerEnterEvent(Event):
    def __init__(self, body):
        super(PlayerEnterEvent, self).__init__()
        self.type = "player-entered"
        self.body = body

    def __dict__(self):
        return self.to_json()

    def to_json(self):
        """
        Encodes class to a specific json file
        :return: json format 
        """
        json = {"id": self.id,
                "type": self.type,
                "body": self.body
                }
        return json


class MessageEvent(Event):
    def __init__(self, body, player_name):
        super(MessageEvent, self).__init__()
        self.type = "message"
        self.body = body
        self.sender_name = player_name

    def to_json(self):
        """
        Encodes class to a specific json file
        :return: json format 
        """
        json = {"id": self.id,
                "type": self.type,
                "body": self.body,
                "sender_name": self.sender_name
                }
        return json


class GenericEvent(Event):
    def __init__(self, type, body):
        super(GenericEvent, self).__init__()
        self.type = type
        self.body = body

    def to_json(self):
        """
        Encodes class to a specific json file
        :return: json format 
        """
        json = {"id": self.id,
                "type": self.type,
                "body": self.body
                }
        return json
