from collections import deque
from collections.abc import Sequence
from time import monotonic

from .config import (
    SWIPE_COOLDOWN_SECONDS,
    SWIPE_DISTANCE,
    SWIPE_MAX_VERTICAL_DRIFT,
    SWIPE_MIN_SPEED,
    SWIPE_WINDOW_SECONDS,
)
from .gestures import Gesture, INDEX_TIP, Landmark


class SwipeGestureController:
    def __init__(self) -> None:

        # (timestamp, x, y)
        self.history: deque[tuple[float, float, float]] = deque()

        self.last_swipe_time = float("-inf")
        self.armed = True # if False, won't trigger a swipe

    def reset(self) -> None:
        self.history.clear()
        self.armed = True

    def update(
        self,
        action_tracking: bool,
        right_gesture: Gesture | None,
        right_landmarks: Sequence[Landmark] | None,
    ) -> str | None:
        now = monotonic()

        valid = (
            action_tracking
            and right_gesture is Gesture.INDEX_POINT
            and right_landmarks is not None
        )

        if not valid:
            self.reset()
            return None

        tip = right_landmarks[INDEX_TIP]
        self.history.append((now, tip.x, tip.y))

        # only consider recent movement
        cutoff = now - SWIPE_WINDOW_SECONDS
        while self.history and self.history[0][0] < cutoff:
            self.history.popleft()

        if (
            not self.armed
            or len(self.history) < 2 # need at least two to calculate speed
            or now - self.last_swipe_time < SWIPE_COOLDOWN_SECONDS
        ):
            return None

        start_time, start_x, start_y = self.history[0]
        elapsed = now - start_time

        if elapsed <= 0:
            return None

        dx = tip.x - start_x
        dy = tip.y - start_y
        horizontal_speed = abs(dx) / elapsed

        is_swipe = (
            abs(dx) >= SWIPE_DISTANCE
            and horizontal_speed >= SWIPE_MIN_SPEED
            and abs(dy) <= SWIPE_MAX_VERTICAL_DRIFT
            and abs(dx) > abs(dy) * 2 # ensures movement isn't too diagonal
        )

        if not is_swipe:
            return None

        self.armed = False
        self.last_swipe_time = now
        self.history.clear()

        return "right" if dx > 0 else "left"