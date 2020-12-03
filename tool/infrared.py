import array

IR_UNIT = 500
IR_ERROR_MARGIN = IR_UNIT / 2

IR_HEADER_MARK = IR_UNIT * 8
IR_HEADER_SPACE = IR_UNIT * 6

IR_ZERO = IR_UNIT
IR_ONE = IR_UNIT * 3
IR_LEAD_OUT = IR_UNIT * 10

IR_CRC_GENERATOR = 0x1D


class Infrared(object):
    def __init__(self, ir_pulseout):
        self._ir_pulseout = ir_pulseout

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

        crc = self._calculate_crc(data)
        print("CRC: ", bin(crc))
        self._encode_byte(durations, duration_index, crc)

        print("Durations: ", durations)
        self._ir_pulseout.send(durations)
        print("Sent")

    def _encode_byte(self, durations, duration_index, value):
        for i in range(8):
            if (value & 0x80) > 0:
                durations[duration_index] = IR_ONE
            else:
                durations[duration_index] = IR_ZERO
            value <<= 1
            duration_index += 1

    def _calculate_crc(self, data):
        crc = 0
        for data_byte in data:
            crc ^= data_byte
            for j in range(8):
                if crc & 0x80 is not 0:
                    crc = ((crc << 1) & 0xFF) ^ IR_CRC_GENERATOR
                else:
                    crc = (crc << 1) & 0xFF
        return crc
