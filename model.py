

class DeviceInfo:
    def __init__(self, driver_name: str = "na", driver_version: str = "na", hw: str = "na"):
        self._driver_name = driver_name
        self._driver_version = driver_version
        self._hw = hw

    @property
    def driver_name(self):
        return self._driver_name

    @property
    def driver_version(self):
        return self._driver_version

    @property
    def hw(self):
        return self._hw


class UseCase:
    def __init__(self, num: int = 0, desc: str = "n.a", fmod1: int = 0, fmod2: int = 0, nr_frames: int = 0,
                 max_expo_us: int = 0):
        self._num = num
        self._description = desc
        self._fmod1 = fmod1
        self._fmod2 = fmod2
        self._nr_of_frames = nr_frames
        self._max_expo_us = max_expo_us

    @property
    def num(self):
        return self._num

    @property
    def description(self):
        return self._description

    @property
    def fmod1(self):
        return self._fmod1

    @property
    def fmod2(self):
        return self._fmod2

    @property
    def nr_of_frames(self):
        return self._nr_of_frames

    @property
    def max_expo_us(self):
        return self._max_expo_us
