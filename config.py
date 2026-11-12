from pathlib import Path

MODEL_PATH = Path("models/hand_landmarker.task")
CAMERA_INDEX = 0 # users may have more than one camera
WINDOW_NAME = "Freeboard Camera"

NUM_HANDS = 1 # change to 2 if 2 handed gestures needed
MIN_HAND_DETECTION_CONFIDENCE = 0.5
MIN_HAND_PRESENCE_CONFIDENCE = 0.5 # basically asks if the hand is still there in the tracked region
MIN_TRACKING_CONFIDENCE = 0.5 # did it successfully track the hand from prev frame?

# Gesture recognition
FINGER_STRAIGHT_ANGLE = 165.0
PINCH_DISTANCE_RATIO = 0.25 # how close thumb and index fingers are relative to hand size