#from __future__ import print_function
import time
import RPi.GPIO as GPIO

GPIO_TRIG = 23
GPIO_ECHO = 24

GPIO_LED_R = 22
GPIO_LED_Y = 27
GPIO_LED_G = 17

GPIO_BUZZER = 25

global WarningCnt
WarningCnt = 0

def measure_dist():
	GPIO.output(GPIO_TRIG, True)
	time.sleep(0.00001)
	GPIO.output(GPIO_TRIG, False)
	start = time.time()

	while GPIO.input(GPIO_ECHO) == 0:
		start = time.time()

	while GPIO.input(GPIO_ECHO) == 1:
		stop = time.time()

	elapsed = stop-start
	dist = (elapsed * 34300)/2
	return dist

def measure_avg():
	dist01 = measure_dist()
	time.sleep(0.1)

	dist02 = measure_dist()
	time.sleep(0.1)

	dist03 = measure_dist()

	dist = (dist01 + dist02 + dist03)/3
	return dist

def set_led(R, Y, G):
	GPIO.output(GPIO_LED_R, R)
	GPIO.output(GPIO_LED_Y, Y)
	GPIO.output(GPIO_LED_G, G)

	global WarningCnt
	#print("%d" % WarningCnt)

	if R:
		WarningCnt+=1
	else:
		WarningCnt = 0


print("Ultrasonic Measurement")

GPIO.setmode(GPIO.BCM)

GPIO.setup(GPIO_TRIG, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

GPIO.setup(GPIO_LED_R, GPIO.OUT)
GPIO.setup(GPIO_LED_Y, GPIO.OUT)
GPIO.setup(GPIO_LED_G, GPIO.OUT)

GPIO.setup(GPIO_BUZZER, GPIO.OUT)

GPIO.output(GPIO_TRIG, False)
GPIO.output(GPIO_LED_G, True)
GPIO.setwarnings(False)


try:
	pwm = GPIO.PWM(GPIO_BUZZER, 262)

	while True:
		dist = measure_avg()
		print("Distance : %.1f" % dist)
		time.sleep(0.5)

		if dist <= 10:
			print("----WARNING----")
			set_led(True, False, False)

			if WarningCnt > 5:
				pwm.start(30)
				time.sleep(0.5)
		elif dist <= 30:
			print("BACK OFF!")
			if WarningCnt > 5:
				pwm.stop()

			set_led(False, True, False)
			#print("elif %d" %  WarningCnt)
		else:
			if WarningCnt > 5:
				pwm.stop()

			set_led(False, False, True)
			#print("else %d" % WarningCnt)

except KeyboardInterrupt:
	pass

finally:
	GPIO.cleanup()
