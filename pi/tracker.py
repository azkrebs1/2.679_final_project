"""Proportional pan/tilt controller.

Holds last commanded angle when no face is seen (v1 behavior).
Structured so I/D terms or a search routine can drop in later.
"""

import config


class PanTiltTracker:
    def __init__(self):
        self.pan  = float(config.PAN_CENTER)
        self.tilt = float(config.TILT_CENTER)

    def update(self, bbox, frame_w, frame_h):
        if bbox is None:
            return self.pan, self.tilt  # hold

        x1, y1, x2, y2, _ = bbox
        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0
        err_x = cx - frame_w / 2.0
        err_y = cy - frame_h / 2.0

        if abs(err_x) > config.DEADZONE_PX:
            self.pan += config.PAN_SIGN * config.KP_PAN * err_x
        if abs(err_y) > config.DEADZONE_PX:
            self.tilt += config.TILT_SIGN * config.KP_TILT * err_y

        self.pan  = max(config.PAN_MIN,  min(config.PAN_MAX,  self.pan))
        self.tilt = max(config.TILT_MIN, min(config.TILT_MAX, self.tilt))
        return self.pan, self.tilt
