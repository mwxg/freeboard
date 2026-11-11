import cv2

from config import CAMERA_INDEX, MODEL_PATH, WINDOW_NAME
from detector import create_hand_landmarker, detect_hands
from drawing import draw_detection_status, draw_hand


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

                    # num_hands is 1, but if it's 2 it'll just automatically
                    # draw both hands
                    for hand_landmarks in result.hand_landmarks:
                        draw_hand(frame, hand_landmarks)

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
