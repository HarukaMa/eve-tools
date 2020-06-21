from struct import unpack

def unpack_str(data, offset):
    str_length = unpack("<Q", data[offset:offset + 0x8])[0]
    return data[offset + 0x8:offset + 0x8 + str_length].decode()

def unpack_long(data, offset):
    return unpack("<I", data[offset:offset + 4])[0]

def unpack_longlong(data, offset):
    return unpack("<Q", data[offset:offset + 8])[0]

def unpack_float(data, offset):
    return unpack("<f", data[offset:offset + 4])[0]

def unpack_double(data, offset):
    return unpack("<d", data[offset:offset + 8])[0]

def unpack_bool(data, offset):
    return unpack("<?", data[offset:offset + 1])[0]