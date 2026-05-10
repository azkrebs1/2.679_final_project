"""Tunables for the pan-tilt face tracker. Edit here, not in the modules."""

# --- Serial link to Arduino ---
SERIAL_PORT = "/dev/ttyUSB0"   # often /dev/ttyACM0 for Uno/Nano clones; try /dev/ttyUSB0 if not
SERIAL_BAUD = 115200
COMMAND_HZ  = 30               # max commands per second to Arduino

# --- Camera ---
CAPTURE_WIDTH  = 640
CAPTURE_HEIGHT = 480
INFER_WIDTH    = 320           # frame is downscaled to this before inference
INFER_HEIGHT   = 240

# --- Detector ---
MODEL_PATH      = "../models/yolov8n-face.pt"
DETECTION_CONF  = 0.5

# --- Servo limits (degrees) ---
PAN_MIN,  PAN_MAX  = 0, 180
TILT_MIN, TILT_MAX = 0, 180
PAN_CENTER  = 90
TILT_CENTER = 90

# --- Control ---
# Proportional gain in degrees per pixel of error. Tune by hand.
# Frame center is (INFER_WIDTH/2, INFER_HEIGHT/2); max error ~half the frame.
KP_PAN  = 0.05
KP_TILT = 0.05

# Derivative gain in degrees per (pixel/frame) of error change.
# Damps overshoot. Start ~0.5*KP, raise until oscillation stops.
KD_PAN  = 0.02
KD_TILT = 0.02

# EMA smoothing on the bbox center, 0..1. Higher = snappier but noisier.
INPUT_EMA_ALPHA = 0.4

# Max degrees the servo command can change per update. Prevents flicks
# from a single bad detection and reduces servo buzz.
MAX_STEP_DEG = 3.0

# Flip these if the camera moves the wrong direction once servos are wired.
PAN_SIGN  = -1
TILT_SIGN = -1

# Don't twitch on tiny errors.
DEADZONE_PX = 10

# --- Face recognition (v2, optional) ---
USE_RECOGNITION  = False
KNOWN_FACES_DIR  = "faces"
RECOG_TOLERANCE  = 0.6
