
from enum import IntEnum, unique
import struct

from kac.serialization.enum import PrimitiveType

import typing
if typing.TYPE_CHECKING:
    from typing import Any, List, Tuple, Union
    ByteValue = Union[int, bytes, 'Byte']
    CharValue = Union[int, bytes, str, 'Char']
    DateTimeValue = Union[int, bytes, Tuple[int, 'DateTime.Kind'], 'DateTime']
    DecimalValue = Union[int, float, bytes, str, 'Decimal']


class Value(object):
    def set(self, new_value: 'Any') -> None:
        raise NotImplementedError()

    def get(self) -> 'Any':
        raise NotImplementedError()


class Primitive(Value):
    def set(self, new_value: 'Any') -> None:
        raise NotImplementedError()

    def get(self) -> 'Any':
        raise NotImplementedError()

    def type(self) -> PrimitiveType:
        raise NotImplementedError()


class Boolean(Primitive):
    @staticmethod
    def _convert(value: 'Any') -> bool:
        return bool(value)

    def __init__(self, value: 'Any') -> None:
        self._value = Boolean._convert(value)

    @property
    def value(self) -> bool:
        return self._value

    @value.setter
    def value(self, new_value: 'Any') -> None:
        self._value = Boolean._convert(new_value)

    def set(self, new_value: 'Any') -> None:
        self._value = Boolean._convert(new_value)

    def get(self) -> bool:
        return self._value

    def type(self) -> PrimitiveType:
        return PrimitiveType.Boolean

    def __bytes__(self) -> bytes:
        return b'\x01' if self._value else b'\x00'


class Byte(Primitive):
    @staticmethod
    def _convert(value: 'ByteValue') -> int:
        if type(value) is Byte:
            return value.value
        if type(value) is int:
            return value & 0xFF
        if type(value) is bytes:
            if len(value) != 1:
                raise ValueError("Byte value must be 1 byte")
            return struct.unpack('b', value)[0]
        raise TypeError("Byte can only be converted from int or bytes, not {}".format(type(value)))

    def __init__(self, value: 'Union[int, bytes, Byte]') -> None:
        self._value = Byte._convert(value)

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, new_value: 'ByteValue') -> None:
        self._value = Byte._convert(new_value)

    def set(self, new_value: 'ByteValue') -> None:
        self._value = Byte._convert(new_value)

    def get(self) -> int:
        return self._value

    def type(self) -> PrimitiveType:
        return PrimitiveType.Byte

    def __bytes__(self) -> bytes:
        return struct.pack('b', self._value)


class Char(Primitive):
    @staticmethod
    def _convert(value: 'CharValue') -> str:
        if type(value) is int:
            return chr(value)
        if type(value) is str:
            if len(value) != 1:
                raise ValueError("Char value must be of length 1")
            return value
        if type(value) is bytes:
            ustr = value.decode('utf-8')
            if len(value) != 1:
                raise ValueError("Char value must be of length 1")
            return ustr
        if type(value) is Char:
            return value.value
        raise TypeError("Char value must be one of int, str, bytes, or Char")

    def __init__(self, value: 'CharValue') -> None:
        self._value = Char._convert(value)

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, new_value: 'CharValue') -> None:
        self._value = Char._convert(new_value)

    def set(self, new_value: 'CharValue') -> None:
        self._value = Char._convert(new_value)

    def get(self) -> str:
        return self._value

    def type(self) -> PrimitiveType:
        return PrimitiveType.Char

    def __bytes__(self) -> bytes:
        return self._value.encode('utf-8')


class DateTime(Primitive):
    MaxValue = 0x1fffffffffffffff
    _Adjust = 0x2000000000000000
    MinValue = -0x2000000000000000

    @unique
    class Kind(IntEnum):
        NoTimeZone = 0
        UtcTime = 1
        LocalTime = 2

    @staticmethod
    def _convert(value: 'DateTimeValue') -> 'Tuple[int, DateTime.Kind]':
        value_type = type(value)
        if value_type is bytes:
            if len(value) != 8:
                raise ValueError("DateTime requires 8 bytes to unpack")
            value = struct.unpack("Q", value)[0]

        if value_type is int:
            kind_value = (value & 0xC000000000000000) >> 62
            tick_value = value & 0x3000000000000000
            return tick_value, DateTime.Kind(kind_value)
        if value_type is Tuple:
            if len(value) != 2:
                raise ValueError("DateTime tuple unpacking requires Tuple[int, DateTime.Kind]")
            tick_value = DateTime._adjust_ticks(value[0])
            kind_value = DateTime.Kind(value[1])
            return tick_value, kind_value
        if value_type is DateTime:
            return value.tuple
        raise TypeError("Invalid type for DateTime, must be one of int, bytes, Tuple[int, DateTime.Kind], or DateTime")

    @staticmethod
    def _adjust_ticks(ticks: int) -> int:
        if ticks < DateTime.MinValue:
            ticks = ~((~ticks) & DateTime.MaxValue)
        elif ticks > DateTime.MaxValue:
            ticks = ticks & DateTime.MaxValue
        return ticks

    def __init__(self, value: 'DateTimeValue') -> None:
        self._ticks, self._kind = DateTime._convert(value)

    @property
    def ticks(self) -> int:
        return self._ticks - DateTime._Adjust

    @ticks.setter
    def ticks(self, new_value: int) -> None:
        self._ticks = DateTime._adjust_ticks(new_value)

    @property
    def kind(self) -> 'DateTime.Kind':
        return self._kind

    @kind.setter
    def kind(self, value: 'Union[DateTime.Kind, int]'):
        self._kind = DateTime.Kind(value)

    @property
    def value(self) -> int:
        return self._kind << 62 | self._ticks

    @value.setter
    def value(self, new_value: 'DateTimeValue') -> None:
        self._ticks, self._kind = DateTime._convert(new_value)

    @property
    def tuple(self) -> 'Tuple[int, DateTime.Kind]':
        return self._ticks, self._kind

    def get(self) -> int:
        return self.value

    def set(self, new_value: 'DateTimeValue') -> None:
        self._ticks, self._kind = DateTime._convert(new_value)

    def type(self) -> PrimitiveType:
        return PrimitiveType.DateTime

    def __bytes__(self) -> bytes:
        return struct.pack("Q", self.value)


class Decimal(Primitive):
    MaxValue = 79228162514264337593543950334

    @staticmethod
    def count_digits(value: str) -> int:
        count = 0
        str_len = len(value)
        for i in range(str_len):
            if 48 <= ord(value[i]) <= 57:
                count += 1
        return count

    @staticmethod
    def round(value: str) -> str:
        str_len = len(value)
        negative = value[0] == '-'
        if str_len <= 29 or (negative and str_len == 30):
            return value

        decimal_idx = -1
        digits = 0
        last_idx = 0
        chars = list()  # type: List[str]
        for i in range(str_len):
            chars.append(value[i])
            if value[i] == '.':
                decimal_idx = i
            if 48 <= ord(value[i]) <= 57:
                digits += 1
            if digits == 29:
                last_idx = i
                break

        # Either we were less than 29 digits or exactly 29 digits
        if last_idx == 0 or len(chars) == str_len:
            return value

        if decimal_idx == -1:
            if negative:
                return "-" + str(Decimal.MaxValue)
            return str(Decimal.MaxValue)

        next_val = int(value[last_idx + 1])
        if next_val < 5:
            return ''.join(chars)

        # Actually round
        round_past_decimal = False
        first_digit = 1 if negative else 0
        remainder = 1
        while remainder and last_idx >= first_digit:
            current = ord(chars[last_idx]) - 48
            current += remainder
            if current >= 10:
                current = 0
                remainder = 1
            else:
                remainder = 0
            chars[last_idx] = chr(current + 48)
            if last_idx - 1 == decimal_idx:
                last_idx -= 2
                round_past_decimal = True
            else:
                last_idx -= 1

        if remainder == 1:
            chars.insert(first_digit, '1')

        if round_past_decimal:
            return ''.join(chars[0:decimal_idx])
        return ''.join(chars[0:last_idx + 2])

    @staticmethod
    def verify(value: str) -> bool:
        digits = 0
        str_len = len(value)
        if str_len == 0:
            return False

        idx = 0
        if value[0] == '-':
            idx += 1
            if str_len == 1:
                return False

        while idx < str_len and 48 <= ord(value[idx]) <= 57:
            idx += 1
            digits += 1

        if idx >= str_len:
            return digits > 0

        if value[idx] == '.':
            if digits == 0 or idx == str_len - 1:
                return False
            idx += 1
        else:
            return False

        while idx < str_len and 48 <= ord(value[idx]) <= 57:
            idx += 1
            digits += 1

        if idx >= str_len:
            return digits > 0
        return False

    @staticmethod
    def _convert(value: 'DecimalValue') -> str:
        if type(value) is int:
            if value > Decimal.MaxValue:
                return str(Decimal.MaxValue)
            if value < -Decimal.MaxValue:
                return str(-Decimal.MaxValue)
            return str(value)
        if type(value) is float:
            if value > Decimal.MaxValue:
                return str(Decimal.MaxValue)
            if value < -Decimal.MaxValue:
                return str(-Decimal.MaxValue)
            str_value = str(value)
            if len(str_value) > 29:
                return Decimal.round(str_value)
            return str_value
        if type(value) is str:
            if not Decimal.verify(value):
                raise ValueError("Invalid Decimal format")
            if len(value) > 29:
                return Decimal.round(value)
            return value
        if type(value) is bytes:
            str_value = value.decode('utf-8')
            if not Decimal.verify(str_value):
                raise ValueError("Invalid Decimal format")
            if len(str_value) > 29:
                return Decimal.round(value)
            return str_value
        if type(value) is Decimal:
            return value.value
        raise TypeError("Decimal value must be one of int, float, str, bytes, or Decimal")

    def __init__(self, value: 'DecimalValue') -> None:
        self._value = Decimal._convert(value)

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, new_value: 'DecimalValue') -> None:
        self._value = Decimal._convert(new_value)

    def set(self, new_value: 'DecimalValue') -> None:
        self._value = Decimal._convert(new_value)

    def get(self) -> str:
        return self._value

    def type(self) -> PrimitiveType:
        return PrimitiveType.Decimal

    def __bytes__(self) -> bytes:
        len_prefix = struct.pack('b', len(self._value))
        return len_prefix + self._value.encode('utf-8')


class Double(Primitive):
    @staticmethod
    def _convert(new_value: 'Union[float, bytes, Double]') -> float:
        if type(new_value) is float:
            return new_value
        if type(new_value) is Double:
            return new_value.get()
        if type(new_value) is bytes:
            if len(new_value) != 8:
                raise ValueError("Double requires 8 bytes to unpack")
            return struct.unpack("d", new_value)[0]
        raise TypeError("Double must be one of float, bytes, or Double")

    def __init__(self, value: 'Union[float, bytes, Double]') -> None:
        self._value = Double._convert(value)

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, new_value: 'Union[float, bytes, Double]') -> None:
        self._value = Double._convert(new_value)

    def get(self) -> float:
        return self._value

    def set(self, new_value: 'Union[float, bytes, Double]') -> None:
        self._value = Double._convert(new_value)

    def type(self) -> PrimitiveType:
        return PrimitiveType.Double

    def __bytes__(self) -> bytes:
        return struct.pack('d', self._value)


class Int16(Primitive):
    @staticmethod
    def _convert(value: 'Union[int, bytes, Int16]') -> int:
        value_type = type(value)
        if value_type is int:
            if value < -32768:
                value = ~((~value) & 0x7FFF)
            elif value > 32767:
                value = value & 0x7FFF
            return value
        if value_type is bytes:
            if len(value) != 2:
                raise ValueError("Int16 requires 2 bytes to unpack")
            return struct.unpack('h', value)[0]
        if value_type is Int16:
            return value.get()
        raise TypeError("Int16 must be one of int, bytes, Int16")

    def __init__(self, value: 'Union[int, bytes, Int16]') -> None:
        self._value = Int16._convert(value)

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value: 'Union[int, bytes, Int16]') -> None:
        self._value = Int16._convert(value)

    def get(self) -> int:
        return self._value

    def set(self, new_value: 'Union[int, bytes, Int16]') -> None:
        self._value = Int16._convert(new_value)

    def type(self) -> PrimitiveType:
        return PrimitiveType.Int16

    def __bytes__(self) -> bytes:
        return struct.pack('h', self._value)


class Int32(Primitive):
    @staticmethod
    def _convert(value: 'Union[int, bytes, Int32]') -> int:
        value_type = type(value)
        if value_type is int:
            if value > 2147483647:
                value = value & 0x7FFFFFFF
            elif value < -2147483648:
                value = ~((~value) & 0x7FFFFFFF)
            return value
        if value_type is bytes:
            if len(value) != 4:
                raise ValueError("Int32 requires 4 bytes to unpack")
            return struct.unpack('i', value)[0]
        if value_type is Int32:
            return value.get()
        raise TypeError("Int32 must be one of int, bytes, or Int32")

    def __init__(self, value: 'Union[int, bytes, Int32]') -> None:
        self._value = Int32._convert(value)

    @property
    def value(self) -> int:
        return self._value

    @value.setter
    def value(self, value: 'Union[int, bytes, Int32]') -> None:
        self._value = Int32._convert(value)

    def get(self) -> int:
        return self._value

    def set(self, value: 'Union[int, bytes, Int32]') -> None:
        self._value = Int32._convert(value)

    def type(self) -> PrimitiveType:
        return PrimitiveType.Int32

    def __bytes__(self) -> bytes:
        return struct.pack('i', self._value)


class Single(Primitive):
    @staticmethod
    def _convert(new_value: 'Union[float, bytes, Single]') -> float:
        if type(new_value) is float:
            return new_value
        if type(new_value) is Single:
            return new_value.get()
        if type(new_value) is bytes:
            if len(new_value) != 4:
                raise ValueError("Single requires 4 bytes to unpack")
            return struct.unpack("f", new_value)[0]
        raise TypeError("Single must be one of float, bytes, or Single")

    def __init__(self, value: 'Union[float, bytes, Single]') -> None:
        self._value = value

    def get(self) -> float:
        return self._value

    def set(self, new_value: 'Union[float, bytes, Single]') -> None:
        self._value = Single._convert(new_value)

    def type(self) -> PrimitiveType:
        return PrimitiveType.Single

    def __bytes__(self) -> bytes:
        return struct.pack('f', self._value)
