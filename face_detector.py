import cv2
from pathlib import Path


class FaceDetector:

    def __init__(self):

        model_path = (
            Path(__file__).parent
            / "face_detection_yunet_2026may.onnx"
        )

        if not model_path.exists():
            raise FileNotFoundError(
                f"YuNet model not found:\n{model_path}"
            )

        print(
            f"Loading YuNet model: {model_path}"
        )

        self.detector = cv2.FaceDetectorYN.create(
            str(model_path),
            "",
            (320, 320),
            0.6,
            0.3,
            5000
        )

        self.last_width = 320
        self.last_height = 320

        print(
            "YuNet model loaded successfully!"
        )

    # ==========================================
    # UPDATE INPUT SIZE
    # ==========================================

    def _update_input_size(self, frame):

        height, width = frame.shape[:2]

        if (
            width != self.last_width
            or height != self.last_height
        ):

            self.detector.setInputSize(
                (width, height)
            )

            self.last_width = width
            self.last_height = height

    # ==========================================
    # SAFE NUMBER
    # ==========================================

    def _number(self, value):

        try:

            if hasattr(value, "item"):
                value = value.item()

            return float(value)

        except Exception:

            try:

                return float(
                    value.flat[0]
                )

            except Exception:

                return 0.0

    # ==========================================
    # DETECT FACES
    # ==========================================

    def detect_faces(self, frame):

        if frame is None:
            return frame, []

        self._update_input_size(
            frame
        )

        _, detected = (
            self.detector.detect(frame)
        )

        faces = []

        if detected is None:
            return frame, faces

        try:

            for face in detected:

                if len(face) < 4:
                    continue

                x = self._number(
                    face[0]
                )

                y = self._number(
                    face[1]
                )

                w = self._number(
                    face[2]
                )

                h = self._number(
                    face[3]
                )

                if w <= 0 or h <= 0:
                    continue

                faces.append(
                    (
                        int(round(x)),
                        int(round(y)),
                        int(round(w)),
                        int(round(h))
                    )
                )

        except Exception as error:

            print(
                f"Face conversion warning: "
                f"{error}"
            )

        return frame, faces

    # ==========================================
    # DETECT EYES
    # ==========================================
    #
    # YuNet output:
    #
    # face[4]  = right eye X
    # face[5]  = right eye Y
    # face[6]  = left eye X
    # face[7]  = left eye Y
    #
    # These are facial landmarks returned
    # directly by YuNet.
    #
    # ==========================================

    def detect_eyes(
        self,
        frame,
        faces
    ):

        eyes = []

        if frame is None:
            return eyes

        self._update_input_size(
            frame
        )

        try:

            _, detected = (
                self.detector.detect(frame)
            )

        except Exception as error:

            print(
                f"Eye landmark error: {error}"
            )

            return eyes

        if detected is None:
            return eyes

        frame_height, frame_width = (
            frame.shape[:2]
        )

        try:

            for detection in detected:

                if len(detection) < 8:
                    continue

                # ----------------------------------
                # FACE BOX
                # ----------------------------------

                face_x = self._number(
                    detection[0]
                )

                face_y = self._number(
                    detection[1]
                )

                face_w = self._number(
                    detection[2]
                )

                face_h = self._number(
                    detection[3]
                )

                if (
                    face_w <= 0
                    or face_h <= 0
                ):
                    continue

                # ----------------------------------
                # RIGHT EYE
                # ----------------------------------

                right_eye_x = self._number(
                    detection[4]
                )

                right_eye_y = self._number(
                    detection[5]
                )

                # ----------------------------------
                # LEFT EYE
                # ----------------------------------

                left_eye_x = self._number(
                    detection[6]
                )

                left_eye_y = self._number(
                    detection[7]
                )

                # ----------------------------------
                # EYE BOX SIZE
                # ----------------------------------

                eye_width = max(
                    18,
                    int(face_w * 0.18)
                )

                eye_height = max(
                    12,
                    int(face_h * 0.10)
                )

                # ==================================
                # RIGHT EYE BOX
                # ==================================

                rx = int(
                    right_eye_x
                    - eye_width / 2
                )

                ry = int(
                    right_eye_y
                    - eye_height / 2
                )

                rx = max(
                    0,
                    min(
                        rx,
                        frame_width - eye_width
                    )
                )

                ry = max(
                    0,
                    min(
                        ry,
                        frame_height - eye_height
                    )
                )

                eyes.append(
                    (
                        rx,
                        ry,
                        eye_width,
                        eye_height
                    )
                )

                # ==================================
                # LEFT EYE BOX
                # ==================================

                lx = int(
                    left_eye_x
                    - eye_width / 2
                )

                ly = int(
                    left_eye_y
                    - eye_height / 2
                )

                lx = max(
                    0,
                    min(
                        lx,
                        frame_width - eye_width
                    )
                )

                ly = max(
                    0,
                    min(
                        ly,
                        frame_height - eye_height
                    )
                )

                eyes.append(
                    (
                        lx,
                        ly,
                        eye_width,
                        eye_height
                    )
                )

        except Exception as error:

            print(
                f"Eye detection warning: "
                f"{error}"
            )

        return eyes

    # ==========================================
    # DRAW FACES
    # ==========================================

    def draw_faces(
        self,
        frame,
        faces
    ):

        for face in faces:

            if len(face) < 4:
                continue

            x = int(face[0])
            y = int(face[1])
            w = int(face[2])
            h = int(face[3])

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                "Face",
                (
                    x,
                    max(y - 10, 20)
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

        return frame

    # ==========================================
    # DRAW FACES + EYES
    # ==========================================

    def draw_faces_and_eyes(
        self,
        frame,
        faces,
        eyes
    ):

        # ==================================
        # FACE BOXES
        # ==================================

        for face in faces:

            if len(face) < 4:
                continue

            x = int(face[0])
            y = int(face[1])
            w = int(face[2])
            h = int(face[3])

            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                "Face",
                (
                    x,
                    max(y - 10, 20)
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

        # ==================================
        # EYE BOXES
        # ==================================

        for index, eye in enumerate(eyes):

            if len(eye) < 4:
                continue

            ex = int(eye[0])
            ey = int(eye[1])
            ew = int(eye[2])
            eh = int(eye[3])

            cv2.rectangle(
                frame,
                (ex, ey),
                (
                    ex + ew,
                    ey + eh
                ),
                (255, 255, 0),
                2
            )

            cv2.putText(
                frame,
                "Eye",
                (
                    ex,
                    max(ey - 5, 15)
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.45,
                (255, 255, 0),
                1
            )

        return frame

    # ==========================================
    # FACE COUNT
    # ==========================================

    def get_face_count(
        self,
        faces
    ):

        return len(faces)