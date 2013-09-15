# -*- coding: utf-8 -*-

import socket
import select
import json

from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.properties import OptionProperty
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window

SNAKE = 'snake'
MY_SNAKE = 'my-snake'
NOTHING = 'nothing'
EGG = 'egg'
BLOCK = 'block'

HALF_BORDER_WIDTH = 2
def pos_str(x, y):
    return '%d, %d' % (x, y)

class SquareWidget(Widget):
    obj = OptionProperty(NOTHING, options=(NOTHING, SNAKE, MY_SNAKE, EGG, BLOCK))

    def on_obj(self, instance, value):
        with self.canvas:
            Color(*{SNAKE: (0.0, 1.0, 1.0),
                    MY_SNAKE: (0.0, 0.8, 0.8),
                    NOTHING: (0.1, 0.1, 0.1),
                    EGG: (0.0, 0.5, 0.5),
                    BLOCK: (0.8, 0.8, 0.8)}[value])
            Rectangle(pos=(self.pos[0] + HALF_BORDER_WIDTH, self.pos[1] + HALF_BORDER_WIDTH),
                      size=(self.size[0] - HALF_BORDER_WIDTH, self.size[1] - HALF_BORDER_WIDTH))

        self.canvas.ask_update()

class BoardWidget(GridLayout):
    def __init__(self, size):
        super(self.__class__, self).__init__()

        rows, cols = size
        self.rows = rows
        self.cols = cols
        self.widgets = {}

        for i in xrange(self.rows * self.cols):
            sw = SquareWidget()
            pos = i % self.rows, i / self.cols
            sw.pos = pos
            self.widgets[pos_str(*pos)] = sw
            self.add_widget(sw)

    def on_touch_move(self, event):
        if getattr(self, 'moved_in_this_touch', None):
            return

        dx, dy = event.dpos
        main_direction = max(dx, dy)
        if main_direction < 10:
            return super(BoardWidget, self).on_touch_move(event)
        
        self.moved_in_this_touch = True
        # TODO: Turn here. 我不确定我的做法是对的，请随意删改。
        return True

    def on_touch_up(self, event):
        self.moved_in_this_touch = None
        return super(BoardWidget, self).on_touch_up(event)

class SnakeApp(App):
    def update_map(self, map_state):
        items = map_state.get('map') or {}
        snakes = map_state.get('snakes') or {}
        self.snake = snakes.get(self.snake_id) or []
        self.snake = set(self.snake)

        all_snakes_bodies = set(reduce(lambda x, y: x + y, snakes.values(), []))
        for pos, square in self.board.widgets.iteritems():
            if pos in self.snake:
                square.obj = SNAKE
            elif pos in all_snakes_bodies:
                square.obj = MY_SNAKE
            else:
                square.obj = items.get(pos, NOTHING)

    def init_keyboard(self, **kwargs):
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
    
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None
    
    def handle_message(self, content):
        json_obj = json.loads(content)

        if 'snakes' in json_obj:
            self.update_map(json_obj)
        if 'new_snake' in json_obj:
            self.snake_id = json_obj['new_snake']['id']

    def recv(self, time_delta):
        rlist, _, elist = select.select([self.sock], [], [self.sock], 0)
        while rlist:
            content = self.sock.recv(4096)
            if not content:
                print 'Server disconnected.'
                return

            self.buffer += content
            parts = self.buffer.split('\r\n')
            messages = parts[:-1]
            self.buffer = parts[-1]
            for m in messages:
                self.handle_message(m)

            rlist, _, elist = select.select([self.sock], [], [self.sock], 0)


    def init_connection(self):
        self.sock = socket.create_connection(('localhost', 10080))
        self.sock_file = self.sock.makefile()
        self.buffer = ''

        content = self.sock_file.readline()
        map_state = json.loads(content)

        size_str = map_state['map_size']
        self.map_size = map(int, size_str.split(','))

        self.sock.send('{"action": "new_snake"}\r\n')
    
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        direction = None
        if keycode[1] == 'w':
            direction = complex(0, -1)
        elif keycode[1] == 's':
            direction = complex(0, 1)
        elif keycode[1] == 'a':
            direction = complex(-1, 0)
        elif keycode[1] == 'd':
            direction = complex(1, 0)
        else:
            return
        
        command = '{"action":"set_direction", "args":{"direction":"%d, %d"}}\r\n' % (direction.real, direction.imag)
        print command
        self.sock.send(command)

    def build(self):
        self.init_keyboard()
        self.init_connection()

        Clock.schedule_interval(self.recv, 1.0)
        print 'map size: %s' % self.map_size
        self.board = BoardWidget(self.map_size)

        return self.board


if __name__ == '__main__':
    SnakeApp().run()
