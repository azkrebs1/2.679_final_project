"""USB serial link to the Arduino. Rate-limited, fire-and-forget."""

import time

import serial

import config


class ArduinoLink:
    def __init__(self, port=config.SERIAL_PORT, baud=config.SERIAL_BAUD):
        self.ser = serial.Serial(port, baud, timeout=0.1)
        time.sleep(2.0)  # Arduino auto-resets on serial open
        self._last_send = 0.0
        self._min_interval = 1.0 / config.COMMAND_HZ
        self._last_cmd = (None, None)

    def send(self, pan, tilt):
        p, t = int(round(pan)), int(round(tilt))
        if (p, t) == self._last_cmd:
            return
        now = time.monotonic()
        if now - self._last_send < self._min_interval:
            return
        self._last_send = now
        self._last_cmd = (p, t)
        self.ser.write(f"P{p},T{t}\n".encode())

    def close(self):
        try:
            self.ser.close()
        except Exception:
            pass
