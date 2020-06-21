from typing import Iterable

from loader_common import unpack_longlong, unpack_long, unpack_str, unpack_bool


class dogmaEffect:
    def __init__(self):
        self.guid = None
        self.sfxName = None
        self.effectName = None
        self.modifierInfo = None
        self.npcUsageChanceAttributeID = None
        self.displayNameID = None
        self.npcActivationChanceAttributeID = None
        self.iconID = None
        self.effectCategory = None
        self.fittingUsageChanceAttributeID = None
        self.durationAttributeID = None
        self.rangeAttributeID = None
        self.dischargeAttributeID = None
        self.falloffAttributeID = None
        self.descriptionID = None
        self.resistanceAttributeID = None
        self.trackingSpeedAttributeID = None
        self.effectID = None
        self.distribution = None
        self.propulsionChance = None
        self.isOffensive = None
        self.disallowAutoRepeat = None
        self.isAssistance = None
        self.isWarpSafe = None
        self.electronicChance = None
        self.rangeChance = None
        self.published = None
        self._available_keys = []

    def __getattr__(self, item):
        if not isinstance(item, str):
            raise AttributeError("Attribute is not a string")
        raise AttributeError("Attribute '%s' does not exist on this instance" % item)

    def __dir__(self) -> Iterable[str]:
        return list(filter(lambda x: x.startswith("__"), super(dogmaEffect, self).__dir__())) + self._available_keys


def load(filename):
    data = open(filename, "rb").read()

    if data[0:4] != bytes.fromhex("464E5C8D"):
        raise IOError(
            "Unexpected cFSD schema version. Loader schema: 464E5C8D Header schema field: %s" % data[0:4].hex())

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
    size = 0x70

    parts = unpack_longlong(data, 0x28)

    starts = []
    for i in range(parts):
        starts.append(unpack_longlong(data, 0x30 + i * 0x8) + 0x10)

    effects = dict()

    def load_keys(flags):
        res = []
        if flags & 0x20:
            res.append("guid")
        if flags & 0x100:
            res.append("sfxName")
        res.append("effectName")
        if flags & 0x200:
            res.append("modifierInfo")
        if flags & 0x1:
            res.append("npcUsageChanceAttributeID")
        if flags & 0x2:
            res.append("displayNameID")
        if flags & 0x4:
            res.append("npcActivationChanceAttributeID")
        if flags & 0x8:
            res.append("iconID")
        res.append("effectCategory")
        if flags & 0x10:
            res.append("fittingUsageChanceAttributeID")
        if flags & 0x40:
            res.append("durationAttributeID")
        if flags & 0x80:
            res.append("rangeAttributeID")
        if flags & 0x400:
            res.append("dischargeAttributeID")
        if flags & 0x800:
            res.append("falloffAttributeID")
        if flags & 0x1000:
            res.append("descriptionID")
        if flags & 0x2000:
            res.append("resistanceAttributeID")
        if flags & 0x4000:
            res.append("trackingSpeedAttributeID")
        res.append("effectID")
        if flags & 0x8000:
            res.append("distribution")
        res.append("propulsionChance")
        res.append("isOffensive")
        res.append("disallowAutoRepeat")
        res.append("isAssistance")
        res.append("isWarpSafe")
        res.append("electronicChance")
        res.append("rangeChance")
        res.append("published")
        return res

    for start in starts:
        count = unpack_longlong(data, start)

        for i in range(count):
            entry = start + i * size + 0x8
            typeID = unpack_longlong(data, entry)
            eff_flags = unpack_longlong(data, entry + 0x6c)
            keys = load_keys(eff_flags)
            effect = dogmaEffect()
            entry += 0x8
            for key in keys:
                if key == "guid":
                    value = unpack_str(data, unpack_longlong(data, entry) + 0x10)
                elif key == "sfxName":
                    value = unpack_str(data, unpack_longlong(data, entry + 0x8) + 0x10)
                elif key == "effectName":
                    value = unpack_str(data, unpack_longlong(data, entry + 0x10) + 0x10)
                elif key == "modifierInfo":
                    type_start = unpack_longlong(data, entry + 0x18) + 0x10
                    value = "Not Implemented"
                elif key == "npcUsageChanceAttributeID":
                    value = unpack_long(data, entry + 0x20)
                elif key == "displayNameID":
                    value = unpack_long(data, entry + 0x24)
                elif key == "npcActivationChanceAttributeID":
                    value = unpack_long(data, entry + 0x28)
                elif key == "iconID":
                    value = unpack_long(data, entry + 0x2c)
                elif key == "effectCategory":
                    value = unpack_long(data, entry + 0x30)
                elif key == "fittingUsageChanceAttributeID":
                    value = unpack_long(data, entry + 0x34)
                elif key == "durationAttributeID":
                    value = unpack_long(data, entry + 0x38)
                elif key == "rangeAttributeID":
                    value = unpack_long(data, entry + 0x3c)
                elif key == "dischargeAttributeID":
                    value = unpack_long(data, entry + 0x40)
                elif key == "falloffAttributeID":
                    value = unpack_long(data, entry + 0x44)
                elif key == "descriptionID":
                    value = unpack_long(data, entry + 0x48)
                elif key == "resistanceAttributeID":
                    value = unpack_long(data, entry + 0x4c)
                elif key == "trackingSpeedAttributeID":
                    value = unpack_long(data, entry + 0x50)
                elif key == "effectID":
                    value = unpack_long(data, entry + 0x54)
                elif key == "distribution":
                    value = unpack_long(data, entry + 0x58)
                elif key == "propulsionChance":
                    value = unpack_bool(data, entry + 0x5c)
                elif key == "isOffensive":
                    value = unpack_bool(data, entry + 0x5d)
                elif key == "disallowAutoRepeat":
                    value = unpack_bool(data, entry + 0x5e)
                elif key == "isAssistance":
                    value = unpack_bool(data, entry + 0x5f)
                elif key == "isWarpSafe":
                    value = unpack_bool(data, entry + 0x60)
                elif key == "electronicChance":
                    value = unpack_bool(data, entry + 0x61)
                elif key == "rangeChance":
                    value = unpack_bool(data, entry + 0x62)
                elif key == "published":
                    value = unpack_bool(data, entry + 0x63)
                else:
                    raise NotImplementedError("BUG: should not reach this line: unknown key '%s'" % key)
                setattr(effect, key, value)
            effect._available_keys = keys

            effects[typeID] = effect

    return effects

# load("/staticdata/dogmaeffects.fsdbinary")