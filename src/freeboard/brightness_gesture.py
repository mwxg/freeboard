from .gestures import(
    Gesture,
    Landmark,
    MIDDLE_PIP,
    INDEX_PIP,
)
from .config import STABLE_RATIO, SLIDER_HEIGHT

from collections.abc import Sequence
from collections import deque

class BrightnessGestureController:

    def __init__(self, system_control):
        self.drag_active = False
        self.start_y: float | None = None
        self.current_brightness: int | None = None
        self.start_brightness: float | None = None

        self.im_point_history: deque[bool] = deque(maxlen=STABLE_RATIO[1])

        self.system_control = system_control

    def reset(self) -> None:
        self.drag_active = False
        self.start_y = None
        self.current_brightness = None
        self.im_point_history.clear()
        self.start_brightness = None

    def update(
        self,
        action_tracking: bool,
        right_gesture: Gesture | None,
        right_landmarks: Sequence[Landmark] | None,
    ) -> int | None:
        """return a new brightness if one needs to be applied"""

        im_point_detected = (
            action_tracking
            and right_gesture is Gesture.IM_POINT
            and right_landmarks is not None
        )

        if self.drag_active:
            self.im_point_history.append(im_point_detected)

            if sum(self.im_point_history) < STABLE_RATIO[0]:
                self.reset()
                return None

            # keep the drag alive but don't update it using an unreliable frame
            if not im_point_detected:
                return None

        elif not im_point_detected:
            return None

        # from here onward this frame has valid pinch landmarks
        assert right_landmarks is not None

        im_point_y = (
            right_landmarks[MIDDLE_PIP].y
            + right_landmarks[INDEX_PIP].y
        ) / 2

        if not self.drag_active:
            self.drag_active = True
            self.start_y = im_point_y
            self.im_point_history.extend([True] * STABLE_RATIO[1])
            self.start_brightness = self.system_control.get_brightness() / 100

        assert self.start_y is not None

        starting_slider_pos = self.start_brightness # start at where current brightness is
        slider_bottom = self.start_y + (starting_slider_pos * SLIDER_HEIGHT)
        # slider_top = self.start_y - (starting_slider_pos * SLIDER_HEIGHT)

        # where on the slider am I?
        progress = (slider_bottom - im_point_y) / SLIDER_HEIGHT
        progress = max(0.0, min(1.0, progress))

        brightness = round(progress * 100)

        if brightness == self.current_brightness:
            return None

        self.current_volume = brightness
        return brightness