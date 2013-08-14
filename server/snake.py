class Snake(object):
    def __init__(self, id, head, length, direction):
        '''
        direction, head should be complex number.
        '''
        self.id = id
        self.body = [head] * length
        self.direction = direction
        self.dead = False

    @property
    def head(self):
        return self.body[0]

    def __len__(self):
        return len(self.body)

    def __iter__(self):
        for b in self.body:
            yield b

    def move(self, map):
        next = self.head + self.direction
        
        if map[next] == 'egg':
            self.body = [next] + self.body # Added new part ahead
        else:
            self.body = [next] + self.body[:-1] # Move last part ahead
        # self.body = [next] + (self.body if map[next] == 'egg' else self.body[:-1])
