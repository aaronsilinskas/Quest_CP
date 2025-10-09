from encoder import PLAYER_PARTY_ID_BITS
from spell.aura import Aura


class Player:

    def __init__(self, id: int, party_id: int):
        # party_id must be in range of PLAYER_PARTY_ID_BITS
        party_id_max = 2**PLAYER_PARTY_ID_BITS
        if party_id not in range(party_id_max):
            raise ValueError(f"Party ID must be between 0 and {party_id_max - 1}")

        self._id = id
        self._party_id = party_id
        self._aura = Aura()

    def update(self, elapsed_time: float):
        self._aura.update(elapsed_time)

    @property
    def id(self) -> int:
        return self._id

    @property
    def party_id(self) -> int:
        return self._party_id

    @property
    def aura(self) -> Aura:
        return self._aura
