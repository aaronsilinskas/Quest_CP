"""
USB Serial Hot-Plug Test
"""

from state_of_things import State, Thing, ThingObserver
import supervisor

# STATES


class HotSerialStates:
    disconnected: State
    connected: State


# THING

class HotSerialThing(Thing):
    def __init__(self):
        super().__init__(HotSerialStates.disconnected)
    

# STATE DEFINITIONS

class HotSerialDisconnected(State):
    def enter(self, thing: HotSerialThing):
        print("Serial disconnected")

    def update(self, thing: HotSerialThing) -> State:
        if supervisor.runtime.serial_connected:
            return HotSerialStates.connected

        return self


HotSerialStates.disconnected = HotSerialDisconnected()


class HotSerialConnected(State):
    def enter(self, thing: HotSerialThing):
        print("Serial connected")

    def update(self, thing: HotSerialThing) -> State:
        runtime = supervisor.runtime
        if not runtime.serial_connected:
            return HotSerialStates.disconnected
        if runtime.serial_bytes_available:
            value = input().strip()
            print("Serial bytes in: ", value)

        return self


HotSerialStates.connected = HotSerialConnected()



# MAIN LOOP


class LoggingObserver(ThingObserver):
    def state_changed(self, old_state: State, new_state: State):
        print(f"{old_state.name} -> {new_state.name}")


hotSerial = HotSerialThing()
hotSerial.observers.attach(LoggingObserver())

while True:
    hotSerial.update()
