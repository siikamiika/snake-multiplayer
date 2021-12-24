#!/usr/bin/env python3

import os
import traceback
import uuid
import json
import asyncio

from tornado import websocket, web, ioloop

import game

class Server:
    def __init__(self):
        self._clients = []
        self._game = game.Game(self)

    def start(self):
        self._game.start()

    # client connection handling
    def add_client(self, client):
        if client not in self._clients:
            self._clients.append(client)

    def remove_client(self, client):
        if client in self._clients:
            self._clients.remove(client)

    def handle_message(self, client, message):
        self._game.handle_message(client, json.loads(message))

    # game broadcasts
    def broadcast(self, message):
        message_ser = json.dumps(message)
        i = 0
        while i < len(self._clients):
            client = self._clients[i]
            try:
                client.write_message(message_ser)
            except:
                self._clients.remove(client)
                i -= 1
                traceback.print_exc()
            i += 1

class GameSocketHandler(websocket.WebSocketHandler):
    def initialize(self, server):
        self.server = server

    def check_origin(self, origin):
        return True

    def open(self):
        self.server.add_client(self)

    def on_message(self, message):
        self.server.handle_message(self, message)

    def on_close(self):
        self.server.remove_client(self)

def main():
    server = Server()
    app = web.Application([
        (r'/game', GameSocketHandler, dict(server=server)),
        (r'/(.*)', web.StaticFileHandler, dict(path='client/', default_filename='index.html')),
    ])
    server.start()
    app.listen(8080)
    ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
