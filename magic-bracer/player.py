from spell.aura import Aura


class Player:

    def __init__(self, id: int, party_id: int):
        self._id = id
        self._party_id = party_id
        self._aura = Aura()

    @property
    def id(self) -> int:
        return self._id

    @property
    def party_id(self) -> int:
        return self._party_id

    @property
    def aura(self) -> Aura:
        return self._aura

    def update(self, ellapsed_time: float):
        self._aura.update(ellapsed_time)
