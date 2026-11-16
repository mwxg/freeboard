from pathlib import Path
from dataclasses import dataclass

PACKAGE_DIR = Path(__file__).resolve().parent
MODEL_PATH = PACKAGE_DIR / "resources" / "hand_landmarker.task"
WINDOW_NAME = "Freeboard"
NUM_HANDS = 2

@dataclass
class AppConfig:
    camera_index: int = 0

    # options for handlandmarker
    min_hand_detection_confidence: float = 0.5
    min_hand_presence_confidence: float = 0.5 # basically asks if the hand is still there in the tracked region
    min_tracking_confidence: float = 0.5 # did it successfully track the hand from prev frame?

    # gesture recognition
    finger_straight_angle: int = 165
    pinch_distance_ratio: float = 0.2 # how close thumb and index fingers are relative to hand size
    im_point_distance_ratio: float = 0.25 # same as above except for the closed peace sign (uses pip joints)

    slider_height: float = 0.5 # 0 to 1 -> relative to screen height

    # _ out _ frames must be stable for a gesture to count
    # used for things like swiping
    stable_required_frames: int = 45
    stable_window_frames: int = 60

    swipe_distance: float = 0.18 # user must swipe at least this far (% of frame width)
    swipe_min_speed: float = 0.65 # frame widths per second
    swipe_max_vertical_drift: float = 0.10 
    swipe_window_seconds: float = 0.35 # only positions from the last _ seconds contribute to swipe detection
    swipe_cooldown_seconds: float = 0.60 # how often you can swipe
