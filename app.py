import cv2

from config import CAMERA_INDEX, MODEL_PATH, WINDOW_NAME
from detector import create_hand_landmarker, detect_hands
from drawing import draw_detection_status, draw_gesture_status, draw_hand
from gestures import classify_gesture


def main() -> None:

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"Missing MediaPipe model: {MODEL_PATH}"
        )

    camera = cv2.VideoCapture(CAMERA_INDEX)

    if not camera.isOpened():
        raise RuntimeError("Could not open webcam")

    try:
        # creates the detector with previously defined options
        with create_hand_landmarker() as landmarker:
            while True:
                success, frame = camera.read()

                if not success:
                    print("Could not read a frame")
                    break

                # mirror the image so it feels better
                frame = cv2.flip(frame, 1)

                result = detect_hands(landmarker, frame)

                # skipped if no hand is detected
                if result.hand_landmarks:

                    hands_left_to_right = sorted(
                        result.hand_landmarks,
                        key=lambda hand: hand[0].x # sort by wrist's x coordinate
                    )

                    # draw one or both hands
                    for index, hand_landmarks in enumerate(hands_left_to_right):
                        if len(hands_left_to_right) == 1:
                            position = "only"

                        elif index == 0:
                            position = "left"
                        else:
                            position = "right"

                        gesture = classify_gesture(hand_landmarks)

                        draw_hand(frame, hand_landmarks)
                        draw_gesture_status(frame, position, gesture)

                    # label to indicate a hand was detected
                    draw_detection_status(frame)

                cv2.imshow(WINDOW_NAME, frame)

                # q closes preview
                if cv2.waitKey(1) & 0xff == ord("q"):
                    break
    finally:
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
