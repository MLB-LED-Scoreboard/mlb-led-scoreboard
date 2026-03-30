import abc
from .update import UpdateStatus
from .config import Config


class PluginData(abc.ABC):

    @abc.abstractmethod
    def __init__(self, config: Config): ...

    @abc.abstractmethod
    def update(self, force: bool = False) -> UpdateStatus: ...
