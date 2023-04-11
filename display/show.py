#!/usr/bin/env python3

import signal
import RPi.GPIO as GPIO

# Gpio pins for each button (from top to bottom)
BUTTONS = [5, 6, 16, 24]

class Location:
    def __init__(self, name, latitude, longitude):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude

# These correspond to buttons A, B, C and D respectively
CITIES = [
    Location("Copenhagen", 55.676098, 12.568337),
    Location("Ålsgårde", 56.075008, 12.545572),
    Location("Karlslunde", 55.566929, 12.245408),
    Location("Aarhus", 56.162939, 10.203921)
]

# Set up RPi.GPIO with the "BCM" numbering scheme
GPIO.setmode(GPIO.BCM)

# Buttons connect to ground when pressed, so we should set them up
# with a "PULL UP", which weakly pulls the input signal to 3.3V.
GPIO.setup(BUTTONS, GPIO.IN, pull_up_down=GPIO.PUD_UP)


# "handle_button" will be called every time a button is pressed
# It receives one argument: the associated input pin.
def handle_button(pin):
    label = CITIES[BUTTONS.index(pin)]
    print("Button press detected on pin: {} label: {}".format(pin, label))


# Loop through out buttons and attach the "handle_button" function to each
# We're watching the "FALLING" edge (transition from 3.3V to Ground) and
# picking a generous bouncetime of 250ms to smooth out button presses.
for pin in BUTTONS:
    GPIO.add_event_detect(pin, GPIO.FALLING, handle_button, bouncetime=250)

# Finally, since button handlers don't require a "while True" loop,
# we pause the script to prevent it exiting immediately.
signal.pause()