EVENT_BITS = 3
EVENT_SPELL = 0x01
PLAYER_PARTY_ID_BITS = 2  # Number of bits to represent party ID (0-3)


class BitEncoder:
    def __init__(self):
        self.bits = 0
        self.length = 0

    def write_bits(self, value: int, length: int):
        # raise error if value cannot be represented in length bits
        maxValue = (1 << length) - 1
        if value < 0 or value > maxValue:
            raise ValueError(f"Value {value} cannot be represented with {length} bits")

        shifted_value = value << self.length
        self.bits |= shifted_value
        self.length += length

    def write_event(self, event: int, party_id: int = 0):
        self.write_bits(event, EVENT_BITS)
        self.write_bits(party_id, PLAYER_PARTY_ID_BITS)

    def to_bytes(self) -> bytearray:
        encoded_bytes = self.bits.to_bytes((self.length + 7) // 8, "big")
        # strip leading zero bytes
        return encoded_bytes.lstrip(b"\x00")


class BitDecoder:
    def __init__(self, data: bytearray):
        self.bits = int.from_bytes(data, "big")
        self.length = len(data) * 8

    def read_bits(self, length: int) -> int:
        mask = (1 << length) - 1
        value = self.bits & mask
        self.bits >>= length
        return value

    def read_event(self) -> tuple[int, int]:
        event = self.read_bits(EVENT_BITS)
        party_id = self.read_bits(PLAYER_PARTY_ID_BITS)
        return event, party_id
