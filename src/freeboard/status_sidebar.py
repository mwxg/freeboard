from PySide6.QtWidgets import QFrame, QLabel, QVBoxLayout

from .gestures import Gesture


class StatusSidebar(QFrame):
    def __init__(self) -> None:
        super().__init__()

        self.setMinimumWidth(220)

        layout = QVBoxLayout(self)

        title_label = QLabel("Gesture Status")
        self._detection_label = QLabel("No hand detected")
        self._left_hand_label = QLabel("Left hand: --")
        self._right_hand_label = QLabel("Right hand: --")
        self._action_tracking_label = QLabel("Action tracking: inactive")
        self._volume_label = QLabel("Volume: --%")
        self._brightness_label = QLabel("Brightness: --%")
        self._last_action_label = QLabel("Last action: None")

        layout.addWidget(title_label)
        layout.addWidget(self._detection_label)
        layout.addWidget(self._left_hand_label)
        layout.addWidget(self._right_hand_label)
        layout.addWidget(self._action_tracking_label)
        layout.addWidget(self._volume_label)
        layout.addWidget(self._brightness_label)
        layout.addWidget(self._last_action_label)
        layout.addStretch()

    def reset_frame_status(self) -> None:
        self._detection_label.setText("No hand detected")
        self._left_hand_label.setText("Left hand (0.00): --")
        self._right_hand_label.setText("Right hand (0.00): --")
        self.set_action_tracking(False)

    def show_hand(
        self,
        hand_name: str,
        confidence: float,
        gesture: Gesture,
    ) -> None:
        self._detection_label.setText("Hand detected")
        text = (
            f"{hand_name.title()} hand "
            f"({confidence:.2f}): {gesture.value}"
        )

        if hand_name == "left":
            self._left_hand_label.setText(text)
        elif hand_name == "right":
            self._right_hand_label.setText(text)

    def set_action_tracking(self, active: bool) -> None:
        state = "active" if active else "inactive"
        self._action_tracking_label.setText(f"Action tracking: {state}")

    def set_volume(self, volume: int) -> None:
        self._volume_label.setText(f"Volume: {volume}%")

    def set_brightness(self, brightness: int) -> None:
        self._brightness_label.setText(f"Brightness: {brightness}%")

    def set_last_action(self, action: str) -> None:
        self._last_action_label.setText(f"Last action: {action}")
