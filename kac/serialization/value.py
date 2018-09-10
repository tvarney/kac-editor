
from abc import ABCMeta, abstractmethod

import typing
if typing.TYPE_CHECKING:
    from typing import BinaryIO


class Value(object, metaclass=ABCMeta):
    @abstractmethod
    def write(self, fp: 'BinaryIO') -> None:
        raise NotImplementedError("{}::write() not implemented".format(type(self).__name__))
