import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
GPIO.setup(7, GPIO.IN)  # Set pin 7 as an input pin

print(GPIO.input(7))  # Prints 0 if LOW, 1 if HIGH
