import abc
from .update import UpdateStatus
from .config import PluginConfig


class PluginData(abc.ABC):

    @abc.abstractmethod
    def __init__(self, config: PluginConfig): ...

    @abc.abstractmethod
    def update(self, force: bool = False) -> UpdateStatus: ...
