from typing import List

from loader_common import unpack_longlong, unpack_double, unpack_long


class Dogma:

    def __init__(self, attributes, effects):
        self.dogmaAttributes: List[DogmaAttribute] = attributes
        self.dogmaEffects: List[DogmaEffect] = effects

    def __repr__(self):
        return "Dogma"

class DogmaAttribute:

    def __init__(self, attributeID, value):
        self.attributeID = attributeID
        self.value = value

    def __repr__(self):
        return "DogmaAttribute ID: %s value: %s" % (self.attributeID, self.value)


class DogmaEffect:

    def __init__(self, effectID, isDefault):
        self.effectID = effectID
        self.isDefault = isDefault

    def __repr__(self):
        return "DogmaEffect ID: %s isDefault: %s" % (self.effectID, "True" if self.isDefault else "False")

def load(filename):
    data = open(filename, "rb").read()

    if data[0:4] != bytes.fromhex("6783D76B"):
        raise IOError(
            "Unexpected cFSD schema version. Loader schema: 6783D76B Header schema field: %s" % data[0:4].hex())

    size = len(data)

    checksum = 37
    for i in range(size - 24):
        checksum = ((checksum * 54059) ^ (data[i + 24] * 76963)) & 0xFFFF_FFFF_FFFF_FFFF
    if checksum.to_bytes(8, "little") != data[8:16]:
        raise IOError(
            "Unexpected cFSD hash. Header hash field: 0x%s Data hash: 0x%s Header length field: %d Data length: %d" % (
                data[8:16].hex().upper(), checksum.to_bytes(8, "little").hex().upper(), unpack_longlong(data, 16),
                size - 24
            ))

    total_count = unpack_longlong(data, 0x20)
    size = unpack_longlong(data, 0x18)

    parts = unpack_longlong(data, 0x28)

    starts = []
    for i in range(parts):
        starts.append(unpack_longlong(data, 0x30 + i * 0x8) + 0x10)

    dogma = dict()
    for start in starts:
        count = unpack_longlong(data, start)

        for i in range(count):
            entry = start + i * size + 0x8
            typeID = unpack_longlong(data, entry)
            attr_start = unpack_longlong(data, entry + 0x8) + 0x10
            eff_start = unpack_longlong(data, entry + 0x10) + 0x10
            attribute_count = unpack_longlong(data, attr_start)
            attributes = []
            for j in range(attribute_count):
                entry = attr_start + 0x8 + j * 0x10
                value = unpack_double(data, entry)
                attributeID = unpack_longlong(data, entry + 0x8)
                attributes.append(DogmaAttribute(attributeID, value))

            effect_count = unpack_longlong(data, eff_start)
            effects = []
            for j in range(effect_count):
                entry = eff_start + 0x8 + j * 0x8
                effectID = unpack_long(data, entry)
                isDefault = bool(unpack_long(data, entry + 0x4))
                effects.append(DogmaEffect(effectID, isDefault))

            dogma[typeID] = Dogma(attributes, effects)
    return dogma

# load("/staticdata/typedogma.fsdbinary")