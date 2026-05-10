"""Entry point: capture -> detect -> (recognize) -> track -> send."""

import cv2

import config
from camera import Camera
from detector import FaceDetector
from serial_link import ArduinoLink
from tracker import PanTiltTracker


def main():
    cam = Camera()
    detector = FaceDetector()
    tracker = PanTiltTracker()
    link = ArduinoLink()

    recognizer = None
    if config.USE_RECOGNITION:
        from recognizer import FaceRecognizer
        recognizer = FaceRecognizer()

    try:
        while True:
            frame = cam.read()
            small = cv2.resize(frame, (config.INFER_WIDTH, config.INFER_HEIGHT))
            boxes = detector.detect(small)

            if recognizer is not None:
                boxes = [b for b in boxes if recognizer.is_known(small, b)]

            target = FaceDetector.largest(boxes)
            pan, tilt = tracker.update(target, config.INFER_WIDTH, config.INFER_HEIGHT)
            link.send(pan, tilt)

            # 🔴 DRAW BOXES (scale back up)
            sx = frame.shape[1] / config.INFER_WIDTH
            sy = frame.shape[0] / config.INFER_HEIGHT
            for (x1, y1, x2, y2, _conf) in boxes:
                x1 = int(x1 * sx)
                y1 = int(y1 * sy)
                x2 = int(x2 * sx)
                y2 = int(y2 * sy)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            # 🔴 DEBUG OVERLAY: camera center, target center, error arrow, servo signal
            fh, fw = frame.shape[:2]
            cam_cx, cam_cy = fw // 2, fh // 2
            cv2.drawMarker(frame, (cam_cx, cam_cy), (255, 255, 255),
                           markerType=cv2.MARKER_CROSS, markerSize=20, thickness=2)

            err_x = err_y = 0.0
            if target is not None:
                tx1, ty1, tx2, ty2, _ = target
                tcx = int((tx1 + tx2) / 2 * sx)
                tcy = int((ty1 + ty2) / 2 * sy)
                cv2.circle(frame, (tcx, tcy), 5, (0, 0, 255), -1)

                # error in inference coords (matches what the tracker sees)
                err_x = (tx1 + tx2) / 2 - config.INFER_WIDTH / 2
                err_y = (ty1 + ty2) / 2 - config.INFER_HEIGHT / 2

                cv2.arrowedLine(frame, (cam_cx, cam_cy), (tcx, tcy),
                                (0, 255, 255), 2, tipLength=0.2)

            err_mag = (err_x * err_x + err_y * err_y) ** 0.5
            lines = [
                f"err: ({err_x:+.0f},{err_y:+.0f}) |e|={err_mag:.0f}px",
                f"pan={pan:6.2f}  tilt={tilt:6.2f}",
            ]
            for i, txt in enumerate(lines):
                cv2.putText(frame, txt, (8, 20 + 20 * i),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)

            # 🔴 SHOW FRAME
            cv2.imshow("Camera", frame)

            # 🔴 REQUIRED: lets window update
            if cv2.waitKey(1) & 0xFF == 27:  # press ESC to exit
                break
    except KeyboardInterrupt:
        pass
    finally:
        link.close()
        cam.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
