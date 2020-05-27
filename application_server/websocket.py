#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging

import os
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
from tornado.options import define, options

define("port", default=8001, help="run on the given port", type=int)

class MainHandler(tornado.websocket.WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        logging.info("A client connected.")

    def on_close(self):
        logging.info("A client disconnected")

    def on_message(self, message):
        from facedetect.detect import get_face_detect_data
        image_data = get_face_detect_data(message)
        if not image_data:
            image_data = message
        self.write_message(image_data)



class Application(tornado.web.Application):
    def __init__(self):
        handlers = [(r"/websocket", MainHandler)]
        settings = dict(debug=True)
        tornado.web.Application.__init__(self, handlers, **settings)


def main():
    #os.environ.setdefault("DJANGO_SETTINGS_MODULE", "liveface.settings")
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()