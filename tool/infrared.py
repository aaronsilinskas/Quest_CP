import adafruit_irremote


class Infrared(object):
    def __init__(self, transmit_pulseout):
        self._transmit_pulseout = transmit_pulseout
        self._encoder = adafruit_irremote.GenericTransmit(
            header=[9500, 4500], one=[550, 550], zero=[550, 1700], trail=0
        )
