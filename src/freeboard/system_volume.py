from pycaw.pycaw import AudioUtilities


class WindowsVolumeController:

    def __init__(self):
        self.device = AudioUtilities.GetSpeakers()

    def get_volume(self) -> int:
        return round(self.device.volume_percent)

    def set_volume(self, percent: int) -> None:
        percent = max(0, min(100, percent))

        self.device.volume_percent = percent
        self.device.EndpointVolume.SetMute(percent == 0, None)