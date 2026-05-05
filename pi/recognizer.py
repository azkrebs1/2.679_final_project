"""Optional face recognition (v2).

v1 tracks the largest face in the frame. To track only *you*, drop photos
of your face into config.KNOWN_FACES_DIR and set USE_RECOGNITION = True.

Requires the `face_recognition` library (pulls in dlib — install separately).
"""

import os

import config


class FaceRecognizer:
    def __init__(self, faces_dir=config.KNOWN_FACES_DIR):
        import face_recognition  # lazy import so v1 doesn't need dlib
        self._fr = face_recognition
        self.encodings = []
        for fn in sorted(os.listdir(faces_dir)):
            path = os.path.join(faces_dir, fn)
            img = face_recognition.load_image_file(path)
            encs = face_recognition.face_encodings(img)
            if encs:
                self.encodings.append(encs[0])
        if not self.encodings:
            raise RuntimeError(f"No face encodings found in {faces_dir}")

    def is_known(self, frame, bbox, tolerance=config.RECOG_TOLERANCE):
        x1, y1, x2, y2, _ = bbox
        # face_recognition wants (top, right, bottom, left)
        loc = (int(y1), int(x2), int(y2), int(x1))
        encs = self._fr.face_encodings(frame, known_face_locations=[loc])
        if not encs:
            return False
        matches = self._fr.compare_faces(self.encodings, encs[0], tolerance=tolerance)
        return any(matches)
