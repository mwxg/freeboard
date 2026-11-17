from pycaw.pycaw import AudioUtilities
import screen_brightness_control as sbc

import ctypes


KEYEVENTF_KEYUP = 0x0002
VK_MEDIA_NEXT_TRACK = 0xB0
VK_MEDIA_PREV_TRACK = 0xB1
VK_MEDIA_STOP = 0xB2
VK_MEDIA_PLAY_PAUSE = 0xB3


def _press_key(key: int) -> None:
    ctypes.windll.user32.keybd_event(key, 0, 0, 0)
    ctypes.windll.user32.keybd_event(key, 0, KEYEVENTF_KEYUP, 0)


class WindowsSystemController:

    def __init__(self):
        self.speaker_device = None
        self.volume_available = False
        self.brightness_available = False

        try:
            self.speaker_device = AudioUtilities.GetSpeakers()
            self.volume_available = True
        except Exception:
            pass

        try:
            sbc.get_brightness(display=0)
            self.brightness_available = True
        except Exception:
            pass

    def get_volume(self) -> int:
        if self.volume_available:
            return round(self.speaker_device.volume_percent)

    def set_volume(self, percent: int) -> None:
        if self.volume_available:
            percent = max(0, min(100, percent))

            self.speaker_device.volume_percent = percent
            self.speaker_device.EndpointVolume.SetMute(percent == 0, None)

    def get_brightness(self, display: int = 0) -> int:
        if self.brightness_available:
            values = sbc.get_brightness(display=display)
            return round(values[0])

    def set_brightness(self, percent: int, display: int = 0) -> None:
        if self.brightness_available:
            percent = max(0, min(100, percent))
            sbc.set_brightness(percent, display=display)

    def next_track(self) -> None:
        _press_key(VK_MEDIA_NEXT_TRACK)

    def previous_track(self) -> None:
        _press_key(VK_MEDIA_PREV_TRACK)

    def toggle_playback(self) -> None:
        _press_key(VK_MEDIA_PLAY_PAUSE)

    def stop_playback(self) -> None:
        _press_key(VK_MEDIA_STOP)