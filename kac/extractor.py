import time

from kac.datatypes import *
from kac.vartypes import *

import typing
if typing.TYPE_CHECKING:
    from typing import Optional


BinaryLibraryRecord = []
MemberReferencesList = []
objectIds = []
typeStats = [0] * 22
parentlessObjects = {}


def register_object_id(object_id: IdentifiableObject):
    objectIds.append(object_id)


def get_object_from_id(object_id) -> 'Optional[IdentifiableObject]':
    for obj in objectIds:
        if obj.object_id == object_id:
            return obj


def get_boolean(file):
    return MSBoolean(position=file.tell(), value=file.read(1) == b'\x01')


def get_byte(file):
    return file.read(1)


def get_char(file):
    return file.read(1).decode('utf-8')


def get_decimal(file):
    raise NotImplementedError("get_decimal")


def get_double(file):
    raise NotImplementedError("get_double")


def get_int(file, size: int=1):
    return int.from_bytes(file.read(size), "little")


def get_typed_int32(file):
    position = file.tell()
    val = get_int(file, 4)
    return MSInteger32(val, position)


def get_signed_byte(file):
    raise NotImplementedError("get_signed_byte")


def get_single(file):
    a1 = file.read(1)
    a2 = file.read(1)
    a3 = file.read(1)
    a4 = file.read(1)
    val = struct.unpack('f', a1 + a2 + a3 + a4)
    return val


def get_time_span(file):
    raise NotImplementedError("get_time_span")


def get_date_time(file):
    raise NotImplementedError("get_date_time")


def get_unsigned_int(file, size: int=1) -> int:
    if size == 1:
        return struct.unpack("<B", file.read(1))[0]
    if size == 2:
        return struct.unpack("<H", file.read(2))[0]
    if size == 4:
        return struct.unpack("<I", file.read(4))[0]
    if size == 8:
        return struct.unpack("<Q", file.read(8))[0]
    raise ValueError("Invalid unsigned int size {}: must be one of 1, 2, 4, or 8".format(size))


def get_null(file):
    raise RuntimeError("get_null should not be called")


def get_string(file):
    return get_length_prefixed_string(file)


def get_length_prefixed_string(file, extend: bool=False):
    length = int.from_bytes(file.read(1), "little")

    is_longer = (length >> 7) & 1
    if is_longer == 1:
        old_length = length & 0b01111111
        length_2 = int.from_bytes(file.read(1), "little")
        length_2 = length_2 & 0b01111111
        length = (length_2 << 7) + old_length

    string = file.read(length).decode('utf-8')
    return string


def get_object(file):
    raise NotImplementedError("get_object")


def get_system_class(file):
    raise NotImplementedError("get_system_class")


def get_class(file):
    raise NotImplementedError("get_class")


def get_object_array(file):
    raise NotImplementedError("get_object_array")


def get_string_array(file):
    raise NotImplementedError("get_string_array")


def get_primitive_array(file):
    raise NotImplementedError("get_primitive_array")


def get_values(file, member_type_info_list, instance: ObjectInstance):
    for i in range(0, len(member_type_info_list[0])):
        member_type_info = member_type_info_list[0][i]
        additional_info = member_type_info_list[1][i]

        if member_type_info == BinaryType.Primitive:
            if additional_info == PrimitiveType.Boolean:
                instance.add_value(get_boolean(file))
            elif additional_info == PrimitiveType.Byte:
                instance.add_value(get_byte(file))
            elif additional_info == PrimitiveType.Char:
                instance.add_value(get_char(file))
            elif additional_info == PrimitiveType.Decimal:
                instance.add_value(get_decimal(file))
            elif additional_info == PrimitiveType.Double:
                instance.add_value(get_double(file))
            elif additional_info == PrimitiveType.Int16:
                instance.add_value(get_int(file, 2))
            elif additional_info == PrimitiveType.Int32:
                instance.add_value(get_typed_int32(file))
            elif additional_info == PrimitiveType.Int64:
                instance.add_value(get_int(file, 8))
            elif additional_info == PrimitiveType.SByte:
                instance.add_value(get_signed_byte(file))
            elif additional_info == PrimitiveType.Single:
                instance.add_value(get_single(file))
            elif additional_info == PrimitiveType.TimeSpan:
                instance.add_value(get_time_span(file))
            elif additional_info == PrimitiveType.DateTime:
                instance.add_value(get_date_time(file))
            elif additional_info == PrimitiveType.UInt16:
                instance.add_value(get_unsigned_int(file, 2))
            elif additional_info == PrimitiveType.UInt32:
                instance.add_value(get_unsigned_int(file, 4))
            elif additional_info == PrimitiveType.UInt64:
                instance.add_value(get_unsigned_int(file, 8))
            elif additional_info == PrimitiveType.Null:
                instance.add_value(get_null(file))
            elif additional_info == PrimitiveType.String:
                instance.add_value(get_string(file))
            else:
                raise RuntimeError("Unknown primitive type {}".format(additional_info))
        elif member_type_info == BinaryType.String:
            instance.add_value(read_record_type_enum(file))
        elif member_type_info == BinaryType.Object:
            instance.add_value(read_record_type_enum(file))
        elif member_type_info == BinaryType.SystemClass:
            instance.add_value(read_record_type_enum(file))
        elif member_type_info == BinaryType.Class:
            instance.add_value(read_record_type_enum(file))
        elif member_type_info == BinaryType.ObjectArray:
            instance.add_value(read_record_type_enum(file))
        elif member_type_info == BinaryType.StringArray:
            instance.add_value(read_record_type_enum(file))
        elif member_type_info == BinaryType.PrimitiveArray:
            instance.add_value(read_record_type_enum(file))
        else:
            raise RuntimeError("member_type_info {} is invalid".format(member_type_info))


def get_array_info(file):
    object_id = get_int(file, 4)
    length = get_int(file, 4)

    return ArrayInfo(object_id, length)


def get_class_info(file, extend: bool=False):
    object_id = get_int(file, 4)
    name = get_length_prefixed_string(file, True)
    member_count = get_int(file, 4)
    member_names = []
    for i in range(0, member_count):
        val = get_length_prefixed_string(file)
        member_names.append(val)

    return ClassInfo(object_id, name, member_count, member_names)


def get_system_class_type_info(file):
    type_name = get_string(file)
    print("get_system_class_type_info() -> Read {}".format(type_name))


def get_class_type_info(file):
    type_name = get_length_prefixed_string(file)
    library_id = get_int(file, 4)
    is_valid_library_id = False
    for binaryLibrary in BinaryLibraryRecord:
        if binaryLibrary.libraryId == library_id:
            is_valid_library_id = True
            break
    if not is_valid_library_id:
        raise RuntimeError("Class {} does not have a valid library_id ({})".format(type_name, library_id))

    return ClassTypeInfo(type_name, library_id)


def get_member_type_info(file, class_info):
    binary_types = list()

    for i in range(0, class_info.member_count):
        binary_types.append(get_int(file))

    additional_info = list()
    for bin_type in binary_types:
        if bin_type == 0 or bin_type == 7:
            additional_info.append(get_int(file))
        elif bin_type == 1 or bin_type == 2 or bin_type == 5 or bin_type == 6:
            additional_info.append(None)
        elif bin_type == 3:
            additional_info.append(get_system_class_type_info(file))
        elif bin_type == 4:
            additional_info.append(get_class_type_info(file))

    return binary_types, additional_info


def read_serialized_stream_header(file):
    # Type value 0
    root_id = get_int(file, 4)
    header_id = get_int(file, 4)
    major_version = get_int(file, 4)
    minor_version = get_int(file, 4)

    print("==== LOADING ====")
    print("=> RootId: {}; HeaderId: {}; Version {}.{}".format(root_id, header_id, major_version, minor_version))
    print("=> HEADER VERIFICATION SUCCESS")


def get_class_with_id(file):
    # Type value 1
    object_id = get_int(file, 4)
    metadata_id = get_int(file, 4)
    update_object = get_object_from_id(metadata_id)
    if update_object is None:
        print("ERR: unable to find object to update")

    # TODO: Check if making the above an exception breaks anything

    new_instance = ObjectInstance(object_id, metadata_id)
    update_object.extra_data.register_instance(new_instance)
    get_values(file, update_object.extra_data.member_type_info, new_instance)

    return new_instance


def read_system_class_with_members(file):
    # Type value 2
    pos = file.tell()
    class_info = get_class_info(file, True)
    print("read_system_class_with_members() -> Read {} at {}".format(class_info, pos))


def get_class_with_members_and_types(file):
    # Type value 5
    class_info = get_class_info(file)
    member_type_info = get_member_type_info(file, class_info)
    _ = get_int(file, 4)  # library_id
    class_object = ClassWithMembersAndTypes(class_info, member_type_info)
    get_values(file, member_type_info, class_object.instances[0])
    register_object_id(IdentifiableObject(class_info.object_id, class_object))
    return class_object.instances[0]


def get_system_class_with_members_and_types(file):
    # Type value 4
    class_info = get_class_info(file)
    member_type_info = get_member_type_info(file, class_info)
    class_object = ClassWithMembersAndTypes(class_info, member_type_info)
    _ = get_values(file, member_type_info, class_object.instances[0])  # values
    register_object_id(IdentifiableObject(class_info.object_id, class_object))
    return class_object.instances[0]


def read_binary_object_string(file):
    # Type value 6
    object_id = get_int(file, 4)
    value = get_length_prefixed_string(file)
    return BinaryObjectString(object_id, value)


def read_binary_array(file):
    # Type value 7
    _ = get_int(file, 4)  # object_id
    binary_type_enum = get_int(file)
    rank = get_int(file, 4)
    lengths = list()
    for i in range(0, rank):
        lengths.append(get_int(file, 4))

    if binary_type_enum in [BinaryArrayType.SingleOffset, BinaryArrayType.JaggedOffset,
                            BinaryArrayType.RectangularOffset]:
        lower_bounds = []
        for i in range(0, rank):
            lower_bounds.append(get_int(file, 4))

    type_enum = get_int(file)
    if type_enum == 0 or type_enum == 7:
        get_int(file)
    elif type_enum == 1 or type_enum == 2 or type_enum == 5 or type_enum == 6:
        pass
    elif type_enum == 3:
        get_system_class_type_info(file)
    elif type_enum == 4:
        get_class_type_info(file)


def get_member_reference(file):
    # Type value 9
    id_ref = get_int(file, 4)
    return MemberReference(id_ref)


def read_binary_library(file):
    # Type value 12
    library_id = get_int(file, 4)
    library_name = get_length_prefixed_string(file)

    BinaryLibraryRecord.append(BinaryLibrary(library_id, library_name))


def read_object_null_multiple_256(file):
    # Type value 14
    null_count = get_int(file)
    print("read_object_null_multiple_256() -> Read {}".format(null_count))


def read_object_null_multiple(file):
    # Type value 14
    null_count = get_int(file, 4)
    print("read_object_null_multiple() -> Read {}".format(null_count))


def read_array_single_primitive(file):
    # Type value 15
    array_info = get_array_info(file)
    primitive_type_enum = get_int(file, 1)

    values = ArrayInstance(array_info, PrimitiveType(primitive_type_enum))

    for i in range(0, array_info.length):
        get_values(file, ([BinaryType.Primitive], [primitive_type_enum]), values)
    return


def read_array_single_object(file):
    # Type value 16
    array_info = get_array_info(file)
    print("read_array_single_object() -> Read {}".format(array_info))


def read_array_single_string(file):
    # Type value 16
    array_info = get_array_info(file)
    print("read_array_single_string() -> Read {}".format(array_info))


def read_record_type_enum(file, top_level: bool=False):
    global parentlessObjects

    bin_type = get_int(file)
    typeStats[bin_type] += 1

    if bin_type == RecordType.SerializedStreamHeader:
        return False

    if bin_type == RecordType.ClassWithId:
        return get_class_with_id(file)
    elif bin_type == RecordType.SystemClassWithMembersAndTypes:
        return get_system_class_with_members_and_types(file)
    elif bin_type == RecordType.SystemClassWithMembers:
        return read_system_class_with_members(file)
    elif bin_type == RecordType.ClassWithMembersAndTypes:
        val = get_class_with_members_and_types(file)
        if top_level:
            parentlessObjects[val.class_base.class_info.name] = val
        return val
    elif bin_type == RecordType.BinaryObjectString:
        return read_binary_object_string(file)
    elif bin_type == RecordType.BinaryArray:
        return read_binary_array(file)
    elif bin_type == RecordType.MemberReference:
        return get_member_reference(file)
    elif bin_type == RecordType.ObjectNull:
        pass
    elif bin_type == RecordType.BinaryLibrary:
        return read_binary_library(file)
    elif bin_type == RecordType.ObjectNullMultiple256:
        return read_object_null_multiple_256(file)
    elif bin_type == RecordType.ObjectNullMultiple:
        return read_object_null_multiple(file)
    elif bin_type == RecordType.ArraySinglePrimitive:
        return read_array_single_primitive(file)
    elif bin_type == RecordType.ArraySingleObject:
        return read_array_single_object(file)
    elif bin_type == RecordType.ArraySingleString:
        return read_array_single_string(file)
    elif bin_type == RecordType.MessageEnd:
        return False
    else:
        raise ValueError("Unknown Binary Type {} at {}".format(bin_type, file.tell()))


def dump_class(target, level: int=1):
    target_class = target.classBase
    print("="*level + ">DUMPING", target_class.classInfo.name, "WITH", len(target_class.instances), "ELEMENTS")

    print("="*level + "> VALUES")
    print("="*level + str(target_class.classInfo.memberNames))


def parse_save_file(filename):
    with open(filename, mode='rb') as inspected_file:

        data_array = bytearray(inspected_file.read())
        inspected_file.seek(0)

        start_time = time.time()
        # Read file header
        header_check = get_int(inspected_file)
        # The SerializedStreamHeader must be the first record
        assert(header_check == 0)
        read_serialized_stream_header(inspected_file)

        while read_record_type_enum(inspected_file, True) is not False:
            continue
        print("==== FINISHED ====")
        print("=> Loading took ", time.time() - start_time, "seconds")

    return parentlessObjects, data_array


def write_save_file(output_file_name, data_array):
    with open(output_file_name, mode="wb+") as new_file:
            new_file.write(data_array)
