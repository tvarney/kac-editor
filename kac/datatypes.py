
from enum import IntEnum, unique


IDENTIFIER_DEFAULT_VALUE = -1
IDENTIFIER_ARRAY_VALUES = -2

INSTANCE_LIST = []
ARRAY_LIST = []


@unique
class BinaryTypeEnumeration(IntEnum):
    Primitive = 0
    String = 1
    Object = 2
    SystemClass = 3
    Class = 4
    ObjectArray = 5
    StringArray = 6
    PrimitiveArray = 7


@unique
class PrimitiveTypeEnumeration(IntEnum):
    Boolean = 1
    Byte = 2
    Char = 3
    # No value for 4
    Decimal = 5
    Double = 6
    Int16 = 7
    Int32 = 8
    Int64 = 9
    SByte = 10
    Single = 11
    TimeSpan = 12
    DateTime = 13
    UInt16 = 14
    UInt32 = 15
    UInt64 = 16
    Null = 17
    String = 18


@unique
class RecordTypeEnumeration(IntEnum):
    SerializedStreamHeader = 0
    ClassWithId = 1
    SystemClassWithMembers = 2
    ClassWithMembers = 3
    SystemClassWithMembersAndTypes = 4
    ClassWithMembersAndTypes = 5
    BinaryObjectString = 6
    BinaryArray = 7
    MemberPrimitiveTyped = 8
    MemberReference = 9
    ObjectNull = 10
    MessageEnd = 11
    BinaryLibrary = 12
    ObjectNullMultiple256 = 13
    ObjectNullMultiple = 14
    ArraySinglePrimitive = 15
    ArraySingleObject = 16
    ArraySingleString = 17
    MethodCall = 21
    MethodReturn = 22


@unique
class BinaryArrayTypeEnumeration(IntEnum):
    Single = 0
    Jagged = 1
    Rectangular = 2
    SingleOffset = 3
    JaggedOffset = 4
    RectangularOffset = 5


class MemberReference(object):
    def __init__(self, id_ref):
        self.idRef = id_ref

    def resolve(self):
        for element in INSTANCE_LIST + ARRAY_LIST:
            if element.objectId == self.idRef:
                return element


class BinaryLibrary(object):
    def __init__(self, library_id, library_name):
        self.libraryId = library_id
        self.libraryName = library_name


class ClassTypeInfo(object):
    def __init__(self, type_name, library_id):
        self.typeName = type_name
        self.libraryId = library_id

    def __repr__(self):
        return self.typeName + " : " + str(self.libraryId)


class ClassInfo(object):
    def __init__(self, object_id, name, member_count, member_names):
        self.object_id = object_id
        self.name = name
        self.member_count = member_count
        self.member_names = member_names

    def __repr__(self):
        members = ",".join(self.member_names)
        return "{} {},member count:{} {}".format(self.object_id, self.name, self.member_count, members)


class ClassWithMembersAndTypes:
    def __init__(self, class_info, member_type_info):
        self.class_info = class_info
        self.member_type_info = member_type_info
        self.default_values = None
        self.instances = []
        self.instances.append(ObjectInstance(IDENTIFIER_DEFAULT_VALUE, self.class_info.object_id))
        self.instances[0].class_base = self

    def register_instance(self, instance: 'ObjectInstance'):
        instance.class_base = self
        self.instances.append(instance)

    def get_instance(self, index):
        instance = self.instances[index]
        if len(instance.values) != len(self.class_info.memberNames):
            # TODO: Maybe make this an exception?
            print("ERR: Not enough data !")

        for i in range(0, len(self.class_info.memberNames)):
            value = instance.values[i]
            if type(value) is MemberReference:
                value = value.resolve()

            print(self.class_info.memberNames[i], "=>", value)

        return instance


class ObjectInstance:
    def __init__(self, object_id: int, class_base_id):
        INSTANCE_LIST.append(self)
        self.object_id = object_id
        self.class_base = None
        self.class_base_id = class_base_id
        self.values = {}
        self.addresses = []

    def __repr__(self):
        return "<instance of=" + self.class_base.class_info.name + ">"

    def __getitem__(self, item):
        return self.values[item]

    def add_value(self, value, address=None):
        self.values[self.class_base.class_info.member_names[len(self.values)]] = value
        self.addresses.append(address)


class ArrayInstance(ObjectInstance):
    def __init__(self, array_info: 'ArrayInfo', primitive_type: 'PrimitiveTypeEnumeration'):
        ObjectInstance.__init__(self, array_info.object_id, primitive_type)
        ARRAY_LIST.append(self)
        self.array_info = array_info
        self.primitive_type = primitive_type
        self.values = []
        self.addresses = []

    def __repr__(self):
        return "<array, size=" + str(self.array_info.length) + ", type=" + str(self.primitive_type) + ">"

    def add_value(self, value, address=None):
        self.values.append(value)
        self.addresses.append(address)


class IdentifiableObject:
    def __init__(self, object_id, extra_data=None):
        self.object_id = object_id
        self.extra_data = extra_data


class ArrayInfo:
    def __init__(self, object_id, length):
        self.object_id = object_id
        self.length = length

    def __repr__(self):
        return str(self.object_id) + " " + str(self.length)


class BinaryObjectString:
    def __init__(self, object_id, value):
        self.object_id = object_id
        self.value = value

    def __repr__(self):
        return "<string, id=" + str(self.object_id) + ", val=\"" + self.value + "\">"
