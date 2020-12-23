from event import SPELL_EVENT


spell_ids = {1: "Light", 2: "Fire", 3: "Water", 4: "Earth", 5: "Wind"}


def id_for_spell(name):
    for spell_id, spell_name in spell_ids.items():
        if spell_name == name:
            return spell_id
    raise RuntimeError("Unknown spell: ", name)


def spell_for_id(spell_id):
    if spell_id not in spell_ids:
        print("Unknown spell ID: ", spell_id)
        return
    spell_name = spell_ids[spell_id]
    return Spell(spell_name)


class Spell(object):
    def __init__(self, name):
        self._name = name
        self._spell_id = id_for_spell(name)
        self._power = 0
        self.lifespan = 10

    @property
    def spell_id(self):
        return self._spell_id

    @property
    def name(self):
        return self._name

    @property
    def power(self):
        return self._power

    @power.setter
    def power(self, power):
        self._power = power
        self.max_power = max(self._power, power)

    def send(self, out, team):
        power_byte = 255 * self.power & 0xFF

        print("Sending event: ", self.name, self.spell_id, power_byte, team)

        data = bytes((SPELL_EVENT, self._spell_id, power_byte, team))
        out.send(data)


def receive_spell(data):
    if len(data) < 4 or data[0] != SPELL_EVENT:
        return None

    spell_id = data[1]
    power = data[2]
    team = data[3]
    spell = spell_for_id(spell_id)
    if spell is None:
        return None

    spell.power = power

    print("Spell received: ", spell.name, spell_id, power, team)
    return spell, team


def select_spell(initial_acceleration, current_acceleration):
    # x = pointing up or down. Up = -1, Down = 1
    # z, y = rotation. Flat = abs(z)=1, y=0. On edge = abs(z)=0,abs(y)=1
    # vert: Up = -1, Down = 1
    # Horz: Flat = 0, Edge = 1, -1
    initial_vert = _map_vert(initial_acceleration)
    initial_horz = _map_horz(initial_acceleration)
    current_vert = _map_vert(current_acceleration)
    current_horz = _map_horz(current_acceleration)

    print(
        "Initial: {} {} -> Current {} {}".format(
            initial_vert, initial_horz, current_vert, current_horz
        )
    )

    if initial_vert == VERT_UP and current_vert == VERT_UP:
        return Spell("Light")

    if (
        initial_vert == VERT_MIDDLE
        and initial_horz == HORZ_FLAT
        and current_vert == VERT_MIDDLE
        and current_horz == HORZ_EDGE
    ):
        return Spell("Fire")

    if (
        initial_vert == VERT_UP
        and current_vert == VERT_MIDDLE
        and current_horz == HORZ_FLAT
    ):
        return Spell("Wind")

    if (
        initial_vert == VERT_DOWN
        and current_vert == VERT_MIDDLE
        and current_horz == HORZ_FLAT
    ):
        return Spell("Water")

    if (
        initial_vert == VERT_DOWN
        and current_vert == VERT_MIDDLE
        and current_horz == HORZ_EDGE
    ):
        return Spell("Earth")

    return None


VERT_DOWN = 1
VERT_LOW = 2
VERT_MIDDLE = 3
VERT_HIGH = 4
VERT_UP = 5


def _map_vert(acceleration):
    x = acceleration[0]
    if x > 0.75:
        return VERT_DOWN
    if x > 0.25:
        return VERT_LOW
    if x > -0.25:
        return VERT_MIDDLE
    if x > -0.75:
        return VERT_HIGH
    return VERT_UP


HORZ_FLAT = 1
HORZ_ANGLE = 2
HORZ_EDGE = 3


def _map_horz(acceleration):
    y = abs(acceleration[1])
    if y < 0.35:
        return HORZ_FLAT
    if y < 0.65:
        return HORZ_ANGLE
    return HORZ_EDGE
