import RPi.GPIO as GPIO
from time import sleep
import requests
import time

GPIO.setmode(GPIO.BCM)

# Define GPIO pins for the two servos
pan_gpio_pin = 4  # Pin for panning servo
tilt_gpio_pin = 17  # Pin for tilting servo

GPIO.setup(pan_gpio_pin, GPIO.OUT)
GPIO.setup(tilt_gpio_pin, GPIO.OUT)

tilt_limit = 90

# The URL to the API endpoint
api_url = "https://studev.groept.be/api/a23ib2d03/get_servo_values/1"

# Function to get data from the API
def get_servo_values():
    try:
        # Make a GET request to the API
        response = requests.get(api_url)
        # Check if the request was successful
        if response.status_code == 200:
            # Parse the JSON response
            data = response.json()[0]
            # Assuming the response contains the values in a format you expect
            # Example: {"panAngle": 10, "tiltAngle": 20}
            tiltAngle= data['alpha'] 
            panAngle= data['beta'] 
            return panAngle, tiltAngle
        else:
            print("Error fetching data:", response.status_code)
    except requests.exceptions.RequestException as e:
        # Handle any exceptions that occur during the request
        print("Request failed:", e)


def mapTo(val, max1, min1, max2, min2):
    """Map the angle value to the pulse width."""
    return val * (max2 - min2) / (max1 - min1) + min2

def update_servo_angle(gpio_pin, angle):
    """Update the servo angle."""
    pulse = mapTo(angle, 180, 0, 0.0025, 0.0004)
    GPIO.output(gpio_pin, GPIO.HIGH)
    sleep(pulse)
    GPIO.output(gpio_pin, GPIO.LOW)
    sleep(0.02 - pulse)

while True:
    previous_pan_angle = None
    previous_tilt_angle = None
    

    tilt_angle, pan_angle = get_servo_values()
    print(pan_angle, tilt_angle)
    pan_angle += 90
    tilt_angle += 90
    
    
    if tilt_angle > tilt_limit: 
        tilt_angle = tilt_limit
        
    # Update panning servo only if there is a change
    if pan_angle != previous_pan_angle:
        update_servo_angle(pan_gpio_pin, pan_angle)
        previous_pan_angle = pan_angle

    # Update tilting servo only if there is a change
    if tilt_angle != previous_tilt_angle:
        update_servo_angle(tilt_gpio_pin, tilt_angle)
        previous_tilt_angle = tilt_angle

    
    
