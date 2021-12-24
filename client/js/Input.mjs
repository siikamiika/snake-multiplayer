export default class Input {
    constructor() {
        this._handlers = {};
    }

    start() {
        document.addEventListener('keydown', this._handle.bind(this));
    }

    addHandler(code, handler) {
        if (!this._handlers[code]) {
            this._handlers[code] = [];
        }
        this._handlers[code].push(handler);
    }

    _handle({code}) {
        const handlers = this._handlers[code];
        if (!handlers) { return; }
        for (const handler of handlers) {
            handler();
        }
    }
}
