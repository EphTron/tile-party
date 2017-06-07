#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 23.05.17 14:45
@author: ephtron
"""

import json
import os.path
import base64, uuid

import tornado.escape
import tornado.web
import tornado.ioloop
from sqlalchemy.orm.collections import _PlainColumnGetter

from tornado import gen
from tornado.options import define, options

from lib.GameLogic import GameLogic
from lib.Event import PlayerEnterEvent, MessageEvent, GenericEvent

define("port", default=8888, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")


class BaseHandler(tornado.web.RequestHandler):
    def initialize(self, logic):
        self.logic = logic

    def get_current_user(self):
        _player_name = self.get_secure_cookie("player")
        if _player_name is not None:
            return _player_name.decode('utf-8')

    def get_current_player_obj(self):
        _player_id = self.get_secure_cookie("player_id")

        if _player_id is not None:
            _player_id = int(_player_id.decode('utf-8'))
            if _player_id in self.logic.players:
                _player = self.logic.get_player(_player_id)
                if _player:
                    return _player

    def set_current_user(self, player_name):
        if player_name:
            self.set_secure_cookie("player", player_name)
            _player_id = self.logic.create_player(player_name)
            self.set_secure_cookie("player_id", str(_player_id))
        else:
            self.clear_cookie("player")
            self.clear_cookie("player_id")


class GameHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("game.html")

    @tornado.web.authenticated
    def post(self):
        _command = self.get_argument('command', '')

        if _command == "start":
            self.redirect(u"/labyrinth/0/0")
        else:
            self.redirect(u"/")


class LabyrinthHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, level_id, tile_id):
        level_id = int(level_id)
        tile_id = int(tile_id)

        # get current level and tile
        _current_level = self.logic.get_level(level_id)
        _current_tile = _current_level.get_tile(tile_id)

        # get player and add her to the current tile
        _player = self.get_current_player_obj()
        print("player: ", _player)
        _current_tile.player_enters(_player)
        _player.set_current_tile(_current_tile)

        # create player-joined event
        # Todo: only send enter event when player really enters, not on refresh
        _event = PlayerEnterEvent(_player.name)
        self.logic.new_event([_event])

        _event_cache_json = json.dumps([event.to_json() for event in self.logic.event_cache])

        self.render("labyrinth.html",
                    tile=_current_tile,
                    tile_json=_current_tile.to_json(),
                    events=_event_cache_json)


class NewEventHandler(BaseHandler):
    def post(self):
        _player = self.get_current_player_obj()
        if _player:
            _event = MessageEvent(self.get_argument("body"), _player.get_name())
            # old code: _event["player"] = self.get_current_user().decode('utf-8')

        # to_basestring is necessary for Python 3's json encoder, which doesn't accept byte strings.
        if self.get_argument("next", None):
            print("get next", self.get_argument("next"))
            self.redirect(self.get_argument("next"))
        else:
            _event_json = _event.to_json()
            print("Writing:", _event_json)
            self.write(_event_json)
        self.logic.new_event([_event])


class EventUpdateHandler(BaseHandler):
    @gen.coroutine
    def post(self):
        print("EventUpdateHandler received post")
        cursor = self.get_argument("cursor", None)
        # print("cursor out: ", cursor)
        # Save the future returned by wait_for_events so we can cancel it in wait_for_events
        self.future = self.logic.wait_for_events(cursor=cursor)
        events = yield self.future
        if self.request.connection.stream.closed():
            print("closed")
            return
            # self.write({'status':'ok'})
        print("my yielded events", events)
        events_json = json.dumps({"events":[event.to_json() for event in events]})

        # json = dict(events=events)
        # _event_cache_json = json.dumps(self.logic.event_cache)
        print("Sending json event:", events_json)
        self.write(events_json)

    def on_connection_close(self):
        print("closed connection")
        self.logic.cancel_wait(self.future)


class LoginHandler(BaseHandler):
    def get(self):
        self.render("login.html")

    def post(self):
        player_name = self.get_argument('player_name', '')

        if player_name is not None:
            if not self.get_secure_cookie('player'):
                self.set_current_user(player_name)

        self.redirect(u"/")


class LogoutHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.clear_cookie("user")
        self.redirect(u"/")

    @tornado.web.authenticated
    def post(self):
        logout = self.get_argument('logout', '')

        if logout == "logout":
            self.clear_cookie("user")
            self.redirect(u"/")


class GameApp(tornado.web.Application):
    def __init__(self, logic):
        handlers = [
            (r"/", GameHandler, dict(logic=logic)),
            (r"/event/new", NewEventHandler, dict(logic=logic)),
            (r"/event/update", EventUpdateHandler, dict(logic=logic)),
            (r"/login", LoginHandler, dict(logic=logic)),
            (r"/logout", LogoutHandler, dict(logic=logic)),
            (r"/labyrinth/([^/]*)/([^/]*)", LabyrinthHandler, dict(logic=logic))
        ]

        # create random + safe cookie_secret key
        secret = base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
        settings = {
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
            "template_path": os.path.join(os.path.dirname(__file__), "templates"),
            "cookie_secret": secret,
            "login_url": "/login",
            "xsrf_cookies": True,
            "debug": options.debug,
        }
        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == "__main__":
    logic = GameLogic()
    app = GameApp(logic)
    app.listen(options.port)

    tornado.ioloop.IOLoop.current().start()
