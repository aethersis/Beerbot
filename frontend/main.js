class InputBackend {
  reportAxes(axes) {
    // Quick and dirty debounce
    if (true || JSON.stringify(this.lastState) != JSON.stringify(axes)) {
      this.lastState = axes;
      this.report(axes);
    }
  }
}


class GamepadBackend extends InputBackend {
  constructor() {
    super();

    this.pollInterval = 50;

    window.addEventListener("gamepadconnected", (e) => {
      console.log("Gamepad connected at index %d: %s. %d buttons, %d axes.",
        e.gamepad.index, e.gamepad.id,
        e.gamepad.buttons.length, e.gamepad.axes.length);

      if (this.poller) {
        clearInterval(this.poller);
      }

      this.poller = setInterval(() => {
        var gp = navigator.getGamepads()[e.gamepad.index];

        this.reportAxes(gp.axes);
      }, this.pollInterval);
    });
    window.addEventListener("gamepaddisconnected", (e) => {
      console.info(e);
      this.reportAxes([0, 0, 0, 0]);
    });
  }
}


class NippleBackend extends InputBackend {
  constructor() {
    super();
    // TODO
    this.left = nipplejs.create({ zone: document.getElementById("left"), size: 200 });
    this.right = nipplejs.create({ zone: document.getElementById("right"), size: 200 });

    this.left.on('move end', this.moved.bind(this));
    this.right.on('move end', this.moved.bind(this));
    this.axes = [0, 0, 0, 0];
  }

  moved(event, data) {
    if (!data.distance) { data.distance = 0; data.angle = {radian: 0}; }
    this.axes[2*event.target.id + 0] = (data.distance * Math.cos(data.angle.radian) / 100);
    this.axes[2*event.target.id + 1] = -(data.distance * Math.sin(data.angle.radian) / 100);
    this.reportAxes(this.axes);
  }
}

/**
 * Converts keyup/down events to -1.0 - 1.0 values
 */
class KeyAxisHandler {
  constructor(keys) {
    this.keys = keys;
    this.value = 0;
    this.state = {};
  }

  /**
   * Processes incoming event. Returns non-null when event has been handled by
   * this axis
   */
  process(event) {
    if (this.keys.includes(event.key)) {
      // event.repeat is broken.
      if (this.state[event.key] == (event.type == 'keydown')) {
        return this.value;
      }

      this.state[event.key] = (event.type == 'keydown');

      let change = 0.0;
      if (this.keys.indexOf(event.key) == (event.type == 'keydown')) {
        change = 1.0;
      } else {
        change = -1.0;
      }

      this.value += change;
      return this.value;
    }

    return null;
  }
}

class KeyboardBackend extends InputBackend {
  constructor() {
    super();

    this.axes = [
      new KeyAxisHandler(['ArrowLeft', 'ArrowRight']),
      new KeyAxisHandler(['ArrowUp', 'ArrowDown']),
      new KeyAxisHandler(['a', 'd']),
      new KeyAxisHandler(['w', 's']),
    ];

    window.addEventListener('keydown', this.handleKeyEvent.bind(this));
    window.addEventListener('keyup', this.handleKeyEvent.bind(this));
  }

  handleKeyEvent(event) {
    for (let axis of this.axes) {
      if (axis.process(event) !== null) {
        this.reportAxes(this.axes.map((a) => a.value));

        // prevent default
        return false;
      }
    }
  }
}

const ws = new WebSocket('ws://' + location.hostname + ':9000');
ws.onopen = (e) => {
  //ws.send('hello');
};

const inputBackends = [
  new GamepadBackend(),
  new NippleBackend(),
  new KeyboardBackend(),
];

for (let backend of inputBackends) {
  backend.report = (axes) => {
    console.info(backend, axes);
    if (ws.readyState == 1) {
      ws.send(JSON.stringify([axes[0], axes[1], axes[2], -axes[3]]));
    }
  }
}

/** Just make it full screen lel */
document.addEventListener("click", function() {
    var el = document.documentElement,
      rfs = el.requestFullscreen
        || el.webkitRequestFullScreen
        || el.mozRequestFullScreen
        || el.msRequestFullscreen 
    ;

    rfs.call(el);
});
