from encoder import BitEncoder
from spell.aura import Aura


class Player:

    def __init__(self, id: int, party_id: int):
        if id not in range(16):
            raise ValueError("Player ID must be between 0 and 15")
        if party_id not in range(4):
            raise ValueError("Party ID must be between 0 and 3")

        self._id = id
        self._party_id = party_id
        self._aura = Aura()

    def update(self, elapsed_time: float):
        self._aura.update(elapsed_time)

    def encode_ids(self, encoder: BitEncoder):
        encoder.add_bits(self._id, 4)
        encoder.add_bits(self._party_id, 2)

    @property
    def id(self) -> int:
        return self._id

    @property
    def party_id(self) -> int:
        return self._party_id

    @property
    def aura(self) -> Aura:
        return self._aura
