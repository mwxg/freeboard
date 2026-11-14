from pathlib import Path

MODEL_PATH = Path("models/hand_landmarker.task")
CAMERA_INDEX = 0 # users may have more than one camera
WINDOW_NAME = "Freeboard Camera"

NUM_HANDS = 2
MIN_HAND_DETECTION_CONFIDENCE = 0.5
MIN_HAND_PRESENCE_CONFIDENCE = 0.5 # basically asks if the hand is still there in the tracked region
MIN_TRACKING_CONFIDENCE = 0.5 # did it successfully track the hand from prev frame?

# Gesture recognition
FINGER_STRAIGHT_ANGLE = 165.0
PINCH_DISTANCE_RATIO = 0.2 # how close thumb and index fingers are relative to hand size
IM_POINT_DISTANCE_RATIO = 0.25

# controls
SLIDER_HEIGHT = 0.5 # 0 to 1 -> relative to screen height
VOLUME_SLIDER_PADDING = 0.10 # how far the invisible volume slider is from the top/bottom of the screen

STABLE_RATIO = (45, 60) # [0] of the last [1] frames must be stable for gesture to continue