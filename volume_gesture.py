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

    def reset(self) -> None:
        self.drag_active = False
        self.start_y = None
        self.current_volume = None

    def update(
        self,
        action_tracking: bool,
        right_gesture: Gesture | None,
        right_landmarks: Sequence[Landmark] | None,
    ) -> int | None:
        """return a new volume if one needs to be applied"""
        
        if (
            not action_tracking
            or right_gesture is not Gesture.PINCH
            or right_landmarks is None
        ):
            self.reset()
            return None

        pinch_y = (
            right_landmarks[THUMB_TIP].y
            + right_landmarks[INDEX_TIP].y
        ) / 2

        # set start_y once only when the pinch starts
        if not self.drag_active:
            if pinch_y <= self.top_y:
                return None

            self.drag_active = True
            self.start_y = pinch_y

        # start_y has to exist while dragging
        assert self.start_y is not None

        slider_height = self.start_y - self.top_y
        progress = (self.start_y - pinch_y) / slider_height
        progress = max(0.0, min(1.0, progress))

        volume = round(progress * 100)

        if volume == self.current_volume:
            return None

        self.current_volume = volume
        return volume