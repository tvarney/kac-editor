import struct


class MSBoolean(object):
    def __init__(self, value, position):
        self.value = value
        self.position = position

    def __repr__(self):
        return "<boolean pos=" + str(self.position) + ", value=" + str(self.value) + ">"

    def update(self, data_array, value):
        data_array[self.position] = 0 if value is False else 1
        self.value = value


class MSInteger32(object):
    def __init__(self, value, position):
        self.value = value
        self.position = position

    def __repr__(self):
        return "<integer32 pos=" + str(self.position) + ", value=" + str(self.value) + ">"

    def update(self, data_array, value):
        v = struct.pack(">I", value)
        data_array[self.position] = v[0]
        data_array[self.position] = v[1]
        data_array[self.position] = v[2]
        data_array[self.position] = v[3]
        self.value = value
