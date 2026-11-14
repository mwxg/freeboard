from collections import deque
from collections.abc import Sequence
from time import monotonic

from .config import (
    SWIPE_COOLDOWN_SECONDS,
    SWIPE_DISTANCE,
    SWIPE_MAX_VERTICAL_DRIFT,
    SWIPE_MIN_SPEED,
    SWIPE_WINDOW_SECONDS,
    STABLE_RATIO,
)
from .gestures import Gesture, INDEX_TIP, Landmark


class SwipeGestureController:
    def __init__(self) -> None:

        # (timestamp, x, y)
        self.history: deque[tuple[float, float, float]] = deque()

        # same 45/60 stability requirement
        self.index_point_history: deque[bool] = deque(maxlen=STABLE_RATIO[1])

        self.last_swipe_time = float("-inf")
        self.armed = True # if False, won't trigger a swipe

    def reset(self) -> None:
        self.history.clear()
        self.index_point_history.clear()
        self.armed = True

    def update(
        self,
        action_tracking: bool,
        right_gesture: Gesture | None,
        right_landmarks: Sequence[Landmark] | None,
    ) -> str | None:
        now = monotonic()

        index_point_detected = (
            action_tracking
            and right_gesture is Gesture.INDEX_POINT
            and right_landmarks is not None
        )

        swipe_active = self.history or not self.armed

        if swipe_active:
            self.index_point_history.append(index_point_detected)

            if sum(self.index_point_history) < STABLE_RATIO[0]:
                self.reset()
                return None

            if not index_point_detected:
                return None

        elif not index_point_detected:
            return None

        if not self.history and self.armed:
            self.index_point_history.extend([True])

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

        # flip it because it is reversed
        return "left" if dx > 0 else "right"