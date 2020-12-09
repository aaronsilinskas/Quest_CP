import array

IR_UNIT = 500
IR_ERROR_MARGIN = IR_UNIT / 2

IR_HEADER_MARK = IR_UNIT * 8
IR_HEADER_SPACE = IR_UNIT * 6

IR_ZERO = IR_UNIT
IR_ONE = IR_UNIT * 3
IR_LEAD_OUT = IR_UNIT * 10

IR_CRC_GENERATOR = 0x1D


def _calculate_crc(data):
    crc = 0
    for data_byte in data:
        crc ^= data_byte
        for j in range(8):
            if crc & 0x80 is not 0:
                crc = ((crc << 1) & 0xFF) ^ IR_CRC_GENERATOR
            else:
                crc = (crc << 1) & 0xFF
    return crc


class Infrared(object):
    def __init__(self, ir_pulseout, ir_pulsein):
        self._ir_pulseout = ir_pulseout
        self._ir_pulsein = ir_pulsein
        self._decoder = IRDecoder()

    def send(self, data):
        print("Sending: ", data)
        # length = header + (data * 8 bits per byte) + crc bits + lead out
        durations = array.array("H", [0] * (2 + len(data) * 8 + 8 + 1))
        durations[0] = IR_HEADER_MARK
        durations[1] = IR_HEADER_SPACE
        durations[-1] = IR_LEAD_OUT

        duration_index = 2
        for data_byte in data:
            self._encode_byte(durations, duration_index, data_byte)
            duration_index += 8

        crc = _calculate_crc(data)
        print("CRC: ", bin(crc))
        self._encode_byte(durations, duration_index, crc)

        print("Durations: ", durations)
        self._ir_pulseout.send(durations)
        print("Sent")

    def receive(self):
        if len(self._ir_pulsein) is 0:
            return

        while len(self._ir_pulsein) > 0:
            packet = self._decoder.decode(self._ir_pulsein.popleft())
            if packet is not None:
                return packet

    def _encode_byte(self, durations, duration_index, value):
        for i in range(8):
            if (value & 0x80) > 0:
                durations[duration_index] = IR_ONE
            else:
                durations[duration_index] = IR_ZERO
            value <<= 1
            duration_index += 1


class IRDecoder(object):
    def __init__(self):
        self._received_headers = 0
        self._received_data = bytearray()

    def decode(self, pulse):
        # print("Pulse: ", pulse)

        # discard pulses until we get the first header pulse
        if self._received_headers is 0:
            if self._check_pulse(pulse, IR_HEADER_MARK):
                self._received_headers = 1
        elif self._received_headers is 1:
            if self._check_pulse(pulse, IR_HEADER_SPACE):
                self._received_headers = 2
                self._received_data = bytearray()
                self._reset_bits()
            else:
                self._received_headers = 0
        elif self._received_headers is 2:
            if self._check_pulse(pulse, IR_ONE):
                self._write_bit(1)
            elif self._check_pulse(pulse, IR_ZERO):
                self._write_bit(0)
            elif self._check_pulse(pulse, IR_LEAD_OUT):
                self._received_headers = 0
                received_crc = self._received_data[-1]
                received_data = self._received_data[:len(self._received_data)-1]
                calculated_crc = _calculate_crc(received_data)
                self._received_data = bytearray()
                if received_crc is calculated_crc:
                    return received_data
                else:
                    print("CRC mismatch: ", bin(received_crc), bin(calculated_crc))
            else:
                # unknown pulse, packet is corrupt so reset
                self._received_headers = 0

    def _reset_bits(self):
        self._received_byte = 0
        self._received_bit_index = 7

    def _check_pulse(self, received, expected):
        return abs(received - expected) < IR_ERROR_MARGIN

    def _write_bit(self, bit):
        if bit is 1:
            self._received_byte |= 1 << self._received_bit_index
        self._received_bit_index -= 1
        if self._received_bit_index < 0:
            # print("Received Byte: ", bin(self._received_byte))
            self._received_data.append(self._received_byte)
            self._reset_bits()
        # print("Bit Update: ", bin(self._received_byte), self._received_bit_index)
