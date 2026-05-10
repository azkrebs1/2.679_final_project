"""PD pan/tilt controller with input smoothing and output rate limiting.

Holds last commanded angle when no face is seen.
Structured so an I term or a search routine can drop in later.
"""

import config


class PanTiltTracker:
    def __init__(self):
        self.pan  = float(config.PAN_CENTER)
        self.tilt = float(config.TILT_CENTER)
        # Smoothed bbox center (in inference-frame pixels). None until first detection.
        self.cx = None
        self.cy = None
        # Previous error, for the D term.
        self.prev_err_x = 0.0
        self.prev_err_y = 0.0

    def reset_track(self):
        """Call when target is lost so D and EMA don't carry stale state."""
        self.cx = None
        self.cy = None
        self.prev_err_x = 0.0
        self.prev_err_y = 0.0

    def update(self, bbox, frame_w, frame_h):
        if bbox is None:
            self.reset_track()
            return self.pan, self.tilt  # hold

        x1, y1, x2, y2, _ = bbox
        raw_cx = (x1 + x2) / 2.0
        raw_cy = (y1 + y2) / 2.0

        # EMA smoothing on the target center.
        a = config.INPUT_EMA_ALPHA
        if self.cx is None:
            self.cx, self.cy = raw_cx, raw_cy
        else:
            self.cx = a * raw_cx + (1 - a) * self.cx
            self.cy = a * raw_cy + (1 - a) * self.cy

        err_x = self.cx - frame_w / 2.0
        err_y = self.cy - frame_h / 2.0

        d_err_x = err_x - self.prev_err_x
        d_err_y = err_y - self.prev_err_y
        self.prev_err_x = err_x
        self.prev_err_y = err_y

        # PD step (in degrees), with deadzone on the P term.
        step_pan = 0.0
        step_tilt = 0.0
        if abs(err_x) > config.DEADZONE_PX:
            step_pan = config.PAN_SIGN * (
                config.KP_PAN * err_x + config.KD_PAN * d_err_x
            )
        if abs(err_y) > config.DEADZONE_PX:
            step_tilt = config.TILT_SIGN * (
                config.KP_TILT * err_y + config.KD_TILT * d_err_y
            )

        # Rate-limit so a noisy frame can't fling the head.
        m = config.MAX_STEP_DEG
        step_pan  = max(-m, min(m, step_pan))
        step_tilt = max(-m, min(m, step_tilt))

        self.pan  += step_pan
        self.tilt += step_tilt

        self.pan  = max(config.PAN_MIN,  min(config.PAN_MAX,  self.pan))
        self.tilt = max(config.TILT_MIN, min(config.TILT_MAX, self.tilt))
        return self.pan, self.tilt
