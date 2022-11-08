from enum import Enum

import platform

class StrConst(str, Enum):

    def __str__(self):
        return self.value

    @property
    def str(self):
        """

        Sometimes you really need a true str so here is syntactic sugar

        (e.g. some Pandas operations seem to type check rather than duck type).

        """

        return str(self.value)

class Platform(StrConst):
    LINUX = 'linux'
    WINDOWS = 'windows'
    MAC = 'mac'

PLATFORMS = {'Linux': Platform.LINUX, 'Windows': Platform.WINDOWS, 'Darwin': Platform.MAC}
PLATFORM = PLATFORMS.get(platform.system())
