import array


class Infrared(object):
    def __init__(self, ir_pulseout):
        self.header = [9500, 4500]
        self.one = [550, 550]
        self.zero = [550, 1700]
        self.trail = 4500
        self._ir_pulseout = ir_pulseout

    def send(self, data):
        print("Sending: ", data)
        durations = array.array("H", [0] * (2 + len(data) * 8 * 2 + 1))
        durations[0] = self.header[0]
        durations[1] = self.header[1]
        durations[-1] = self.trail

        out = 2
        for byte_index, _ in enumerate(data):
            for i in range(7, -1, -1):
                if (data[byte_index] & 1 << i) > 0:
                    durations[out] = self.one[0]
                    durations[out + 1] = self.one[1]
                else:
                    durations[out] = self.zero[0]
                    durations[out + 1] = self.zero[1]
                out += 2

        print("Durations: ", durations)
        self._ir_pulseout.send(durations)
        print("Sent")
