export default class GameMap {
    constructor() {
        this._element = document.querySelector('#map');
    }

    draw(snakes) {
        const ctx = this._element.getContext('2d');
        ctx.clearRect(0, 0, 500, 500);
        ctx.lineWidth = 5;
        for (const snake of snakes) {
            let x_ = null;
            let y_ = null;
            for (const [x, y] of snake.nodes) {
                if (x_ === null) {
                    [x_, y_] = [x, y];
                    continue;
                }
                ctx.beginPath();
                ctx.moveTo(x_ * 4, y_ * 4);
                ctx.lineTo(x * 4, y * 4);
                ctx.stroke();
                [x_, y_] = [x, y];
            }
        }
    }
}
