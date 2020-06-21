from typing import Iterable

from loader_common import unpack_longlong, unpack_long, unpack_str, unpack_bool, unpack_float


class dogmaAttribute:
    def __init__(self):
        self.description = None
        self.name = None
        self.tooltipDescriptionID = None
        self.maxAttributeID = None
        self.dataType = None
        self.iconID = None
        self.defaultValue = None
        self.attributeID = None
        self.unitID = None
        self.chargeRechargeTimeID = None
        self.tooltipTitleID = None
        self.categoryID = None
        self.displayNameID = None
        self.highIsGood = None
        self.published = None
        self.stackable = None
        self._available_keys = []

    def __getattr__(self, item):
        if not isinstance(item, str):
            raise AttributeError("Attribute is not a string")
        raise AttributeError("Attribute '%s' does not exist on this instance" % item)

    def __dir__(self) -> Iterable[str]:
        return list(filter(lambda x: x.startswith("__"), super(dogmaAttribute, self).__dir__())) + self._available_keys


def load(filename):
    data = open(filename, "rb").read()

    if data[0:4] != bytes.fromhex("7C5EF0B6"):
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
    size = 0x50

    parts = unpack_longlong(data, 0x28)

    starts = []
    for i in range(parts):
        starts.append(unpack_longlong(data, 0x30 + i * 0x8) + 0x10)

    attributes = dict()

    def load_keys(flags):
        res = []
        if flags & 0x4:
            res.append("description")
        res.append("name")
        if flags & 0x1:
            res.append("tooltipDescriptionID")
        if flags & 0x2:
            res.append("maxAttributeID")
        res.append("dataType")
        if flags & 0x8:
            res.append("iconID")
        res.append("defaultValue")
        res.append("attributeID")
        if flags & 0x10:
            res.append("unitID")
        if flags & 0x20:
            res.append("chargeRechargeTimeID")
        if flags & 0x40:
            res.append("tooltipTitleID")
        if flags & 0x80:
            res.append("categoryID")
        if flags & 0x100:
            res.append("displayNameID")
        res.append("highIsGood")
        res.append("published")
        res.append("stackable")
        return res

    for start in starts:
        count = unpack_longlong(data, start)

        for i in range(count):
            entry = start + i * size + 0x8
            typeID = unpack_longlong(data, entry)
            attr_flags = unpack_longlong(data, entry + 0x48)
            keys = load_keys(attr_flags)
            attribute = dogmaAttribute()
            entry += 0x8
            for key in keys:
                if key == "description":
                    value = unpack_str(data, unpack_longlong(data, entry) + 0x10)
                elif key == "name":
                    value = unpack_str(data, unpack_longlong(data, entry + 0x8) + 0x10)
                elif key == "tooltipDescriptionID":
                    value = unpack_long(data, entry + 0x10)
                elif key == "maxAttributeID":
                    value = unpack_long(data, entry + 0x14)
                elif key == "dataType":
                    value = unpack_long(data, entry + 0x18)
                elif key == "iconID":
                    value = unpack_long(data, entry + 0x1c)
                elif key == "defaultValue":
                    value = unpack_float(data, entry + 0x20)
                elif key == "attributeID":
                    value = unpack_long(data, entry + 0x24)
                elif key == "unitID":
                    value = unpack_long(data, entry + 0x28)
                elif key == "chargeRechargeTimeID":
                    value = unpack_long(data, entry + 0x2c)
                elif key == "tooltipTitleID":
                    value = unpack_long(data, entry + 0x30)
                elif key == "categoryID":
                    value = unpack_long(data, entry + 0x34)
                elif key == "displayNameID":
                    value = unpack_long(data, entry + 0x38)
                elif key == "highIsGood":
                    value = unpack_bool(data, entry + 0x3c)
                elif key == "published":
                    value = unpack_bool(data, entry + 0x3d)
                elif key == "stackable":
                    value = unpack_bool(data, entry + 0x3e)
                else:
                    raise NotImplementedError("BUG: should not reach this line: unknown key '%s'" % key)
                setattr(attribute, key, value)
            attribute._available_keys = keys

            attributes[typeID] = attribute

    return attributes

# load("/staticdata/dogmaattributes.fsdbinary")