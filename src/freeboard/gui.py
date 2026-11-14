import cv2

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QCloseEvent, QImage, QPixmap
from PySide6.QtWidgets import (
    QLabel, QMainWindow,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QFrame,
)

from .config import CAMERA_INDEX, MODEL_PATH, WINDOW_NAME
from .detector import create_hand_landmarker, detect_hands
from .drawing import draw_hand
from .gestures import Gesture, classify_gesture
from .volume_gesture import VolumeGestureController
from .system_volume import WindowsVolumeController


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Missing MediaPipe model: {MODEL_PATH}"
            )

        self.setWindowTitle(WINDOW_NAME)
        self.resize(960, 720)

        # displays each webcam frame
        self.video_label = QLabel()
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet(
            "background-color: #18181b;"
        )

        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)

        main_layout.addWidget(self.video_label, stretch=1)

        sidebar = QFrame()
        sidebar.setMinimumWidth(220)

        sidebar_layout = QVBoxLayout(sidebar)

        title_label = QLabel("Gesture Status")
        self.detection_label = QLabel("No hand detected")
        self.left_hand_label = QLabel("Left hand: --")
        self.right_hand_label = QLabel("Right hand: --")
        self.action_tracking_label = QLabel("Action tracking: inactive")

        self.volume_label = QLabel(f"Volume: -%")

        # computer actions are enabled only while left index is pointing up
        self.action_tracking = False

        sidebar_layout.addWidget(title_label)
        sidebar_layout.addWidget(self.detection_label)
        sidebar_layout.addWidget(self.left_hand_label)
        sidebar_layout.addWidget(self.right_hand_label)
        sidebar_layout.addWidget(self.action_tracking_label)
        sidebar_layout.addWidget(self.volume_label)
        sidebar_layout.addStretch()

        main_layout.addWidget(sidebar)
        self.setCentralWidget(central_widget)

        self.camera = cv2.VideoCapture(CAMERA_INDEX)

        if not self.camera.isOpened():
            raise RuntimeError("Could not open webcam")

        self.landmarker = create_hand_landmarker()

        self.system_volume = WindowsVolumeController()

        # gesture controllers
        self.volume_gesture = VolumeGestureController(self.system_volume)

        self.frame_timer = QTimer(self)
        self.frame_timer.timeout.connect(self.update_frame)
        self.frame_timer.start(16)

        self.volume_label.setText(f"Volume: {self.system_volume.get_volume()}%") # so it doesn't display 0 on opening

    def update_frame(self) -> None:

        # frames start with neutral labels
        self.detection_label.setText("No hand detected")
        self.left_hand_label.setText("Left hand (0.00): --")
        self.right_hand_label.setText("Right hand (0.00): --")
        self.action_tracking = False
        self.action_tracking_label.setText("Action tracking: inactive")

        success, frame = self.camera.read()

        if not success:
            self.video_label.setText("Could not read a frame")
            return

        result = detect_hands(self.landmarker, frame)

        hands = {}
        left_hand = None
        right_hand = None

        if result.hand_landmarks:
            for hand_landmarks, handedness in zip(
                result.hand_landmarks,
                result.handedness,
            ):

                category = handedness[0]
                hand_name = category.category_name.lower()

                hands[hand_name] = {
                    "landmarks": hand_landmarks,
                    "gesture": classify_gesture(hand_landmarks),
                    "confidence": category.score,
                }

                self.detection_label.setText("Hand detected")
                draw_hand(frame, hand_landmarks)

            left_hand = hands.get("left")
            right_hand = hands.get("right")

            if left_hand is not None:
                self.left_hand_label.setText(f"Left hand ({left_hand["confidence"]:.2f}): {left_hand["gesture"].value}")
                self.action_tracking = (
                    left_hand["gesture"] is Gesture.INDEX_POINT
                    and left_hand["confidence"] >= 0.8
                )
            if right_hand is not None:
                self.right_hand_label.setText(f"Right hand ({right_hand["confidence"]:.2f}): {right_hand["gesture"].value}")

        volume = self.volume_gesture.update(
            action_tracking=self.action_tracking,
            right_gesture=(
                right_hand["gesture"] if right_hand else None
            ),
            right_landmarks=(
                right_hand["landmarks"] if right_hand else None
            ),
        )

        if volume is not None:
            self.system_volume.set_volume(volume)
            self.volume_label.setText(f"Volume: {self.system_volume.get_volume()}%")

        if self.action_tracking:
            self.action_tracking_label.setText("Action tracking: active")

        # mirror the image so movement feels natural
        frame = cv2.flip(frame, 1)
        self.display_frame(frame)

    def display_frame(self, frame) -> None:
        # OpenCV uses BGR but Qt expects RGB
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

        # pixmap is optimized for displaying images on screen
        pixmap = QPixmap.fromImage(image)
        scaled_pixmap = pixmap.scaled(
            self.video_label.size(),
            Qt.AspectRatioMode.KeepAspectRatio,

            # can use FastTransformation or SmoothTransformation
            # smooth looks better but takes slightly longer to process
            Qt.TransformationMode.SmoothTransformation,
        )

        self.video_label.setPixmap(scaled_pixmap)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.frame_timer.stop()
        self.camera.release()
        self.landmarker.close()

        event.accept()
