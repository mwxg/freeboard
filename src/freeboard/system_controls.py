from pycaw.pycaw import AudioUtilities
import screen_brightness_control as sbc


class WindowsSystemController:

    def __init__(self):
        self.device = AudioUtilities.GetSpeakers()

    def get_volume(self) -> int:
        return round(self.device.volume_percent)

    def set_volume(self, percent: int) -> None:
        percent = max(0, min(100, percent))

        self.device.volume_percent = percent
        self.device.EndpointVolume.SetMute(percent == 0, None)

    def get_brightness(self, display: int = 0) -> int:
        values = sbc.get_brightness(display=display)
        return round(values[0])

    def set_brightness(self, percent: int, display: int = 0) -> None:
        percent = max(0, min(100, percent))
        sbc.set_brightness(percent, display=display)