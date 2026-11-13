from pycaw.pycaw import AudioUtilities


class WindowsVolumeController:

    def __init__(self):
        self.device = AudioUtilities.GetSpeakers()

    def get_volume(self) -> int:
        return round(self.device.volume_percent)

    def set_volume(self, percent: int) -> None:
        self.device.volume_percent = max(0, min(100, percent))
        self.device.EndpointVolume.SetMute(0, None)
        if self.device.volume_percent == 0:
            self.device.EndpointVolume.SetMute(1, None)