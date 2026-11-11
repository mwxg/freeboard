import time
from pathlib import Path

import cv2
import mediapipe as mp

MODEL_PATH = Path("models/hand_landmarker.task")

# check what google wrote for hand_landmarker
# to see visualization of the connections
HAND_CONNECTIONS = (
    (0, 1), (1, 2), (2, 3), (3, 4), # thumb
    (0, 5), (5, 6), (6, 7), (7, 8), # index
    (5, 9), (9, 10), (10, 11), (11, 12), # middle
    (9, 13), (13, 14), (14, 15), (15, 16), # ring
    (13, 17), (17, 18), (18, 19), (19, 20), # pinky
    (0, 17),
)

def draw_hand(frame, landmarks) -> None:
    height, width = frame.shape[:2]
    points = [
        (int(landmark.x * width), int(landmark.y * height)) for landmark in landmarks
    ]

    for start, end in HAND_CONNECTIONS:
        cv2.line(frame, points[start], points[end], (0, 255, 0), 2)

    for point in points:
        cv2.circle(frame, point, 4, (0, 0, 255), -1)

def main() -> None:

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Missing MediaPipe model: {MODEL_PATH}"
        )

    options = mp.tasks.vision.HandLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=str(MODEL_PATH)),
        running_mode=mp.tasks.vision.RunningMode.VIDEO,
        num_hands=1, # change to 2 if 2 handed gestures needed
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5, # basically asks if the hand is still there in the tracked region
        min_tracking_confidence=0.5 # did it successfully track the hand from prev frame?
    )

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        raise RuntimeError("Could not open webcam")

    try:
        # creates the detector with previously defined options
        with mp.tasks.vision.HandLandmarker.create_from_options(
            options
        ) as landmarker:
            while True:
                success, frame = camera.read()

                if not success:
                    print("Could not read a frame")
                    break

                # mirror the image so it feels better
                frame = cv2.flip(frame, 1)

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
                result = landmarker.detect_for_video(
                    mp_image,
                    timestamp_ms
                )

                # skipped if no hand is detected
                if result.hand_landmarks:

                    # num_hands is 1, but if it's 2 it'll just automatically
                    # draw both hands
                    for hand_landmarks in result.hand_landmarks:
                        draw_hand(frame, hand_landmarks)

                    # label to indicate a hand was detected
                    cv2.putText(
                        frame,
                        "Hand detected",
                        (20, 40),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1,
                        (0, 255, 0),
                        2
                    )
                
                cv2.imshow("Freeboard Camera", frame)

                # q closes preview
                if cv2.waitKey(1) & 0xff == ord("q"):
                    break
    finally:
        camera.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()