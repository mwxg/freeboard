
![Freeboard logo](./assets/freeboard.ico)

# Freeboard

Freeboard is a desktop prototype that uses a webcam to recognize hand gestures in real time. It is built with MediaPipe, OpenCV, and PySide6, with the goal of mapping gestures to actions such as volume, brightness, and media controls.

## Current features

- Detects and draws landmarks for up to two hands
- Shows each hand's gesture and detection confidence
- Recognizes open palm, pinch, index point, and peace gestures
- Uses a left-hand index point to activate action tracking
- Converts right-hand pinch movement into a volume value from 0 to 100

## Install on Windows

The packaged installer is intended for 64-bit Windows 10 or Windows 11 and
does not require Python or `uv`.

1. Download `Freeboard-Setup-0.1.0.exe` from the
   [GitHub Releases page](https://github.com/mwxg/freeboard/releases).
2. Run the installer and optionally create a desktop shortcut.
3. Launch Freeboard and allow camera access if Windows requests it.
4. Point upward with your left index finger to activate action tracking, then
   use one of the right-hand gestures described below.

The current installer is not digitally signed, so Microsoft Defender
SmartScreen may warn that Windows protected your PC. If you downloaded the
installer from this repository's Releases page, select **More info**, verify
that the app is Freeboard, and select **Run anyway** to continue.

Freeboard processes camera frames locally for gesture recognition. It does not
save recordings or transmit camera images. You can revoke camera access at any
time in **Windows Settings > Privacy & security > Camera**.

To remove Freeboard, open **Windows Settings > Apps > Installed apps**, find
Freeboard, and select **Uninstall**.

## Development requirements

- Python 3.14 or newer
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- A webcam and permission to access it

## Run from source

1. Clone the repository and open its root directory.
2. Install the dependencies and run the application:

```powershell
uv sync
uv run freeboard
```

The bundled hand-tracking model is resolved relative to the installed
`freeboard` package, so the application can be launched from any directory.

## Gestures

| Gesture | Current behavior |
| --- | --- |
| Left index point | Activates action tracking |
| Right-hand pinch | Starts volume tracking while action tracking is active |
| Right-hand IM point | Starts brightness tracking while action tracking is active |
| Right-hand swipe | Skips to the next media / goes to previous |
| Open palm | Recognition only |
| Peace sign | Recognition only |

*"IM point" means pointing with your index and middle finger, like a closed peace sign.*

Point upward with your left index finger and hold it there to activate action tracking. The app will not perform any actions if you do not do this.

To try the **volume** gesture, pinch your right thumb and index finger together, and move the pinch up and down. Release the pinch to stop.  
To try the **brightness** gesture, point upward with your right index and middle fingers, and move them up and down. Stop the gesture to stop.  
To try the **skip/prev** gesture, point upward with your right index finger and swipe left or right. Try to keep the movement controlled and at a constant speed for best results.

## Settings

| Setting | Description | Expected range |
| --- | --- | --- |
| Camera | Index of the webcam to use. | `0`–`10` |
| Detection confidence | Minimum confidence required for MediaPipe to detect a hand. | `0.00`–`1.00` |
| Presence confidence | Minimum confidence required for a hand to remain present in the tracked region. | `0.00`–`1.00` |
| Tracking confidence | Minimum confidence required to track a hand from the previous frame. | `0.00`–`1.00` |
| Straight finger angle | Minimum joint angle, in degrees, used to consider a finger straight. | `90`–`180` |
| Pinch ratio | Maximum thumb-to-finger distance relative to hand size for recognizing a pinch. | `0.01`–`1.00` |
| IM point ratio | Maximum distance between the index and middle finger joints, relative to hand size, for recognizing an IM point. | `0.01`–`1.00` |
| Slider height | Vertical gesture travel used to move volume or brightness through its full range, relative to frame height. | `0.10`–`1.00` |
| Stable required frames | Number of matching frames required for a gesture to remain active. | `1`–`600` frames |
| Stable window frames | Number of recent frames checked for gesture stability. | `1`–`600` frames |
| Swipe distance | Minimum horizontal swipe distance relative to frame width. | `0.01`–`1.00` frame widths |
| Swipe minimum speed | Minimum horizontal speed required to recognize a swipe. | `0.01`–`10.00` frame widths/second |
| Swipe maximum vertical drift | Maximum vertical movement allowed during a swipe, relative to frame height. | `0.01`–`1.00` frame heights |
| Swipe window (seconds) | Amount of recent movement history used to detect a swipe. | `0.01`–`10.00` seconds |
| Swipe cooldown (seconds) | Minimum delay between recognized swipes. | `0.00`–`10.00` seconds |
