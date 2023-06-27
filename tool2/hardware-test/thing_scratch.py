import adafruit_rfm69
from state import Thing
try:
    from typing import Callable, TypeAlias

    Callback: TypeAlias = Callable[[], None]
except ImportError:
    pass


class ButtonThing(Thing):
    # Track press and release of an object
    def __init__(self):
        super().__init__()
        self._on_press = []
        self._on_release = []

    def on_press(self, callback: Callback):
        self._on_press.append(callback)

    def on_release(self, callback: Callback):
        self._on_release.append(callback)

    def press(self):
        for press_callback in self._on_press:
            press_callback()


class TriggerTrackerThing(Thing):
    # Tracks whether the trigger will cast or tune magic

    def pressed(self):
        print("pressed")

    def released(self):
        print("released")


class MagicCoreThing(Thing):
    # Applies the rules of magic and acts as magic storage

    def detect(self):
        print("magic detect")


class MagicTunerByGestureThing(Thing):
    # Tunes to a type of magic by gesture

    def __init__(self, core: MagicCoreThing):
        super().__init__()
        self._core = core

    def start(self):
        print("gesture started")

    def finish(self):
        print("gesture finished")


class InfraredTransceiverThing(Thing):
    # Decode and encode game events over infrared
    def __init__(self, infrared: Infrared):
        super().__init__()
        self._infrared = infrared

    def send_event(self, event):
        print("send event", event)


class RadioTransceiverThing(Thing):
    # Decode and encode events over radio
    def __init__(self, radio: adafruit_rfm69.RFM69):
        super().__init__()
        self._radio = radio

    def send_event(self, event):
        print("send event", event)


class GunCasterThing(Thing):
    # Handles shooting cooldown, magic amount, etc
    # This is where guns and weapons can be customized

    def __init__(self, core: MagicCoreThing):
        super().__init__()
        self._core = core

    def cast(self):
        print("cast")


class ConsoleThing(Thing):
    # Console for game selection and showing status
    def __init__(self, core: MagicCoreThing):
        super().__init__()
        self._core = core


class BarrelThing(Thing):
    # Handles barrel neopixel animations

    def cast(self, magic):
        print("cast", magic)

    def tuning(self, magic, distance):
        print("tuning", magic, distance)


class SampleGameThing(Thing):
    # Sample Game - Process events, apply game rules
    def __init__(self, core: MagicCoreThing):
        super().__init__()
        self._core = core

    def process_event(self, event):
        print("event received", event)

# Wire Up


trigger = ButtonThing()
infrared_transceiver = InfraredTransceiverThing(infrared)
radio_transceiver = RadioTransceiverThing(hardware.radio)

trigger_tracker = TriggerTrackerThing()
trigger.on_press(trigger_tracker.pressed)
trigger.on_release(trigger_tracker.released)

magic_core = MagicCoreThing()

magic_tuner = MagicTunerByGestureThing(magic_core)
trigger_tracker.on_start_tuning = magic_tuner.start
trigger_tracker.on_finish_tuning = magic_tuner.finish

gun_caster = GunCasterThing(magic_core)
trigger_tracker.on_cast = gun_caster.cast

console = ConsoleThing(magic_core)
# what do the console buttons wire up to?

barrel = BarrelThing()
magic_tuner.on_tuning = barrel.tuning
gun_caster.on_cast = barrel.cast

game = SampleGameThing(magic_core)
infrared_transceiver.on_event = game.process_event
radio_transceiver.on_event = game.process_event


def game_start():
    gun_caster.start()
    trigger_tracker.start()
    console.show_game_start()


def game_pause():
    gun_caster.pause()
    trigger_tracker.pause()
    console.show_game_pause()


def game_resume():
    game_start()
    console.show_game_resume()


def game_stop():
    game_pause()
    console.show_game_stop()


game.on_start = game_start
game.on_pause = game_pause
game.on_resume = game_resume
game.on_stop = game_stop

trigger.on_press(lambda: print("another listener"))
trigger.press()