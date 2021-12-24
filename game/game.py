import time
import threading
import asyncio
import uuid
import random

from .snake import Snake

class Game:
    _TICK_DURATION = 0.1

    def __init__(self, server):
        self._server = server
        self._snakes = {}

    def start(self):
        threading.Thread(target=self._tick).start()

    def _tick(self):
        asyncio.set_event_loop(asyncio.new_event_loop())
        previous_tick = time.time() - Game._TICK_DURATION
        while True:
            self._on_tick()
            now = time.time()
            since_tick = now - previous_tick
            previous_tick = now
            time.sleep(max(self._TICK_DURATION * 2 - since_tick, 0))

    def _iter_live_snakes(self):
        for snake in self._snakes.values():
            if not snake.is_alive():
                continue
            yield snake

    def _on_tick(self):
        snakes = [*self._iter_live_snakes()]
        for snake in snakes:
            snake.tick()
        for snake in snakes:
            for snake2 in snakes:
                if snake2.intersects_with_snake(snake):
                    snake.kill()

        self._server.broadcast({
            'type': 'message',
            'name': 'game_state_update',
            'data': {
                'snakes': [s.serialize() for s in self._snakes.values()],
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
            self._snakes[snake_id] = Snake(snake_id, (125, random.randint(0, 125)))
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