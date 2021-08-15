import board
import time

from hardware import Hardware
from state import State, StateMachine
from sound import Sound

hw = Hardware()
hw.setup_neopixels("target1", data=board.D5, count=12, brightness=0.2)

hw.setup_audio(board.A0)
sound = Sound(hw.audio, voices=2)

hw.setup_piezo_sensor("target1", board.A1)

# new_target_delay is set to 4 seconds at start
# new_target_delay decreases on each successful hit
# A target is randomly set to active, where it lights up
# A target stays lit for active_window, then becomes inactive
# If an active target is hit, it counts as a successful hit
# If an inactive target is hit, it counts as a failed hit


class TargetContext:
    def __init__(self, name):
        self.name = name
        self.state = None

class GlobalState:
    targets = [TargetContext("target1")]
    hit_count = 0

gs = GlobalState()


state_machine = StateMachine()

class Idle(State):
    def update(self, ellapsed_time, context):
        current_voltage = hw.piezo(context.name)
        # print("(", current_voltage, ")")
        if current_voltage > 0.15:
            return "Hit"
        return self.name

state_machine.add_state(Idle())

class Hit(State):
    def enter(self, context):
        target_name = context.name
        sound.play_file("rimshot.wav", loop=False, voice=1)

        hw.pixels[target_name].fill((0, 128, 128))
        hw.pixels[target_name].show()

        print("Hit! ", target_name)

    def update(self, ellapsed_time, context):
        current_voltage = hw.piezo(context.name)
        print("(", current_voltage, ")")
        if current_voltage <= 0.15:
            return "Reset"
        return self.name

state_machine.add_state(Hit())

class Reset(State):
    def enter(self, context):
        target_name = context.name
        hw.pixels[target_name].fill((0, 0, 0))
        hw.pixels[target_name].show()

        print("Stop Hit! ",target_name)
        print("( 0 )")
        print("( 0 )")
        print("( 0 )")

    def update(self, ellapsed_time, context):
        return "Idle"

state_machine.add_state(Reset())

for target in gs.targets:
    state_machine.go_to_state("Idle", target)

while True:
    hw.update()
    ellapsed_time = hw.ellapsed_time

    for target in gs.targets:
        state_machine.update(target, ellapsed_time)

    time.sleep(0.01)

    sound.update()
