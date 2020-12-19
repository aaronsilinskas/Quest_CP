from event import SPELL_EVENT

spell_classes = {}


def spell_for_id(spell_id):
    class_name = spell_classes[spell_id]
    klass = globals()[class_name]
    return klass()


class Spell(object):
    def __init__(self, spell_id):
        self._spell_id = spell_id
        class_name = type(self).__name__
        self._name = class_name[: -len("Spell")]
        self._power = 0
        self.lifespan = 10
        spell_classes[spell_id] = class_name

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


class LightSpell(Spell):
    def __init__(self):
        Spell.__init__(self, 1)


class FireSpell(Spell):
    def __init__(self):
        Spell.__init__(self, 2)


class WaterSpell(Spell):
    def __init__(self):
        Spell.__init__(self, 3)


class EarthSpell(Spell):
    def __init__(self):
        Spell.__init__(self, 4)


class WindSpell(Spell):
    def __init__(self):
        Spell.__init__(self, 5)


def receive_spell(data, player):
    if len(data) < 4 or data[0] != SPELL_EVENT:
        return False

    spell_id = data[1]
    power = data[2]
    team = data[3]
    spell = spell_for_id(spell_id)
    spell.power = power

    print("Spell received: ", spell.name, spell_id, power, team)
    player.hit_by_spell(spell, team)
    return True


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
        return LightSpell()

    if (
        initial_vert == VERT_MIDDLE
        and initial_horz == HORZ_FLAT
        and current_vert == VERT_MIDDLE
        and current_horz == HORZ_EDGE
    ):
        return FireSpell()

    if (
        initial_vert == VERT_UP
        and current_vert == VERT_MIDDLE
        and current_horz == HORZ_FLAT
    ):
        return WindSpell()

    if (
        initial_vert == VERT_DOWN
        and current_vert == VERT_MIDDLE
        and current_horz == HORZ_FLAT
    ):
        return WaterSpell()

    if (
        initial_vert == VERT_DOWN
        and current_vert == VERT_MIDDLE
        and current_horz == HORZ_EDGE
    ):
        return EarthSpell()

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
