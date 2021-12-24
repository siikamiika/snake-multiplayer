import GameMap from '/js/GameMap.mjs';
import Input from '/js/Input.mjs';

export default class Game {
    constructor() {
        this._socket = null;
        this._state = null;
        this._map = null;
        this._input = null;
        this._snakeId = null;

        this._messageHandlers = {
            'registered': this._onRegistered.bind(this),
            'game_state_update': this._onGameStateUpdate.bind(this),
        };
    }

    start() {
        this._map = new GameMap();

        this._input = new Input();
        this._input.addHandler('KeyW', () => this._sendCommand('input', 'up'));
        this._input.addHandler('KeyA', () => this._sendCommand('input', 'left'));
        this._input.addHandler('KeyS', () => this._sendCommand('input', 'down'));
        this._input.addHandler('KeyD', () => this._sendCommand('input', 'right'));
        this._input.start();

        this._socket = new WebSocket(`ws://${window.location.host}/game`);
        this._socket.addEventListener('open', this._onSocketOpen.bind(this));
        this._socket.addEventListener('message', this._onSocketMessage.bind(this));
    }

    // socket
    _onSocketOpen(_) {
        this._sendCommand('register');
    }

    _onSocketMessage({data: messageData}) {
        const {type, name, data} = JSON.parse(messageData);
        if (type === 'message') {
            this._handleMessage(name, data)
        } else {
            throw Error(`Unrecognized type: ${type}`);
        }
    }

    // communication
    _sendCommand(name, data=null) {
        this._socket.send(JSON.stringify({
            type: 'command',
            name: name,
            data: data,
            snake_id: this._snakeId,
        }));
    }

    _handleMessage(name, data) {
        this._messageHandlers[name](data);
    }

    // game logic event handlers
    _onRegistered(data) {
        this._snakeId = data.id;
    }

    _onGameStateUpdate(data) {
        this._state = data;
        this._map.draw(this._state.snakes);
    }
}
