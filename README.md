# Freeboard

Freeboard is a desktop prototype that uses a webcam to recognize hand gestures in real time. It is built with MediaPipe, OpenCV, and PySide6, with the goal of mapping gestures to actions such as volume, brightness, and media controls.

## Current features

- Detects and draws landmarks for up to two hands
- Shows each hand's gesture and detection confidence
- Recognizes open palm, pinch, index point, and peace gestures
- Uses a left-hand index point to activate action tracking
- Converts right-hand pinch movement into a volume value from 0 to 100

## Requirements

- Python 3.14 or newer
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- A webcam and permission to access it
- MediaPipe's `hand_landmarker.task` model

## Setup

1. Clone the repository and open its root directory.
2. Download `hand_landmarker.task` and save it as `models/hand_landmarker.task`.
3. Install the dependencies and run the application:

```powershell
uv sync
uv run freeboard
```

Run the application from the repository root so it can find the model.

## Gestures

| Gesture | Current behavior |
| --- | --- |
| Left index point | Activates action tracking |
| Right-hand pinch | Starts volume tracking while action tracking is active |
| Right-hand IM point | Starts brightness tracking while action tracking is active |
| Open palm | Recognition only |
| Peace sign | Recognition only |

<small>"IM point" means pointing with your index and middle finger, like a closed peace sign.</small>

Point upward with your left index finger and hold it there to activate action tracking. The app will not perform any actions if you do not do this.

To try the **volume** gesture, pinch your right thumb and index finger together, and move the pinch up and down. Release the pinch to stop.  
To try the **brightness** gesture, point upward with your right index and middle fingers, and move them up and down. Stop the gesture to stop.  

## Configuration

Camera selection, detection thresholds, gesture sensitivity, and volume-slider padding can be adjusted in `src/freeboard/config.py`.

## Planned work

- Make gesture mappings configurable
- Add automated tests and an in-app settings screen
