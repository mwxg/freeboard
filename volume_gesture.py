from gestures import(
    Gesture,
    Landmark,
    INDEX_TIP,
    THUMB_TIP
)
from config import VOLUME_SLIDER_PADDING

from collections.abc import Sequence
from collections import deque

class VolumeGestureController:

    def __init__(self, top_y: float=VOLUME_SLIDER_PADDING):
        self.top_y = top_y
        self.drag_active = False
        self.start_y: float | None = None
        self.current_volume: int | None = None

        # 4/5 of the last 5 frames must be a pinch to be "stable"
        self.pinch_history: deque[bool] = deque(maxlen=5)

    def reset(self) -> None:
        self.drag_active = False
        self.start_y = None
        self.current_volume = None
        self.pinch_history.clear()

    def update(
        self,
        action_tracking: bool,
        right_gesture: Gesture | None,
        right_landmarks: Sequence[Landmark] | None,
    ) -> int | None:
        """return a new volume if one needs to be applied"""

        pinch_detected = (
            action_tracking
            and right_gesture is Gesture.PINCH
            and right_landmarks is not None
        )

        if self.drag_active:
            self.pinch_history.append(pinch_detected)

            if sum(self.pinch_history) < 4:
                self.reset()
                return None

            # keep the drag alive but don't update it using an unreliable frame
            if not pinch_detected:
                return None

        elif not pinch_detected:
            return None

        # from here onward this frame has valid pinch landmarks
        assert right_landmarks is not None

        pinch_y = (
            right_landmarks[THUMB_TIP].y
            + right_landmarks[INDEX_TIP].y
        ) / 2

        if not self.drag_active:
            if pinch_y <= self.top_y:
                return None

            self.drag_active = True
            self.start_y = pinch_y
            self.pinch_history.extend([True] * 5)

        assert self.start_y is not None

        slider_height = self.start_y - self.top_y
        progress = (self.start_y - pinch_y) / slider_height
        progress = max(0.0, min(1.0, progress))

        volume = round(progress * 100)

        if volume == self.current_volume:
            return None

        self.current_volume = volume
        return volume