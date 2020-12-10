SPELL_EVENT = 1

SPELL_IDS = {"Light": 1, "Fire": 2, "Water": 3, "Earth": 4, "Wind": 5}


class Events(object):
    def __init__(self, out):
        self._out = out

    def send_spell(self, name, power, team=1):
        spell_id = SPELL_IDS[name]
        power_byte = 255 * power & 0xFF

        print("Sending event: ", name, spell_id, power_byte, team)

        data = [SPELL_EVENT, spell_id, power_byte, team]
        self._out.send(data)
