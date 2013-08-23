from threading import Event
from utils import complex_to_position_str as ctps


class Controller(object):
    def __init__(self, map):
        self.map = map
        self.snakes = set()
        self.ticked = Event()

    def put_random_eggs(self):
        #TODO
        pass

    def add_snake(self, snake):
        self.snakes.add(snake)

    def tick(self):
        for s in self.snakes:
            s.move(self.map)

        deads, snake_map = self.map.draw_and_check_snakes(self.snakes)
        self.snakes = self.snakes - deads

        for s in deads:
            s.dead = True

        self.ticked.set()
        self.ticked.clear()

    def to_json_dict(self):
        return {
            'map': self.map.to_json_dict(),
            'snakes': {s.id: [ctps(b) for b in s.body] for s in self.snakes}
        }
        

def test():
    from map import Map
    from snake import Snake
    
    map = Map(complex(10, 10))
    map.add_egg(complex(5, 0))

    length = 4
    snake = Snake(1, head=complex(0, 0), length=length, direction=complex(1, 0))
    
    controller = Controller(map)
    controller.add_snake(snake)

    for i in xrange(10):
        controller.tick()

    assert snake not in controller.snakes
    assert snake.dead
    assert len(snake) == length + 1
    print 'Snake died at %s' % snake.head

if __name__ == '__main__':
    test()
