from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from .config import AppConfig


class SettingsSidebar(QFrame):
    settings_changed = Signal()

    def __init__(self, config: AppConfig) -> None:
        super().__init__()
        self.config = config
        self.setMinimumWidth(260)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.camera_index = QSpinBox()
        self.camera_index.setRange(0, 10)

        self.detection_confidence = self._decimal_input(0, 1, 0.05)
        self.presence_confidence = self._decimal_input(0, 1, 0.05)
        self.tracking_confidence = self._decimal_input(0, 1, 0.05)

        self.finger_angle = QSpinBox()
        self.finger_angle.setRange(90, 180)

        self.pinch_ratio = self._decimal_input(0.01, 1, 0.01)
        self.im_point_ratio = self._decimal_input(0.01, 1, 0.01)

        self.slider_height = self._decimal_input(0.1, 1, 0.05)

        self.stable_required_frames = QSpinBox()
        self.stable_required_frames.setRange(1, 600)
        self.stable_window_frames = QSpinBox()
        self.stable_window_frames.setRange(1, 600)

        self.swipe_distance = self._decimal_input(0.01, 1, 0.01)
        self.swipe_min_speed = self._decimal_input(0.01, 10, 0.05)
        self.swipe_max_vertical_drift = self._decimal_input(0.01, 1, 0.01)
        self.swipe_window_seconds = self._decimal_input(0.01, 10, 0.05)
        self.swipe_cooldown_seconds = self._decimal_input(0, 10, 0.05)

        form.addRow("Camera", self.camera_index)
        form.addRow("Detection confidence", self.detection_confidence)
        form.addRow("Presence confidence", self.presence_confidence)
        form.addRow("Tracking confidence", self.tracking_confidence)
        form.addRow("Straight finger angle", self.finger_angle)
        form.addRow("Pinch ratio", self.pinch_ratio)
        form.addRow("IM point ratio", self.im_point_ratio)
        form.addRow("Slider height", self.slider_height)
        form.addRow("Stable required frames", self.stable_required_frames)
        form.addRow("Stable window frames", self.stable_window_frames)
        form.addRow("Swipe distance", self.swipe_distance)
        form.addRow("Swipe minimum speed", self.swipe_min_speed)
        form.addRow("Swipe maximum vertical drift", self.swipe_max_vertical_drift,)
        form.addRow("Swipe window (seconds)", self.swipe_window_seconds)
        form.addRow("Swipe cooldown (seconds)", self.swipe_cooldown_seconds,)

        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self.apply)
        reset_button = QPushButton("Reset to defaults")
        reset_button.clicked.connect(self.reset_to_defaults)

        layout.addLayout(form)
        layout.addWidget(apply_button)
        layout.addWidget(reset_button)
        layout.addStretch()

        self.load_config()

    @staticmethod
    def _decimal_input(
        minimum: float,
        maximum: float,
        step: float,
    ) -> QDoubleSpinBox:
        control = QDoubleSpinBox()
        control.setDecimals(2)
        control.setRange(minimum, maximum)
        control.setSingleStep(step)
        return control

    def load_config(self, config: AppConfig | None = None) -> None:
        config = config or self.config

        self.camera_index.setValue(config.camera_index)
        self.detection_confidence.setValue(config.min_hand_detection_confidence)
        self.presence_confidence.setValue(config.min_hand_presence_confidence)
        self.tracking_confidence.setValue(config.min_tracking_confidence)
        self.finger_angle.setValue(config.finger_straight_angle)
        self.pinch_ratio.setValue(config.pinch_distance_ratio)
        self.im_point_ratio.setValue(config.im_point_distance_ratio)
        self.slider_height.setValue(config.slider_height)
        self.stable_required_frames.setValue(config.stable_required_frames)
        self.stable_window_frames.setValue(config.stable_window_frames)
        self.swipe_distance.setValue(config.swipe_distance)
        self.swipe_min_speed.setValue(config.swipe_min_speed)
        self.swipe_max_vertical_drift.setValue(config.swipe_max_vertical_drift)
        self.swipe_window_seconds.setValue(config.swipe_window_seconds)
        self.swipe_cooldown_seconds.setValue(config.swipe_cooldown_seconds)

    def reset_to_defaults(self) -> None:
        self.load_config(AppConfig())

    def apply(self) -> None:
        self.config.camera_index = self.camera_index.value()
        self.config.min_hand_detection_confidence = self.detection_confidence.value()
        self.config.min_hand_presence_confidence = self.presence_confidence.value()
        self.config.min_tracking_confidence = self.tracking_confidence.value()
        self.config.finger_straight_angle = self.finger_angle.value()
        self.config.pinch_distance_ratio = self.pinch_ratio.value()
        self.config.im_point_distance_ratio = self.im_point_ratio.value()
        self.config.slider_height = self.slider_height.value()
        self.config.stable_required_frames = self.stable_required_frames.value()
        self.config.stable_window_frames = self.stable_window_frames.value()
        self.config.swipe_distance = self.swipe_distance.value()
        self.config.swipe_min_speed = self.swipe_min_speed.value()
        self.config.swipe_max_vertical_drift = self.swipe_max_vertical_drift.value()
        self.config.swipe_window_seconds = self.swipe_window_seconds.value()
        self.config.swipe_cooldown_seconds = self.swipe_cooldown_seconds.value()

        self.settings_changed.emit()
