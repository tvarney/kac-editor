
from abc import ABCMeta, abstractmethod

import typing
if typing.TYPE_CHECKING:
    from kac.serialization.enum import BinaryType
    from typing import Any, BinaryIO


class Value(object, metaclass=ABCMeta):
    @abstractmethod
    def set(self, new_value: 'Any') -> None:
        raise NotImplementedError("{}::set() not implemented".format(type(self).__name__))

    @abstractmethod
    def get(self) -> 'Any':
        raise NotImplementedError("{}::get() not implemented".format(type(self).__name__))

    @abstractmethod
    def binary_type(self) -> BinaryType:
        raise NotImplementedError("{}::binary_type() not implemented".format(type(self).__name__))

    @abstractmethod
    def write(self, fp: 'BinaryIO', with_type: bool=True) -> None:
        raise NotImplementedError("{}::write() not implemented".format(type(self).__name__))
