import cv2

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QCloseEvent, QImage, QPixmap
from PySide6.QtWidgets import QLabel, QMainWindow

from config import CAMERA_INDEX, MODEL_PATH, WINDOW_NAME
from detector import create_hand_landmarker, detect_hands
from drawing import draw_detection_status, draw_gesture_status, draw_hand
from gestures import classify_gesture


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Missing MediaPipe model: {MODEL_PATH}"
            )

        self.setWindowTitle(WINDOW_NAME)
        self.resize(960, 720)

        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet(
            "background-color: #18181b;"
        )

        self.setCentralWidget(self.video_label)

        self.camera = cv2.VideoCapture(CAMERA_INDEX)

        if not self.camera.isOpened():
            raise RuntimeError("Could not open webcam")

        self.landmarker = create_hand_landmarker()

        self.frame_timer = QTimer(self)
        self.frame_timer.timeout.connect(self.update_frame)
        self.frame_timer.start(16)

    def update_frame(self) -> None:
        success, frame = self.camera.read()

        if not success:
            self.video_label.setText("Could not read a frame")
            return

        # Mirror the image so movement feels natural.
        frame = cv2.flip(frame, 1)

        result = detect_hands(self.landmarker, frame)

        if result.hand_landmarks:
            hands_left_to_right = sorted(
                result.hand_landmarks,
                key=lambda hand: hand[0].x,
            )

            for index, hand_landmarks in enumerate(hands_left_to_right):
                if len(hands_left_to_right) == 1:
                    position = "only"
                elif index == 0:
                    position = "left"
                else:
                    position = "right"

                gesture = classify_gesture(hand_landmarks)

                draw_hand(frame, hand_landmarks)
                draw_gesture_status(frame, position, gesture)

            draw_detection_status(frame)

        self.display_frame(frame)

    def display_frame(self, frame) -> None:
        # OpenCV uses BGR; Qt expects RGB here.
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        height, width, _ = rgb_frame.shape
        bytes_per_line = rgb_frame.strides[0]

        image = QImage(
            rgb_frame.data,
            width,
            height,
            bytes_per_line,
            QImage.Format.Format_RGB888,
        ).copy()

        pixmap = QPixmap.fromImage(image)
        scaled_pixmap = pixmap.scaled(
            self.video_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )

        self.video_label.setPixmap(scaled_pixmap)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.frame_timer.stop()
        self.camera.release()
        self.landmarker.close()

        event.accept()