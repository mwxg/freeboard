import cv2

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QCloseEvent, QImage, QPixmap
from PySide6.QtWidgets import (
    QLabel, QMainWindow,
    QHBoxLayout,
    QMessageBox,
    QWidget,
)

from .config import AppConfig, MODEL_PATH, WINDOW_NAME
from .detector import create_hand_landmarker, detect_hands
from .drawing import draw_hand
from .gestures import Gesture, classify_gesture
from .volume_gesture import VolumeGestureController
from .brightness_gesture import BrightnessGestureController
from .swipe_gesture import SwipeGestureController
from .status_sidebar import StatusSidebar
from .settings_sidebar import SettingsSidebar

from .system_controls import WindowsSystemController


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Missing MediaPipe model: {MODEL_PATH}"
            )

        self.config = AppConfig()

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

        self.settings_sidebar = SettingsSidebar(self.config)
        self.status_sidebar = StatusSidebar()

        main_layout.addWidget(self.settings_sidebar)
        main_layout.addWidget(self.video_label, stretch=1)
        main_layout.addWidget(self.status_sidebar)
        self.setCentralWidget(central_widget)

        self.settings_sidebar.settings_changed.connect(
            self.apply_settings
        )

        # computer actions are enabled only while left index is pointing up
        self.action_tracking = False

        self.camera = cv2.VideoCapture(self.config.camera_index)

        if not self.camera.isOpened():
            raise RuntimeError(
                f"Freeboard could not open camera {self.config.camera_index}.\n\n"
                "Make sure the camera is connected, camera access is enabled "
                "in Windows Settings, and another application is not using it."
            )

        self.camera_index = self.config.camera_index

        self.landmarker = create_hand_landmarker(self.config)

        self.system_control = WindowsSystemController()

        # gesture controllers
        self.volume_gesture = VolumeGestureController(self.system_control, self.config)
        self.brightness_gesture = BrightnessGestureController(self.system_control, self.config)
        self.swipe_gesture = SwipeGestureController(self.config)

        self.frame_timer = QTimer(self)
        self.frame_timer.timeout.connect(self.update_frame)
        self.frame_timer.start(16)

        self.status_sidebar.set_volume(self.system_control.get_volume())
        self.status_sidebar.set_brightness(self.system_control.get_brightness())

    def update_frame(self) -> None:

        # frames start with neutral labels
        self.status_sidebar.reset_frame_status()
        self.action_tracking = False

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
                    "gesture": classify_gesture(hand_landmarks, hand_name, self.config),
                    "confidence": category.score,
                }

                self.status_sidebar.show_hand(
                    hand_name,
                    category.score,
                    hands[hand_name]["gesture"],
                )
                draw_hand(frame, hand_landmarks)

            left_hand = hands.get("left")
            right_hand = hands.get("right")

            if left_hand is not None:
                self.action_tracking = (
                    left_hand["gesture"] is Gesture.INDEX_POINT
                    and left_hand["confidence"] >= 0.8
                )

        self.status_sidebar.set_action_tracking(self.action_tracking)

        volume = self.volume_gesture.update(
            action_tracking=self.action_tracking,
            right_gesture=(
                right_hand["gesture"] if right_hand else None
            ),
            right_landmarks=(
                right_hand["landmarks"] if right_hand else None
            ),
        )

        brightness = self.brightness_gesture.update(
            action_tracking=self.action_tracking,
            right_gesture=(
                right_hand["gesture"] if right_hand else None
            ),
            right_landmarks=(
                right_hand["landmarks"] if right_hand else None
            ),
        )

        if volume is not None:
            self.system_control.set_volume(volume)
            self.status_sidebar.set_volume(self.system_control.get_volume())
            self.status_sidebar.set_last_action("Change volume")

        if brightness is not None:
            self.system_control.set_brightness(brightness)
            self.status_sidebar.set_brightness(self.system_control.get_brightness())
            self.status_sidebar.set_last_action("Change brightness")

        swipe = self.swipe_gesture.update(
            action_tracking=self.action_tracking,
            right_gesture=right_hand["gesture"] if right_hand else None,
            right_landmarks=right_hand["landmarks"] if right_hand else None,
        )

        if swipe == "right":
            self.system_control.next_track()
            self.status_sidebar.set_last_action("Next track")
        elif swipe == "left":
            self.system_control.previous_track()
            self.status_sidebar.set_last_action("Previous track")

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

    def apply_settings(self) -> None:
        self.volume_gesture = VolumeGestureController(
            self.system_control, self.config
        )
        self.brightness_gesture = BrightnessGestureController(
            self.system_control, self.config
        )
        self.swipe_gesture = SwipeGestureController(self.config)

        self.landmarker.close()
        self.landmarker = create_hand_landmarker(self.config)

        if self.camera_index != self.config.camera_index:
            requested_camera_index = self.config.camera_index
            new_camera = cv2.VideoCapture(requested_camera_index)

            if new_camera.isOpened():
                self.camera.release()
                self.camera = new_camera
                self.camera_index = self.config.camera_index
            else:
                new_camera.release()
                self.config.camera_index = self.camera_index
                self.settings_sidebar.load_config()
                QMessageBox.warning(
                    self,
                    "Camera unavailable",
                    "Could not open camera "
                    f"{requested_camera_index}. The previous camera "
                    "will continue to be used.",
                )

    def closeEvent(self, event: QCloseEvent) -> None:
        self.frame_timer.stop()
        self.camera.release()
        self.landmarker.close()

        event.accept()
