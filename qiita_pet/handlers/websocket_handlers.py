# adapted from
# https://gist.github.com/abhinavsingh/6378134
from json import loads

from zmq import Context, SUB, SUBSCRIBE
from zmq.eventloop import ioloop
from zmq.eventloop.zmqstream import ZMQStream
from tornado.websocket import WebSocketHandler
from tornado.gen import engine

from qiita_ware.run import r_server

# all messages are in json format. They must have the following format:
# 'analysis': analysis_id
# 'msg': message to print
# 'command': what command this is from in format datatype#command


class MessageHandler(WebSocketHandler):
    def __init__(self, *args, **kwargs):
        super(MessageHandler, self).__init__(*args, **kwargs)
        self.context = Context()
        self.socket = self.context.socket(SUB)
        self.socket.connect('tcp://127.0.0.1:5560')
        self.stream = ZMQStream(self.socket)
        self.stream.on_recv(self.callback)

    def get_current_user(self):
        user = self.get_secure_cookie("user")
        if user is None:
            return ''
        else:
            return user.strip('" ')

    def on_message(self, msg):
        msginfo = loads(msg)
        # listens for handshake from page
        if "user:" in msginfo['msg']:
            self.channel = msginfo['msg'].split(':')[1]
            self.socket.setsockopt(SUBSCRIBE, self.channel)
            # fight race condition by loading from channel after listen started
            oldmessages = r_server.lrange(self.channel + ':messages', 0, -1)
            if oldmessages is not None:
                for message in oldmessages:
                    self.write_message(message)

    def callback(self, msg):
        if msg.kind == 'message':
            self.write_message(str(msg.body))
