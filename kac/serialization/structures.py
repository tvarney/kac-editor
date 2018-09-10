
from kac.serialization.enum import PrimitiveType
from kac.serialization.primitives import String, Int32
from kac.serialization.value import Value

import typing
if typing.TYPE_CHECKING:
    from typing import BinaryIO, List, Optional
    from kac.serialization.primitives import Primitive, StringValue, Int32Value


class ClassTypeInfo(Value):
    @staticmethod
    def read(fp: 'BinaryIO') -> 'ClassTypeInfo':
        class_name = String.read(fp)
        library_id = Int32.read(fp)
        return ClassTypeInfo(class_name.get(), library_id.get())

    def __init__(self, class_name: 'StringValue', library_id: 'Int32Value') -> None:
        Value.__init__(self)
        self._class_name = String(class_name)
        self._library_id = Int32(library_id)

    def write(self, fp: 'BinaryIO') -> None:
        self._class_name.write(fp)
        self._library_id.write(fp)


class ClassInfo(Value):
    def __init__(self, object_id: 'Int32Value', name: 'StringValue', member_count: 'Int32Value',
                 member_names: 'List[StringValue]') -> None:
        self._object_id = Int32(object_id)
        self._name = String(name)
        self._member_count = Int32(member_count)
        self._members = list()
        for i in range(self._member_count.value):
            self._members.append(String(member_names[i]))

    def write(self, fp: 'BinaryIO') -> None:
        self._object_id.write(fp)
        self._name.write(fp)
        self._member_count.write(fp)
        for member_name in self._members:
            member_name.write(fp)


class ValueWithCode(Value):
    @staticmethod
    def read(fp: 'BinaryIO') -> 'ValueWithCode':
        code = PrimitiveType(fp.read(1)[0])
        if code == PrimitiveType.Null:
            return ValueWithCode(code, None)
        value = Primitive.class_from_enum(code).read(fp)
        return ValueWithCode(code, value)

    def __init__(self, code: 'PrimitiveType', value: 'Optional[Primitive]') -> None:
        self._code = PrimitiveType(code)
        self._value = value
        if self._code == PrimitiveType.Null and self._value is not None:
            raise ValueError("Null values may not be assigned a value")
        if self._code != PrimitiveType.Null and self._value is None:
            raise ValueError("Non-Null values must have a valid value")

    @property
    def code(self) -> 'PrimitiveType':
        return self._code

    @property
    def value(self) -> 'Primitive':
        return self._value

    def write(self, fp: 'BinaryIO') -> None:
        fp.write(bytes((self._code, )))
        self._value.write(fp)


# TODO: Implement rest of list methods
# TODO: Add type checking to methods without it
class ArrayOfValueWithCode(Value):
    def __init__(self, items: 'List[ValueWithCode]') -> None:
        self._items = items

    def append(self, value: ValueWithCode) -> None:
        self._items.append(value)

    def insert(self, idx: int, value: ValueWithCode) -> None:
        self._items.insert(idx, value)

    def write(self, fp: 'BinaryIO') -> None:
        length = Int32(len(self._items))
        length.write(fp)
        for item in self._items:
            item.write(fp)

    def __getitem__(self, idx: int) -> ValueWithCode:
        return self._items[idx]

    def __setitem__(self, idx: int, value: ValueWithCode):
        if type(value) is not ValueWithCode:
            raise TypeError("ArrayOfValuesWithCode may only contain instances of ValueWithCode")
        self._items[idx] = value

    def __len__(self) -> int:
        return len(self._items)


# TODO: Implement BinaryMethodCall
class BinaryMethodCall(Value):
    def __init__(self) -> None:
        pass

    def write(self, fp: 'BinaryIO') -> None:
        pass


# TODO: Implement MethodCallArray
class MethodCallArray(Value):
    def __init__(self) -> None:
        pass

    def write(self, fp: 'BinaryIO') -> None:
        pass


# TODO: Implement BinaryMethodReturn
class BinaryMethodReturn(Value):
    def __init__(self) -> None:
        pass

    def write(self, fp: 'BinaryIO') -> None:
        pass


# TODO: Implement MethodReturnCallArray
class MethodReturnCallArray(Value):
    def __init__(self) -> None:
        pass

    def write(self, fp: 'BinaryIO') -> None:
        pass
