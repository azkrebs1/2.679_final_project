"""Picamera2 wrapper. Returns BGR frames for OpenCV/YOLO."""

import cv2
from picamera2 import Picamera2

import config


class Camera:
    def __init__(self):
        self.picam = Picamera2()
        cfg = self.picam.create_preview_configuration(
            main={"size": (config.CAPTURE_WIDTH, config.CAPTURE_HEIGHT), "format": "RGB888"}
        )
        self.picam.configure(cfg)
        self.picam.start()

    def read(self):
        rgb = self.picam.capture_array()
        return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)

    def close(self):
        self.picam.stop()
