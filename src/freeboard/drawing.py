import cv2
from .gestures import Gesture


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


def draw_detection_status(frame) -> None:
    cv2.putText(
        frame,
        "Hand detected",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )


def draw_gesture_status(frame, position, gesture: Gesture) -> None:

    y_pos = 80
    
    if position == "only":
        text = f"One hand: {gesture.value}"
    elif position == "left":
        text = f"Left hand: {gesture.value}"
    else:
        text = f"Right hand: {gesture.value}"
        y_pos = 120

    cv2.putText(
        frame,
        text,
        (20, y_pos),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (255, 255, 0),
        2
    )