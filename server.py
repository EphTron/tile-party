#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on May 23.05.17 14:45
@author: ephtron
"""

import os.path
import base64, uuid

import tornado.web
import tornado.ioloop

from tornado.options import define, options

from lib.GameLogic import GameLogic

define("port", default=8888, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")


class BaseHandler(tornado.web.RequestHandler):
    def initialize(self, logic):
        self.logic = logic

    def get_current_user(self):
        player = self.get_secure_cookie("player")
        if player:
            return player

    def set_current_user(self, player_name):
        if player_name:
            self.set_secure_cookie("player", player_name)
        else:
            self.clear_cookie("player")


class GameHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("game.html")

    @tornado.web.authenticated
    def post(self):
        command = self.get_argument('command', '')

        if command == "start":
            self.redirect(u"/labyrinth/0/0")
        else:
            self.redirect(u"/")


class LabyrinthHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, level_id, tile_id):
        level_id = int(level_id)
        tile_id = int(tile_id)
        print("parameters: ", level_id, tile_id)
        _current_level = self.logic.get_level(level_id)
        print(_current_level)
        _current_tile = _current_level.get_tile(tile_id)

        self.render("labyrinth.html",
                    tile=_current_tile,
                    tile_json=_current_tile.to_json())


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
