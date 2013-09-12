import socket
import json
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.gridlayout import GridLayout
from kivy.properties import OptionProperty
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window

SNAKE = 'Snake'
NOTHING = 'Nothing'
EGG = 'Egg'
WALL = 'Wall'

HALF_BORDER_WIDTH = 2
def pos_str(x, y):
    return '%d, %d' % (x, y)

class SquareWidget(Widget):
    obj = OptionProperty(NOTHING, options=(NOTHING, SNAKE, EGG, WALL))

    def on_obj(self, instance, value):
        with self.canvas:
            Color(*{SNAKE: (0.0, 1.0, 1.0),
                    NOTHING: (0.1, 0.1, 0.1),
                    EGG: (0.0, 0.5, 0.5),
                    WALL: (0.8, 0.8, 0.8)}[value])
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

        for x in xrange(self.rows * self.cols):
            sw = SquareWidget()
            pos = pos_str(x % self.rows, x / self.cols)
            self.widgets[pos] = sw
            self.add_widget(sw)

class SnakeApp(App):
    def init_keyboard(self, **kwargs):
        self._keyboard = Window.request_keyboard(self._keyboard_closed, self)
        self._keyboard.bind(on_key_down=self._on_keyboard_down)
    
    def _keyboard_closed(self):
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None
    
    def recv_once(self, time_delta):
        # TODO: `select` before read.
        content = self.sock_file.readline()
        map_state = json.loads(content)
        snakes = map_state.get('snakes', {})

        all_snakes_bodies = set(reduce(lambda x, y: x + y, snakes.values(), []))

        for pos, square in self.board.widgets.iteritems():
            square.obj = SNAKE if pos in all_snakes_bodies else NOTHING

    def init_connection(self):
        self.sock = socket.create_connection(('localhost', 10080))
        self.sock_file = self.sock.makefile()

        content = self.sock_file.readline()
        map_state = json.loads(content)

        size_str = map_state['map_size']
        self.map_size = map(int, size_str.split(','))

        self.sock.send('{"action": "new_snake"}\r\n')
    
    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        direction = complex(0, 1)
        if keycode[1] == 'w':
            direction = complex(0, 1)
        elif keycode[1] == 's':
            direction = complex(0, -1)
        elif keycode[1] == 'a':
            direction = complex(-1, 0)
        elif keycode[1] == 'd':
            direction = complex(1, 0)
        
        command = '{"action":"set_direction", "args":{"direction":"%d, %d"}}\r\n' % (direction.real, direction.imag)
        print command
        self.sock.send(command)

    def build(self):
        self.init_keyboard()
        self.init_connection()

        Clock.schedule_interval(self.recv_once, 1.0)
        print 'map size: %s' % self.map_size
        self.board = BoardWidget(self.map_size)

        return self.board


if __name__ == '__main__':
    SnakeApp().run()
