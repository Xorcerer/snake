import gevent
from gevent import monkey
monkey.patch_all()

import copy
import json
import socket
import sys
import time

from snake import Snake
from controller import Controller
from map import Map
from utils import complex_to_position_str as ctps

INIT_LENGTH = 3

last_snake_id = 0
class Player(object):
    def __init__(self, controller):
        self.controller = controller
        self.__snake = None

    @property
    def snake(self):
        snake = self.__snake
        if snake and not snake.dead:
            return snake
        return None

    def new_snake(self, sock):
        snake = self.snake
        if snake:
            return

        global last_snake_id
        last_snake_id += 1
        head = complex(0, 0)
        self.__snake = Snake(last_snake_id, head=head,
                           length=INIT_LENGTH, direction=complex(1, 0))
        self.controller.add_snake(self.__snake)
        sock.send('{ "new_snake": { "id": %d } }' % last_snake_id + '\r\n')

    def set_direction(self, sock, direction):
        snake = self.snake
        if not snake:
            return

        if isinstance(direction, (str, unicode)):
            direction = map(int, direction.split(','))
        d = complex(*direction)
        if sorted((abs(d.imag), abs(d.real))) != [0, 1]:
            return
        snake.direction = d
        print 'snake turned to %s.' % direction

def print_tick():
    sys.stdout.write('tick %d\r' % time.time())
    sys.stdout.flush()

def tick_loop(controller, socks):
    while True:
        gevent.sleep(1)
        controller.tick()
        print_tick()
        data = controller.to_json_dict()
        json_data = json.dumps(data)

        socks_copy = copy.copy(socks)
        for s in socks_copy:
            try:
                s.send(json_data)
                s.send('\r\n')
            except Exception:
                socks.remove(s)

def snake_control_loop(controller, sock):
    player = Player(controller)
    buffer = ''
    while True:
        try:
            new_content = sock.recv(1024)
            if not new_content:
                print 'A client exited.'
                return
        except Exception as e:
            print 'snake_control_loop exited for:', e
            return
        buffer += new_content
        parts = buffer.split('\r\n')
        buffer = parts[-1]
        jsons = parts[:-1]

        for j in jsons:
            print 'decoding command "%s"' % j
            req = json.loads(j)
            action = req['action']
            args = req.get('args') or {}
            try:
                getattr(player, action)(sock=sock, **args)
            except Exception as e:
                print e

def listener_loop(listener, socks, controller):
    while True:
        sock, _ = listener.accept()
        socks.add(sock)
        sock.send('{"map_size": "%s"}\r\n' % ctps(controller.map.size))
        gevent.spawn(snake_control_loop, controller, sock)

def main():
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 10080
    address = '0.0.0.0', port

    listener = socket.socket()
    listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listener.bind(address)
    listener.listen(10)
    print 'Listening on', address
    
    socks = set()

    map = Map(complex(10, 10))
    controller = Controller(map)
    print 'Tick started...'
    task = gevent.spawn(tick_loop, controller, socks)

    listening_task = gevent.spawn(listener_loop, listener, socks, controller)

    gevent.joinall([listening_task, task])
    listener.close()

if __name__ == '__main__':
    main()
