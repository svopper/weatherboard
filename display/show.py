#!/usr/bin/env python3

import os
import time
import signal
import shutil
import requests
import schedule
from PIL import Image
import RPi.GPIO as GPIO
from inky.auto import auto

print("Initializing Inky pHAT")
inky = auto(ask_user=True, verbose=True)
print("Inky pHAT initialized")

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
current_city = CITIES[0]

# Set up RPi.GPIO with the "BCM" numbering scheme
GPIO.setmode(GPIO.BCM)

# Buttons connect to ground when pressed, so we should set them up
# with a "PULL UP", which weakly pulls the input signal to 3.3V.
GPIO.setup(BUTTONS, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def download_image(url):
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        r.raw.decode_content = True
        with open("image.png", 'wb') as f:
            shutil.copyfileobj(r.raw, f)
        print('Image sucessfully Downloaded')
    else:
        print('Image Couldn\'t be retreived')

def build_url(city):
    api_key = os.environ.get("OWA_API_KEY")
    url = "https://weatherboard-api-ca.purplemoss-7aaf1984.westeurope.azurecontainerapps.io/?api_key={}&latitude={}&longitude={}&timezone=Europe/Copenhagen".format(api_key, city.latitude, city.longitude)
    return url

# "handle_button" will be called every time a button is pressed
# It receives one argument: the associated input pin.
def handle_button(pin):
    print("PRESSED")
    current_city = CITIES[BUTTONS.index(pin)]
    download_and_set_image()

def download_and_set_image():
    url = build_url(current_city)
    download_image(url)
    image = Image.open("image.png")
    resizedimage = image.resize(inky.resolution)
    inky.set_image(resizedimage, saturation=1.0)
    # inky.show()


# Loop through out buttons and attach the "handle_button" function to each
# We're watching the "FALLING" edge (transition from 3.3V to Ground) and
# picking a generous bouncetime of 250ms to smooth out button presses.
for pin in BUTTONS:
    GPIO.add_event_detect(pin, GPIO.FALLING, handle_button, bouncetime=250)

def my_function():
    # Replace this with the function you want to run every hour
    download_and_set_image()

if __name__ == '__main__':
    schedule.every(5).seconds.do(my_function)

    while True:
        # Run any scheduled tasks
        schedule.run_pending()

        # Sleep for 1 second before checking for scheduled tasks again
        time.sleep(1)