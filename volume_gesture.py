from gestures import(
    Gesture,
    Landmark,
    INDEX_TIP,
    THUMB_TIP
)
from collections.abc import Sequence

class VolumeGestureController:

    def __init__(self, top_y: float=0.05):
        self.top_y = top_y
        self.drag_active = False
        self.start_y: float | None = None
        self.current_volume: int | None = None

    def update(
        self,
        action_tracking: bool,
        right_gesture: Gesture,
        right_landmarks: Sequence[Landmark] | None,
    ) -> int | None:
        """return a new volume if one needs to be applied"""
        if not action_tracking:
            return None
        if not (right_gesture is Gesture.PINCH):
            return None
        if right_landmarks is None:
            return None

        pinch_y = (
            right_landmarks[THUMB_TIP].y
            + right_landmarks[INDEX_TIP].y
        ) / 2

        if pinch_y <= self.top_y:
            return None

        slider_height = self.start_y - self.top_y
        progress = (self.start_y - pinch_y) / slider_height
        progress = max(0.0, min(1.0, progress))

        volume = round(progress * 100)
        return volume
    