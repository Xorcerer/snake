import copy
import random
from utils import complex_to_position_str


class Map(object):
    def __init__(self, size):
        self.size = size
        self.objects = {} # complex : obj_type
        self.last_snapshot = {}

    def __getitem__(self, position):
        return self.objects.get(position)
    
    def __add(self, position, obj_name):
        if position in self.objects:
            return
        self.objects[position] = obj_name

    def add_egg(self, position):
        self.__add(position, 'egg')
        
    def add_block(self, position):
        self.__add(position, 'block')

    def out_of_map(self, snake):
        for body in snake:
            if (body.real < 0 or body.real >= self.size.real
                or body.imag < 0 or body.imag >= self.size.imag):
                return True
        return False
    
    def __check_snakes(self, snakes, snake_bodies):
        dead_snakes = set()
        
        for s in snakes:
            head_cell = snake_bodies[s.head]

            # If more than 1 snake body in the same cell.
            if len(head_cell) > 1 or self.out_of_map(s):
                dead_snakes.add(s)

        return dead_snakes

    def __update_snapshot(self, snake_bodies):
        self.last_snapshot = copy.copy(self.objects)
        self.last_snapshot.update(snake_bodies)

    def random_position(self):
        return complex(random.randint(self.size.real), random.randint(self.size.imag))
    
    def random_empty_cell(self):
        pos = self.last_snapshot.keys()[0]
        while self.last_snapshot.get(pos):
            pos = self.random_position()
        return pos
    
    def draw_and_check_snakes(self, snakes):
        ''' Draw snakes and return dead snakes. '''

        snake_bodies = {}
        for s in snakes:
            for body in s:
                cell = snake_bodies.setdefault(body, [])
                cell.append(s.id)
                if self.objects.get(body) == 'egg':
                    self.objects.pop(body)

        return self.__check_snakes(snakes, snake_bodies), snake_bodies

    def to_json_dict(self):
        result = {}
        for pos, obj in self.objects.iteritems():
            result[complex_to_position_str(pos)] = obj

        return result

