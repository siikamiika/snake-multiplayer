_OPPOSITES = {
    'left': 'right',
    'right': 'left',
    'up': 'down',
    'down': 'up',
}

_DIRECTION_DELTAS = {
    'left': (-1, 0),
    'right': (1, 0),
    'up': (0, -1),
    'down': (0, 1),
}

class Snake:
    def __init__(
        self,
        identifier,
        head=(0, 0),
        length=30,
        start_direction='left'
    ):
        self._identifier = identifier
        self._nodes = [(0, 0), (length, 0)]
        self._nodes = self._get_initial_nodes(head, length, start_direction)
        self._next_direction = None
        self._food_left = 0
        self._alive = True

    def __repr__(self):
        return f'Snake(nodes={self._nodes})'

    def serialize(self):
        return {
            'alive': self._alive,
            'nodes': self._nodes,
        }

    def get_head(self):
        return self._nodes[0]

    def is_alive(self):
        return self._alive

    def set_name(self, name):
        self._name = name

    def eat(self, amount):
        self._food_left += amount

    def kill(self):
        self._alive = False

    def steer(self, direction):
        self._next_direction = direction

    def tick(self):
        direction = self._determine_direction(*self._nodes[:2])
        if self._next_direction:
            if _OPPOSITES.get(direction) != self._next_direction:
                direction = self._next_direction
            head = self._apply_delta(self._nodes[0], direction)
            self._nodes.insert(0, head)
            self._next_direction = None
        else:
            self._nodes[0] = self._apply_delta(self._nodes[0], direction)
        self._consume_tail()

    def intersects_with_snake(self, snake):
        contains = self._contains_point(snake.get_head())
        if snake == self:
            return contains > 1
        return contains > 0

    def _contains_point(self, point):
        contains = 0
        i = 0
        while i + 1 < len(self._nodes):
            edge = self._nodes[i:i + 2]
            if edge[0][0] == edge[1][0] == point[0]:
                a, b = sorted(edge, key=lambda p: p[1])
                if a[1] <= point[1] <= b[1]:
                    contains += 1
            if edge[0][1] == edge[1][1] == point[1]:
                a, b = sorted(edge, key=lambda p: p[0])
                if a[0] <= point[0] <= b[0]:
                    contains += 1
            i += 1
        return contains

    def _get_initial_nodes(self, head, length, start_direction):
        nodes = [head]
        mask = _DIRECTION_DELTAS[_OPPOSITES[start_direction]]
        nodes.append(tuple(a * length + b for a, b in zip(mask, head)))
        return nodes

    def _apply_delta(self, node, direction):
        return tuple(map(sum, zip(node, _DIRECTION_DELTAS[direction])))

    def _determine_direction(self, a, b):
        (x1, y1), (x2, y2) = a, b
        if y1 == y2:
            if x1 < x2:
                return 'left'
            elif x1 > x2:
                return 'right'
        elif x1 == x2:
            if y1 < y2:
                return 'up'
            elif y1 > y2:
                return 'down'
        raise Exception(f'Invalid direction: {self._nodes}')

    def _length_in_direction(self, a, b, direction):
        mask = _DIRECTION_DELTAS[direction]
        for m, a2, b2 in zip(mask, a, b):
            if m:
                return -m * (b2 - a2)
        raise Exception('How did this happen')

    def _consume_tail(self):
        if self._food_left:
            self._food_left -= 1
            return
        tail = self._nodes[-1]
        tail2 = self._nodes[-2]
        direction = self._determine_direction(tail2, tail)
        if self._length_in_direction(tail2, tail, direction) > 1:
            self._nodes[-1] = self._apply_delta(tail, direction)
        else:
            del self._nodes[-1]

def test():
    snake = Snake('foo')
    operations = [
        lambda s: s.tick(),
        lambda s: s.tick(),
        lambda s: s.steer('up'),
        lambda s: s.tick(),
        lambda s: s.steer('right'),
        lambda s: s.eat(1),
        *[lambda s: s.tick() for _ in range(20)],
        lambda s: print(s._contains_point((-1, -1))),
    ]
    for o in operations:
        o(snake)
        print(snake)

if __name__ == '__main__':
    test()
