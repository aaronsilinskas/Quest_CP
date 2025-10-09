# SPDX-FileCopyrightText: Copyright (c) 2025 Aaron Silinskas for Mindwidgets
#
# SPDX-License-Identifier: MIT

from state_of_things.state_of_things import State, Thing
from adafruit_led_animation.animation import Animation

"""
`ChargingGlyph`
================================================================================

A `Thing` that represents a glyph that charges when active and touched. 

* Author(s): Aaron Silinskas

"""

class ChargingGlyphStates:
    deactivated: State
    activating: State
    activated: State
    deactivating: State
    charging: State
    charged: State
    discharging: State


class ChargingGlyph(Thing):
    """A glyph that charges when active and touched."""

    def __init__(self, charge_time: float = 5.0, discharge_time: float = 2.0):
        """Construct a new ChargingGlyph that is deactivated."""
        super().__init__(ChargingGlyphStates.deactivated)
        self._charge_time: float = charge_time
        self._discharge_time: float = discharge_time
        
        self._activated: bool = False
        self._touched: bool = False        
        self._charge_level: float = 0.0  # Charge level from 0.0 to 1.0

        self._deactivated_animation: Animation = None
        self._activated_animation: Animation = None
        self._charging_animation: Animation = None
        self._charged_animation: Animation = None
        self._discharging_animation: Animation = None

    def set_animations(
        self,
        deactivated: Animation = None,
        activated: Animation = None,
        charging: Animation = None,
        charged: Animation = None,
        discharging: Animation = None,
        deactivating: Animation = None,
    ):
        """Set the animations for each state."""
        self._deactivated_animation = deactivated
        self._activated_animation = activated
        self._charging_animation = charging
        self._charged_animation = charged
        self._discharging_animation = discharging
        self._deactivating_animation = deactivating

    @property
    def activated(self) -> bool:
        return self._activated

    @activated.setter
    def activated(self, value: bool):
        self._activated = value
        
    @property
    def touched(self) -> bool:
        return self._touched

    @touched.setter
    def touched(self, value: bool):
        self._touched = value       
        
    @property
    def charge_level(self) -> float:
        return self._charge_level


class ChargingGlyphDeactivatedState(State):
    def enter(self, thing: ChargingGlyph):
        thing._charge_level = 0.0        
        if thing._deactivated_animation:
            thing._deactivated_animation.fill(0)

    def update(self, thing: ChargingGlyph) -> State:                 
        if thing.activated:
            return ChargingGlyphStates.activating

        if thing._deactivated_animation:
            thing._deactivated_animation.animate()   
        return self


ChargingGlyphStates.deactivated = ChargingGlyphDeactivatedState()

class ChargingGlyphActivatingState(State):
    def enter(self, thing: ChargingGlyph):
        thing._charge_level = 0.0
        if thing._activated_animation:
            thing._activated_animation.fill(0)

    def update(self, thing: ChargingGlyph) -> State:        
        # activation takes 1 second
        if thing.time_active > 1:
            return ChargingGlyphStates.activated

        if thing._activated_animation:
            thing._activated_animation.animate()
        return self
    
ChargingGlyphStates.activating = ChargingGlyphActivatingState()

class ChargingGlyphActivatedState(State):
    def enter(self, thing: ChargingGlyph):
        thing._charge_level = 0.0
        if thing._activated_animation:
            thing._activated_animation.fill(0)

    def update(self, thing: ChargingGlyph) -> State:
        if not thing.activated:
            return ChargingGlyphStates.deactivating
        if thing.touched:
            return ChargingGlyphStates.charging

        if thing._activated_animation:
            thing._activated_animation.animate()
        return self
    
ChargingGlyphStates.activated = ChargingGlyphActivatedState()

class ChargingGlyphDeactivatingState(State):
    def enter(self, thing: ChargingGlyph):
        thing._charge_level = 0.0
        if thing._deactivating_animation:
            thing._deactivating_animation.fill(0)

    def update(self, thing: ChargingGlyph) -> State:
        # deactivation takes 1 second
        if thing.time_active > 1:
            return ChargingGlyphStates.deactivated

        if thing._deactivating_animation:
            thing._deactivating_animation.animate()
        return self

ChargingGlyphStates.deactivating = ChargingGlyphDeactivatingState()

class ChargingGlyphChargingState(State):
    def enter(self, thing: ChargingGlyph):
        if thing._charging_animation:
            thing._charging_animation.fill(0)

    def update(self, thing: ChargingGlyph) -> State:
        if not thing.activated:
            return ChargingGlyphStates.deactivating
        if not thing.touched:
            return ChargingGlyphStates.discharging

        thing._charge_level = min(thing.time_active / thing._charge_time, 1.0)
        print("Charge Level:", thing._charge_level)
        if thing._charge_level >= 1.0:
            return ChargingGlyphStates.charged
        
        if thing._charging_animation:
            thing._charging_animation.animate()            

        return self
    
ChargingGlyphStates.charging = ChargingGlyphChargingState()

class ChargingGlyphChargedState(State):
    def enter(self, thing: ChargingGlyph):
        thing._charge_level = 1.0
        if thing._charged_animation:
            thing._charged_animation.fill(0)

    def update(self, thing: ChargingGlyph) -> State:
        if not thing.activated:
            return ChargingGlyphStates.deactivating

        if thing._charged_animation:
            thing._charged_animation.animate()
        return self
    
ChargingGlyphStates.charged = ChargingGlyphChargedState()

class ChargingGlyphDischargingState(State):
    def enter(self, thing: ChargingGlyph):
        if thing._discharging_animation:
            thing._discharging_animation.fill(0)

    def update(self, thing: ChargingGlyph) -> State:
        if not thing.activated:
            return ChargingGlyphStates.deactivating
        if thing.touched:
            return ChargingGlyphStates.charging

        thing._charge_level = max(1.0 - (thing.time_active / thing._discharge_time), 0.0)
        if thing._charge_level <= 0.0:
            thing._charge_level = 0.0
            return ChargingGlyphStates.activated
        
        if thing._discharging_animation:
            thing._discharging_animation.animate()
        return self
    
ChargingGlyphStates.discharging = ChargingGlyphDischargingState()