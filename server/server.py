import gevent
from gevent import monkey
monkey.patch_all()

import copy
import json
import socket
import sys

from snake import Snake
from controller import Controller
from map import Map


INIT_LENGTH = 3

class Player(object):
    def __init__(self, controller):
        self.controller = controller

    @property
    def snake(self):
        snake = getattr(self, '__snake', None)
        if snake and not snake.dead:
            return snake
        return None

    def new_snake(self):
        snake = self.snake
        if snake:
            return
        
        self.__snake = Snake(1, head=complex(0, 0),
                           length=INIT_LENGTH, direction=complex(1, 0))
        self.controller.add_snake(self.__snake)

    def set_direction(self, direction):
        snake = self.snake
        if not snake:
            return

        d = complex(*direction)
        if sorted((d.imag, d.read)) != (0, 1):
            return
        snake.direction = d

def tick_loop(controller, socks):
    while True:
        gevent.sleep(1)
        controller.tick()
        print 'tick'
        data = controller.to_json_dict()
        json_data = json.dumps(data)

        socks_copy = copy.copy(socks)
        for s in socks_copy:
            try:
                s.send(json_data)
                s.send('\r\n')
            except Exception as e:
                print 'tick_loop exited for:', e
                socks.remove(s)

def snake_control_loop(controller, sock):
    player = Player(controller)
    buffer = ''
    while True:
        try:
            buffer += sock.recv(1024)
        except Exception as e:
            print 'snake_control_loop exited for:', e
            return
        parts = buffer.split('\r\n')
        buffer = parts[-1]
        jsons = parts[:-1]
        
        for j in jsons:
            print 'decoding command "%s"' % j
            req = json.loads(j)
            action = req['action']
            args = req.get('args') or {}
            getattr(player, action)(**args)
        
def main():
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 10080
    listener = socket.socket()
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(('localhost', port))
    listener.listen(10)
    socks = set()

    map = Map(complex(10, 10))    
    controller = Controller(map)
    task = gevent.spawn(tick_loop, controller, socks)

    while True:
        
        sock, _ = listener.accept()
        socks.add(sock)
        gevent.spawn(snake_control_loop, controller, sock)

    gevent.joinall([task])
    listener.close()

if __name__ == '__main__':
    main()
