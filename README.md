# Pan-Tilt Face Tracker

OpenCV + YOLO face tracker on Raspberry Pi 4. The Pi does detection and
control; an Arduino drives the two servos over USB serial.

```
final_project/
├── arduino/
│   └── pan_tilt_controller.ino   # flash to Arduino (D9 = pan, D10 = tilt)
├── pi/
│   ├── main.py                   # entry point
│   ├── camera.py                 # picamera2 capture
│   ├── detector.py               # YOLO face detection
│   ├── tracker.py                # P controller, frame-center error -> angles
│   ├── serial_link.py            # USB serial protocol
│   ├── recognizer.py             # optional face recognition (v2)
│   └── config.py                 # all tunables
├── models/                       # put yolov8n-face.pt here
├── faces/                        # (v2) photos of you, for recognition
└── requirements.txt
```

## Hardware

- Raspberry Pi 4 Model B with the camera in the CSI ribbon slot
- Arduino connected to the Pi via USB
- Pan servo on **D9**, tilt servo on **D10**
- Common ground between Arduino and servo supply; servos powered separately
  (don't try to run them off the Arduino 5V rail)

## Setup

1. **Flash the Arduino**: open `arduino/pan_tilt_controller.ino` in the Arduino
   IDE and upload.
2. **On the Pi**:
   ```bash
   cd final_project
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
3. **Get the model**: download a YOLOv8n face model (e.g.
   `yolov8n-face.pt` from akanametov/yolov8-face) into `models/`.
4. **Find the Arduino port**: `ls /dev/ttyACM* /dev/ttyUSB*`. Update
   `SERIAL_PORT` in `pi/config.py` if it isn't `/dev/ttyACM0`.
5. **Run**:
   ```bash
   cd pi
   python3 main.py
   ```
   Ctrl-C to stop.

## Wiring direction

Once the servos arrive, if pan or tilt moves the wrong direction, flip the
sign in `config.py`:

```python
PAN_SIGN  = -1   # change to +1
TILT_SIGN = -1   # change to +1
```

(or swap the 3-pin header — same effect).

## Tuning

- **Twitchy / overshoots**: lower `KP_PAN` / `KP_TILT`.
- **Sluggish**: raise them.
- **Jitters when face isn't moving**: raise `DEADZONE_PX`.
- **Constrain travel** so the camera doesn't try to look at its own mount:
  narrow `PAN_MIN/PAN_MAX` and `TILT_MIN/TILT_MAX`.

## Serial protocol

Pi -> Arduino: `P<angle>,T<angle>\n`, e.g. `P95,T82\n`. Angles 0..180.
Arduino -> Pi: `OK <pan>,<tilt>\n` on each accepted command.

## v2 — track only you

1. Drop several photos of your face into `faces/` (one face per photo, well-lit,
   different angles).
2. `pip install face_recognition` (builds dlib — takes a while on the Pi).
3. Set `USE_RECOGNITION = True` in `config.py`.

This filters detections by identity *after* YOLO finds faces. The YOLO model
itself is not retrained — it stays generic.

## Search-mode TODO (v1.5)

`tracker.update(bbox=None, ...)` currently holds position. To add a sweep,
extend that branch to slowly oscillate `self.pan` between two angles and reset
once a face is seen again.
