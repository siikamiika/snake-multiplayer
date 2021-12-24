import time
import threading
import asyncio
import uuid
import random

from tornado import ioloop

from .snake import Snake

class Game:
    _TICK_DURATION = 0.1

    def __init__(self, server, area_size=(125, 125)):
        self._server = server
        self._area_size = area_size
        self._snakes = {}
        self._food_pos = None
        self._loop = ioloop.IOLoop.current()

    def start(self):
        threading.Thread(target=self._tick).start()

    def _tick(self):
        while True:
            self._loop.add_callback(self._on_tick)
            time.sleep(self._TICK_DURATION)

    def _iter_live_snakes(self):
        for snake in self._snakes.values():
            if not snake.is_alive():
                continue
            yield snake

    def _on_tick(self):
        snakes = [*self._iter_live_snakes()]
        for snake in snakes:
            snake.tick()
            if snake.get_head() == self._food_pos:
                snake.eat(10)
                self._food_pos = None
        for snake in snakes:
            for snake2 in snakes:
                if snake2.intersects_with_snake(snake):
                    snake.kill()
        if self._food_pos is None:
            self._food_pos = (
                random.randint(0, self._area_size[0]),
                random.randint(0, self._area_size[1]),
            )
        self._server.broadcast({
            'type': 'message',
            'name': 'game_state_update',
            'data': {
                'snakes': [s.serialize() for s in self._snakes.values() if s.is_alive()],
                'food_pos': self._food_pos,
            }
        })

    def handle_message(self, client, message):
        if message['type'] == 'command':
            self._handle_command(client, message['name'], message['data'], message['snake_id'])
        else:
            raise Exception(f'Unrecognized type: {message["type"]}')

    def _handle_command(self, client, name, data, snake_id):
        if name == 'register':
            snake_id = uuid.uuid4().hex
            self._snakes[snake_id] = Snake(
                snake_id,
                (
                    self._area_size[0],
                    random.randint(0, self._area_size[1])
                )
            )
            client.write_message(self._generate_message('registered', {'id': snake_id}))
        elif name == 'input':
            if snake_id in self._snakes:
                self._snakes[snake_id].steer(data)

    def _generate_message(self, name, data):
        return {
            'type': 'message',
            'name': name,
            'data': data,
        }
