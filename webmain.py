import os.path
import time
import json

# for cookie_secret
import base64, uuid

import logging
import tornado.escape
import tornado.ioloop
import tornado.web

from tornado import gen

from tornado.options import define, options, parse_command_line

from GameLogic import GameLogic, Player, Lobby, ComplexEncoder

define("port", default=8888, help="run on the given port", type=int)
define("debug", default=False, help="run in debug mode")


class BaseHandler(tornado.web.RequestHandler):

    def initialize(self, logic):
        self.logic = logic

    def get_current_user(self):
        user_id = self.get_secure_cookie("user_id")
        user = self.get_secure_cookie("user")
        if user and user_id:
            if user == self.logic.get_player(int(user_id)).name:
                return user

    def get_current_player(self):
        player_id = self.get_secure_cookie("user_id")
        if player_id:
            return self.logic.get_player(int(player_id))

    def get_current_lobby(self):
        lobby_id = self.get_secure_cookie("lobby")
        if lobby_id:
            return self.logic.get_lobby(lobby_id)

    def set_current_user(self, user):
        if user:
            user_id = self.logic.add_player(user)
            self.set_secure_cookie("user_id", str(user_id))
            self.set_secure_cookie("user", user)
        else:
            self.clear_cookie("user")
            self.clear_cookie("user_id")
            self.clear_cookie("lobby")

    def set_current_lobby(self, lobby):
        if lobby:
            self.set_secure_cookie("lobby", lobby.id)
            user = self.get_current_player()
            self.logic.add_player_to_lobby(user, lobby)

        else:
            self.clear_cookie("lobby")



class GameHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        self.render("menu.html")

    @tornado.web.authenticated
    def post(self):
        cmd = self.get_argument('cmd')
        if cmd:
            if cmd=="open":
                lobby_link = self.logic.create_lobby(self.get_current_player())
                self.redirect(u"/lobby/"+lobby_link)
            elif cmd=="join":
                in_lobby = self.get_argument('lobby')
                if in_lobby in self.logic.lobbys:
                    user = self.get_current_player()
                    lobby = self.logic.get_lobby(in_lobby)
                    self.set_current_lobby(lobby)
                    self.redirect(u"/lobby/"+in_lobby)
                else:
                    self.write("Lobby doenst exist!")


class LobbyHandler(BaseHandler):
        
    @tornado.web.authenticated
    def get(self, lobby_id):

        if lobby_id in self.logic.lobbys:
            lobby = self.logic.get_lobby(lobby_id)

            if self.get_current_lobby() != lobby:
                self.set_current_lobby(lobby)
            
            #encode player object to json
            players = []
            for p in lobby.players:
                player = p.reprJSON()
                players.append(player)
                #players.append(p.to_json())

            print("Players as JSON:", players)

            self.render("lobby.html", 
                        players_in_lobby=players)

    def post(self, lobby_id):
        print("Post Lobby")
        if lobby_id in self.logic.lobbys:
            lobby = self.logic.get_lobby(lobby_id)
            
            if self.get_current_lobby() != lobby:
                self.set_current_lobby(lobby)

            state = self.get_argument('ready_button')

            if state:
                print("Input of Post",state)
                player = self.get_current_player()
                player.state = state

            self.redirect(u"/"+str(lobby_id))

            #self.render("lobby.html", 
            #    players_in_lobby=lobby.players)

    def on_connection_close(self):
        user = self.get_current_player()
        self.get_current_lobby().kick_player(user)


class LobbyChangeHandler(BaseHandler):
    def post(self, lobby_id):
        print("Lobby Change Handler")

        player = self.get_current_player()

        new_state =  self.get_argument("state")
        if new_state:
            print("Input of Post",new_state)
            player = self.get_current_player()
            player.state = new_state


        if self.get_argument("next", None):
            self.redirect(self.get_argument("next"))
        else:
            json = player.reprJSON()
            print("Writing Player as JSON:",json)
            self.write(json)

        lobby = self.get_current_lobby()
        lobby.update_player(player)

class LobbyUpdateHandler(BaseHandler):
    @gen.coroutine
    def post(self, lobby_id):
        print("Post Lobby Update")

        if lobby_id in self.logic.lobbys:
            lobby = self.logic.get_lobby(lobby_id)

        cursor = self.get_argument("cursor", None)

        lobby_of_player = self.get_current_lobby()
        if lobby_of_player:
            if lobby_of_player != lobby:
                return

        # Save the future returned by wait_for_messages so we can cancel
        # it in wait_for_messages
        self.future = lobby.wait_for_players(cursor=cursor)
        players = yield self.future

        if self.request.connection.stream.closed():
            return

        p = []
        if hasattr(players,'reprJSON'):
            print("case 1")
            self.write(dict(players=players.reprJSON()))
            print("Sending",players.reprJSON())
        else:
            print("case 2")
            for pla in players:
                p.append(pla.reprJSON())
            self.write(dict(players=p))
            print("Sending",p)

    def on_connection_close(self):
        lobby = self.get_current_lobby()
        lobby.cancel_wait(self.future)

class LoginHandler(BaseHandler):

    def get(self):
        self.render("login.html")

    def post(self):
        user_name = self.get_argument('name','')

        if user_name is not None:
            if not self.get_secure_cookie('user'):
                self.set_current_user(user_name)

        self.redirect(u"/")

class LogoutHandler(BaseHandler):

    @tornado.web.authenticated
    def get(self):
        self.clear_cookie("user")
        self.redirect(u"/")

    @tornado.web.authenticated
    def post(self):
        logout = self.get_argument('logout', '')

        if logout=="logout":
            self.clear_cookie("user")
            self.clear_cookie("user_id")
            self.redirect(u"/")

class ChatMessageHandler(BaseHandler):

    def post(self):
        print("Post Chat Message")
        message = {
            "id": str(uuid.uuid4()),
            "body": self.get_argument("body"),
        }
        # to_basestring is necessary for Python 3's json encoder, which doesn't accept byte strings.
        message["html"] = tornado.escape.to_basestring(
            self.render_string("message.html", message=message))
        if self.get_argument("next", None):
            self.redirect(self.get_argument("next"))
        else:
            self.write(message)

        lobby = self.get_current_lobby()
        lobby.chat.new_messages([message])


class ChatUpdateHandler(BaseHandler):
    @gen.coroutine
    def post(self):
        print("Post Chat Update")
        cursor = self.get_argument("cursor", None)
        print("Chat updater", cursor)
        # Save the future returned by wait_for_messages so we can cancel
        # it in wait_for_messages
        lobby = self.get_current_lobby()
        self.future = lobby.chat.wait_for_messages(cursor=cursor)
        messages = yield self.future
        if self.request.connection.stream.closed():
            return
        self.write(dict(messages=messages))

    def on_connection_close(self):
        lobby = self.get_current_lobby()
        lobby.chat.cancel_wait(self.future)
        
@gen.coroutine
def minute_loop(logic):
    while True:
        print("logged players:", logic.players)
        yield gen.sleep(20)


class CokeApp(tornado.web.Application):

    def __init__(self, logic):
        handlers=[
            (r"/", GameHandler, dict(logic=logic)),
            (r"/lobby/([^/]*)", LobbyHandler, dict(logic=logic)),
            (r"/lobby/([^/]*)/change", LobbyChangeHandler, dict(logic=logic)),
            (r"/lobby/([^/]*)/update", LobbyUpdateHandler, dict(logic=logic)),
            (r"/login", LoginHandler,dict(logic=logic)),
            (r"/logout", LogoutHandler, dict(logic=logic)),
            (r"/chat/new", ChatMessageHandler, dict(logic=logic)),
            (r"/chat/update", ChatUpdateHandler, dict(logic=logic))
        ]

        #create random + safe cookie_secret key
        secret = base64.b64encode(uuid.uuid4().bytes + uuid.uuid4().bytes)
        settings = {
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
            "template_path": os.path.join(os.path.dirname(__file__), "templates"),
            "cookie_secret": secret,
            "login_url": "/login",
            "xsrf_cookies":True,
            "debug":options.debug,
        }
        tornado.web.Application.__init__(self, handlers, **settings)

def make_app():
    logic = GameLogic()
    _app = CokeApp(logic)
    return _app

if __name__ == "__main__":

    logic = GameLogic()
    app = CokeApp(logic)
    app.listen(options.port)

    tornado.ioloop.IOLoop.current().spawn_callback(minute_loop, logic)

    tornado.ioloop.IOLoop.current().start()