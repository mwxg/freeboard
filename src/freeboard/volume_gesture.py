from .gestures import(
    Gesture,
    Landmark,
    INDEX_TIP,
    THUMB_TIP
)
from .config import VOLUME_SLIDER_HEIGHT

from collections.abc import Sequence
from collections import deque

class VolumeGestureController:

    def __init__(self, system_volume):
        self.drag_active = False
        self.start_y: float | None = None
        self.current_volume: int | None = None
        self.start_volume: float | None = None

        # 45/60 of the last 60 frames must be a pinch to be "stable"
        self.pinch_history: deque[bool] = deque(maxlen=60)

        self.system_volume = system_volume

    def reset(self) -> None:
        self.drag_active = False
        self.start_y = None
        self.current_volume = None
        self.pinch_history.clear()
        self.start_volume = None

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

            if sum(self.pinch_history) < 45:
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
            self.drag_active = True
            self.start_y = pinch_y
            self.pinch_history.extend([True] * 60)
            self.start_volume = self.system_volume.get_volume() / 100

        assert self.start_y is not None

        starting_slider_pos = self.start_volume # start at where current volume is
        slider_bottom = self.start_y + (starting_slider_pos * VOLUME_SLIDER_HEIGHT)
        # slider_top = self.start_y - (starting_slider_pos * VOLUME_SLIDER_HEIGHT)

        # where on the slider am I?
        progress = (slider_bottom - pinch_y) / VOLUME_SLIDER_HEIGHT
        progress = max(0.0, min(1.0, progress))

        volume = round(progress * 100)

        if volume == self.current_volume:
            return None

        self.current_volume = volume
        return volume