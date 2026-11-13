from enum import Enum
from math import acos, degrees, hypot
from typing import Protocol
from collections.abc import Sequence
from .config import (
    FINGER_STRAIGHT_ANGLE, PINCH_DISTANCE_RATIO,
    IM_POINT_DISTANCE_RATIO,
)


# practicing using Protocols
class Landmark(Protocol):
    x: float
    y: float


class Gesture(Enum):
    OPEN_PALM = "open_palm"
    FIST = "fist"
    PINCH = "pinch"
    INDEX_POINT = "index_point"
    PEACE = "peace"
    IM_POINT = "im_point" # means "index middle point" (basically closed peace sign)
    UNKNOWN = "unknown"


# MCP: big knuckle connecting finger to palm
# PIP: middle knuckle closest to palm
# DIP: knuckle closest to fingertip
# TIP: fingertip
WRIST = 0

THUMB_CMC = 1 # right at the wrist
THUMB_MCP = 2
THUMB_IP = 3 # the knuckle right under your thumbnail; thumb is a little different
THUMB_TIP = 4

INDEX_MCP = 5
INDEX_PIP = 6
INDEX_DIP = 7
INDEX_TIP = 8

MIDDLE_MCP = 9
MIDDLE_PIP = 10
MIDDLE_DIP = 11
MIDDLE_TIP = 12

RING_MCP = 13
RING_PIP = 14
RING_DIP = 15
RING_TIP = 16

PINKY_MCP = 17
PINKY_PIP = 18
PINKY_DIP = 19
PINKY_TIP = 20

def distance(a: Landmark, b: Landmark) -> float:
    return hypot(a.x - b.x, a.y - b.y)


def joint_angle(a: Landmark, joint: Landmark, c: Landmark) -> float:
    """return the angle at `joint` in degrees"""

    # two vectors, joint is the origin
    first = (a.x - joint.x, a.y - joint.y)
    second = (c.x - joint.x, c.y - joint.y)

    first_length = hypot(*first)
    second_length = hypot(*second)

    if first_length == 0 or second_length == 0:
        return 0.0

    # cosine of angle between two vectors from linear algebra class...
    # angles spread out from joint
    # e.g. MCP <- PIP -> DIP
    cosine = (
        first[0] * second[0] + first[1] * second[1]
    ) / (first_length * second_length)

    # arccos needs to be in [-1, 1]
    cosine = max(-1.0, min(1.0, cosine))

    return degrees(acos(cosine))


def finger_is_extended(
    landmarks: Sequence[Landmark],
    mcp: int,
    pip: int,
    dip: int,
    tip: int
) -> bool:
    pip_angle = joint_angle(
        landmarks[mcp],
        landmarks[pip],
        landmarks[dip]
    )

    dip_angle = joint_angle(
        landmarks[pip],
        landmarks[dip],
        landmarks[tip]
    )

    conditions = (
        pip_angle > FINGER_STRAIGHT_ANGLE,
        dip_angle > FINGER_STRAIGHT_ANGLE,

        # finger must be oriented upwards
        landmarks[pip].y < landmarks[mcp].y,
        landmarks[dip].y < landmarks[mcp].y,
        landmarks[tip].y < landmarks[mcp].y
    )

    return all(conditions)

def classify_gesture(landmarks: Sequence[Landmark]) -> Gesture:

    # check each finger if it's extended (except thumb)
    fingers = (
        finger_is_extended(landmarks, INDEX_MCP, INDEX_PIP, INDEX_DIP, INDEX_TIP),
        finger_is_extended(landmarks, MIDDLE_MCP, MIDDLE_PIP, MIDDLE_DIP, MIDDLE_TIP),
        finger_is_extended(landmarks, RING_MCP, RING_PIP, RING_DIP, RING_TIP),
        finger_is_extended(landmarks, PINKY_MCP, PINKY_PIP, PINKY_DIP, PINKY_TIP)
    )

    # normalize against hand size because moving away from camera can change it
    hand_size = distance(landmarks[WRIST], landmarks[MIDDLE_MCP])

    pinch_distance = distance(
        landmarks[THUMB_TIP],
        landmarks[INDEX_TIP],
    )

    # used for the two finger point
    ipip_mpip_distance = distance(
        landmarks[INDEX_PIP],
        landmarks[MIDDLE_PIP],
    )

    if hand_size > 0 and pinch_distance / hand_size < PINCH_DISTANCE_RATIO:
        return Gesture.PINCH
    if hand_size > 0 and ipip_mpip_distance / hand_size < IM_POINT_DISTANCE_RATIO:
        return Gesture.IM_POINT
    if all(fingers):
        return Gesture.OPEN_PALM
    if fingers[0] and not any(fingers[1:]):
        return Gesture.INDEX_POINT
    if fingers[0] and fingers[1] and not any(fingers[2:]):
        return Gesture.PEACE

    # no gesture detected
    return Gesture.UNKNOWN