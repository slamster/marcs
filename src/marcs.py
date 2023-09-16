#!/usr/bin/python
# TODO: clean this code and split in classes

from time import sleep, time
import RPi.GPIO as GPIO
from adafruit_servokit import ServoKit    #https://circuitpython.readthedocs.io/projects/servokit/en/latest/
from enum import Enum
#from picamera import PiCamera
 # - picamera is broken on 64 bit, garbage

# this thing needs root, wtf
#import keyboard

from picamera2 import Picamera2

# Our own stuff
from modules.image.process import Process

from modules.face.facecolors import FaceColor
from modules.cube.rubikscube import RubiksCube
cube = RubiksCube()
white_face_colors = [
    [FaceColor.ORANGE, FaceColor.GREEN, FaceColor.RED],
    [FaceColor.ORANGE, FaceColor.WHITE, FaceColor.RED],
    [FaceColor.ORANGE, FaceColor.BLUE, FaceColor.RED]
]
cube.set_face_colors(FaceColor.WHITE, white_face_colors)
cube.display()

DIR = 17   # Direction GPIO Pin
STEP = 27  # Step GPIO Pin
EN = 22    # Enable
MS2 = 5   # micro stepping y/n
CW = 0     # Clockwise Rotation
CCW = 1    # Counterclockwise Rotation
SPR = 1600   # Steps per Revolution 1.8 degree from stepper which implies 200 per revolution. Microstepping makes this ~1600
#DELAY = .0001 # delay between steps, tested up to 0.0001 with success (faster probably still fine, but starts jerking cube)
DELAY = .002 # delay between steps, tested up to 0.0001 with success (faster probably still fine, but starts jerking cube)
CLOSE_OK_PIN = 4 # GPIO pin that has sensor, if red light on it's ok
INPUT_BUTTON = 23 # GPIO pin that input button

pca = ServoKit(channels=16)

camera = Picamera2()

class LidState(Enum):
    UNKNOWN = 0
    OPEN = 1
    CLOSED = 2

lid = LidState.UNKNOWN

def buttonCallback(channel):
    global lid
    print(f"\nButton pressed! [channel {channel}] lid [{lid}], making snapshot....")
    #if lid == LidState.UNKNOWN:
    #    print("unknown -> Opening")
    #    openLid()
    #elif lid == LidState.OPEN:
    #    print("open -> closing")
    #    closeLid()
    #elif lid == LidState.CLOSED:
    #    print("closed -> opening")
    #    openLid()
    #else:
    #    printf("Unpossible.")
    
    outdir = "/home/pi/www"
    #outfile = f"marcs-{int(time())}.png"
    outfile = f"marcs-latest.png"
    #camera.capture(outdir + "/" + outfile, format="png")
    la = camera.capture_file(outdir + "/" + outfile, format="png")
    print(f"Output written to [{outdir + '/' + outfile}] -> http://192.168.178.131/{outfile} la:{la}")
    Process(outdir + '/' + outfile).detectCube()

def init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DIR, GPIO.OUT)
    GPIO.setup(STEP, GPIO.OUT)
    GPIO.setup(STEP, GPIO.OUT)
    GPIO.setup(MS2, GPIO.OUT)
    GPIO.setup(EN, GPIO.OUT)
    GPIO.setup(INPUT_BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(CLOSE_OK_PIN, GPIO.IN)
    GPIO.output(DIR, CW)

    GPIO.output(EN, GPIO.LOW)
    GPIO.output(MS2, GPIO.HIGH)
    # All above work, faster than this makes the g-forces on the cube distort itself
    DELAY = .0001

    # Servo kit for open/close/bump
    pca.servo[15].set_pulse_width_range(500, 2500)
    pca.servo[14].set_pulse_width_range(500, 2500)

    # Camera init
    camconfig = camera.create_still_configuration(main={"size": (800, 600)})
    camera.configure(camconfig)
    camera.set_controls({"AnalogueGain": 1, "ColourGains": (1.0,1.0)})
    camera.start()

    # Button interrupt
    GPIO.add_event_detect(INPUT_BUTTON, GPIO.FALLING, callback=buttonCallback, bouncetime=400)
	# Calibrate so we have a known starting position
    calibrate()

# keyboard module:
#def wait_for_keypress():
#    print("Press any key to continue...")
#    event = keyboard.read_event(suppress=True)
#    return event.name

def test():
    GPIO.output(DIR, CCW)
    GPIO.output(STEP, GPIO.HIGH)
    sleep(DELAY)
    GPIO.output(STEP, GPIO.LOW)
    sleep(DELAY)

def rotateLeft():
    print("Rotating counter-clockwise (aka left when viewed from top)")
    GPIO.output(DIR, CCW)
    for x in range(int(SPR/4)):
        GPIO.output(STEP, GPIO.HIGH)
        sleep(DELAY)
        GPIO.output(STEP, GPIO.LOW)
        sleep(DELAY)

    # Check if red light is on, if so we're done
    while not isRedLightOn():
        GPIO.output(STEP, GPIO.HIGH)
        sleep(DELAY)
        GPIO.output(STEP, GPIO.LOW)
        sleep(DELAY)

    # Continue until it's just off, to kill slack
    while isRedLightOn():
        GPIO.output(STEP, GPIO.HIGH)
        sleep(DELAY)
        GPIO.output(STEP, GPIO.LOW)
        sleep(DELAY)

    # Go back until it's back on so our program doesn't complain
    GPIO.output(DIR, CW)
    while not isRedLightOn():
        GPIO.output(STEP, GPIO.HIGH)
        sleep(DELAY)
        GPIO.output(STEP, GPIO.LOW)
        sleep(DELAY)

def rotateRight():
    GPIO.output(DIR, CW)
    print("Going clockwise (aka right when viewed from top)")
    for x in range(int(SPR/4)):
        GPIO.output(STEP, GPIO.HIGH)
        sleep(DELAY)
        GPIO.output(STEP, GPIO.LOW)
        sleep(DELAY)

    # Check if red light is on, if so we're done
    while not isRedLightOn():
        GPIO.output(STEP, GPIO.HIGH)
        sleep(DELAY)
        GPIO.output(STEP, GPIO.LOW)
        sleep(DELAY)

    # Continue until it's just off, to kill slack
    while isRedLightOn():
        GPIO.output(STEP, GPIO.HIGH)
        sleep(DELAY)
        GPIO.output(STEP, GPIO.LOW)
        sleep(DELAY)

    # Go back until it's back on so our program doesn't complain
    GPIO.output(DIR, CCW)
    while not isRedLightOn():
        GPIO.output(STEP, GPIO.HIGH)
        sleep(DELAY)
        GPIO.output(STEP, GPIO.LOW)
        sleep(DELAY)


def setMotorAngle(a, motor=15):
	if motor not in (14, 15):
		print(f"Unknown motor {motor} - abort")
		return
	print(f"Motor {motor} set to angle {a}")
	pca.servo[motor].angle = a
	sleep(1)

def openLid():
    global lid
    print("Opening lid...")
    setMotorAngle(50, motor=15)
    lid = LidState.OPEN

def isRedLightOn():
	# GPIO 4
	# Red light on means we read a 0
	return not GPIO.input(CLOSE_OK_PIN)

def calibrate():
	print(f"Calibrating until we read the close button")
	maxTries = SPR
	while maxTries > 0 and not isRedLightOn():
		GPIO.output(DIR, CCW)
		GPIO.output(STEP, GPIO.HIGH)
		sleep(DELAY)
		GPIO.output(STEP, GPIO.LOW)
		sleep(DELAY)
		maxTries -= 1


def closeLid():
    global lid
    print("Closing lid...")
    # Only allow if Red light indicator is enabled (on)
    # Only the 4 slits should indicate proper position, so closing otherwise might break stuff :)
    if isRedLightOn():
        setMotorAngle(87, motor=15)
        lid = LidState.OPEN
    else:
        print(f"Warning: can not close as indicator is not enabled!")

def bumper():
	# Require open AND redlight check
	openLid();
	if not isRedLightOn():
		print("Red light off - refusing bump!")
		return
	print("Bumping cube...")
	setMotorAngle(70, motor=14)
	setMotorAngle(0, motor=14)
	setMotorAngle(70, motor=14)

def cleanup():
    camera.stop()

    GPIO.output(EN, GPIO.HIGH)
    GPIO.cleanup()
    pca.servo[15].angle=None #disable channel
    pca.servo[14].angle=None #disable channel

def main():
	while True:
		user = input("Enter one of R,L,O,C to continue, q to quit: ")
		if user == "L":
			rotateLeft();
		elif user == "R":
			rotateRight();
		elif user == "T": # Tune/calibrate for red light
			calibrate();
		elif user == "O":
			openLid();
		elif user == "C":
			closeLid();
		elif user == "B":
			bumper();
		elif user == "q":
			print("Stopping...")
			break
		else:
			print("???")

# The actual program
init()
main()
cleanup()

print("Done")
