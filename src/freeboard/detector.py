import time

import cv2
import mediapipe as mp

from .config import AppConfig, NUM_HANDS, MODEL_PATH


def create_hand_landmarker(config: AppConfig):
    options = mp.tasks.vision.HandLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=str(MODEL_PATH)),
        running_mode=mp.tasks.vision.RunningMode.VIDEO,
        num_hands=NUM_HANDS,
        min_hand_detection_confidence=config.min_hand_detection_confidence,
        min_hand_presence_confidence=config.min_hand_presence_confidence,
        min_tracking_confidence=config.min_tracking_confidence,
    )

    return mp.tasks.vision.HandLandmarker.create_from_options(options)


def detect_hands(landmarker, frame):
    # OpenCV represents color in BGR but MediaPipe expects RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # put the frame in a MediaPipe image
    # because the model expects an mp.Image
    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame,
    )

    # video mode needs a timestamp for every frame
    timestamp_ms = time.monotonic_ns() // 1_000_000

    # sends current frame through the hand detector
    return landmarker.detect_for_video(
        mp_image,
        timestamp_ms
    )
