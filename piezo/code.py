import board
import time
import random
from hardware import Hardware
from state import State, StateMachine
from sound import Sound

hw = Hardware()
hw.setup_neopixels("target1", data=board.D5, count=1, brightness=0.2)

hw.setup_audio(board.A0)
sound = Sound(hw.audio, volume=0.1, voices=2)

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
    score = 0
    next_target = 0


gs = GlobalState()

state_machine = StateMachine()


class Idle(State):
    def enter(self, context):
        target_name = context.name
        hw.pixels[target_name].fill((0, 0, 0))
        hw.pixels[target_name].show()

    def update(self, ellapsed_time, context):
        current_voltage = hw.piezo(context.name)
        # print("(", current_voltage, ")")
        if current_voltage > 0.15:
            return "Miss"
        return self.name


state_machine.add_state(Idle())


class Miss(State):
    blink_color = (255, 0, 0)
    blink_duration = 0.2

    def enter(self, context):
        target_name = context.name
        context.miss_time = 0
        context.miss_pixels_on = True
        context.miss_blinks = 0

        hw.pixels[target_name].fill(self.blink_color)
        hw.pixels[target_name].show()

        sound.play_file("dv_have.wav", loop=False, voice=1)

        print("Miss! ", context.name)

    def update(self, ellapsed_time, context):
        target_name = context.name
        context.miss_time += ellapsed_time

        if context.miss_time > self.blink_duration:
            while context.miss_time > self.blink_duration:
                context.miss_time -= self.blink_duration
                context.miss_pixels_on = not context.miss_pixels_on
                if not context.miss_pixels_on:
                    context.miss_blinks = context.miss_blinks + 1

            color = self.blink_color if context.miss_pixels_on else (0, 0, 0)
            hw.pixels[target_name].fill(color)
            hw.pixels[target_name].show()

        if context.miss_blinks >= 4:
            return "Idle"
        return self.name


state_machine.add_state(Miss())


class Active(State):
    active_duration = 1

    def enter(self, context):
        target_name = context.name
        context.active_time = 0

        hw.pixels[target_name].fill((0, 255, 255))
        hw.pixels[target_name].show()

        print("Active! ", context.name)

    def update(self, ellapsed_time, context):
        context.active_time += ellapsed_time

        current_voltage = hw.piezo(context.name)
        # print("(", current_voltage, ")")
        if current_voltage > 0.15:
            return "Hit"

        if context.active_time > self.active_duration:
            return "Idle"
        return self.name


state_machine.add_state(Active())


class Hit(State):
    cooldown_duration = 1

    def enter(self, context):
        target_name = context.name
        context.hit_cooldown = self.cooldown_duration

        hw.pixels[target_name].fill((0, 255, 0))
        hw.pixels[target_name].show()

        sound.play_file("rimshot.wav", loop=False, voice=1)

        gs.score += 1

        print("Hit! ", target_name, " Score = ", gs.score)

    def update(self, ellapsed_time, context):
        current_voltage = hw.piezo(context.name)

        if current_voltage <= 0.15:
            context.hit_cooldown -= ellapsed_time
            if context.hit_cooldown <= 0:
                return "Idle"
        else:
            print("(", current_voltage, ")")
            context.hit_cooldown = self.cooldown_duration

        return self.name


state_machine.add_state(Hit())

for target in gs.targets:
    state_machine.go_to_state("Idle", target)


while True:
    hw.update()
    ellapsed_time = hw.ellapsed_time

    if gs.next_target <= 0:
        gs.next_target = random.uniform(3, 6)
    gs.next_target -= ellapsed_time

    if gs.next_target <= 0:
        target = random.choice(gs.targets)
        if target.state.name == "Idle":
            state_machine.go_to_state("Active", target)

    for target in gs.targets:
        state_machine.update(target, ellapsed_time)

    if gs.score >= 5:
        gs.score = 0
        gs.next_target = 0

        # sound.play_file("win.wav", loop=False, voice=1)

        for i in range(0, 5):
            sound.play_file("win.wav", loop=False, voice=1)
            for target in gs.targets:
                hw.pixels[target.name].fill((255, 255, 255))
                hw.pixels[target.name].show()
            time.sleep(0.5)
            for target in gs.targets:
                hw.pixels[target.name].fill((0, 0, 0))
                hw.pixels[target.name].show()
            time.sleep(0.5)

    time.sleep(0.01)

    sound.update()
