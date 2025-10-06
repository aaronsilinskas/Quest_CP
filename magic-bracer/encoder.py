EVENT_BITS = 3
EVENT_SPELL = 0x01

class BitEncoder:
    def __init__(self):
        self.bits = 0
        self.length = 0

    def add_bits(self, value: int, length: int):
        print("Adding bits: ", bin(value), length)
        
        # raise error if value cannot be represented in length bits
        maxValue = (1 << length) - 1
        if value < 0 or value > maxValue:
            raise ValueError(f"Value {value} cannot be represented with {length} bits")

        self.bits = (self.bits << length) | (value & ((1 << length) - 1))
        print("Current bits: ", bin(self.bits))
        self.length += length
        
    def add_event(self, event: int):
        self.add_bits(event, EVENT_BITS)

    def to_bytes(self) -> bytearray:
        byte_length = (self.length + 7) // 8
        encoding = self.bits.to_bytes(byte_length, "big")
        # remove trailing zero bytes, decoder will assume all zeroes at the end
        encoding = encoding.rstrip(b'\x00')        
        return encoding
