#!/usr/bin/env python
###
# File: buildgps_ws.py
# Desc: BuildGPS WebSocket Proxy
# Author(s): Charles `sparticvs' Timko <sparticvs@popebp.com>
###

from tornado.web import Application
from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketHandler

import json
import httplib


class MainHandler(WebSocketHandler):
    def open(self):
        print "WebSocket Opened"

    def on_message(self, message):
        self.write_message(u"You said: " + message)

    def on_close(self):
        print "WebSocket Closed"


APP = Application([
    (r"/buildgps", MainHandler),
])

if __name__ == "__main__":
    APP.listen(8888)
    IOLoop.instance().start()
