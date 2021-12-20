#from __future__ import print_function
import time
import RPi.GPIO as GPIO

#초음파 센서 연결
GPIO_TRIG = 23 #GPIO 23에 TRIGGER 연결 
GPIO_ECHO = 24 #GPIO 24에  ECHO연결

#LED 연결
GPIO_LED_R = 22 #GPIO 22에 LED RED 연결
GPIO_LED_Y = 27 #GPIO 27에 LED YELLOW 연결
GPIO_LED_G = 17 #GPIO 17에 LED GREEN 연결

#부저 연결
GPIO_BUZZER = 25 #GPIO 25에 BUZZER 연결

#RED ZONE에 머무는 기간 세기위한 변수
global WarningCnt
WarningCnt = 0

#초음파 거리를 계산한다
def measure_dist():
	GPIO.output(GPIO_TRIG, True) #트리거 핀 ON 상태로 만들어 출력 내보내기
	time.sleep(0.00001)
	GPIO.output(GPIO_TRIG, False) #트리거 핀 OFF 상태로 만들어 출력 중지
	start = time.time()

	while GPIO.input(GPIO_ECHO) == 0:
		start = time.time() #에코 핀 ON 되는 시점을 시작 시간으로 설정

	while GPIO.input(GPIO_ECHO) == 1:
		stop = time.time() #에코 핀 OFF 되는 시점을 반사파 수신 시간으로 설정

	elapsed = stop-start #수신시간 - 시작시간으로 펄스 길이 계산

	#음속은 편의상 343m/s으로 계산
	#초음파는 반사판이기 때문에 실제 이동 거리는 2배, 따라서 나누기 2를 함
	dist = (elapsed * 34300)/2 

	return dist

#초음파 거리 계산한다 > 실제 거리 계산에 사용할 평균 값
def measure_avg():
	dist01 = measure_dist()
	time.sleep(0.1)

	dist02 = measure_dist()
	time.sleep(0.1)

	dist03 = measure_dist()

	#0.1초 간격으로 초음파의 거리를 받아온다.
	#0.1초 간격으로 받은 거리를 기준으로 평균을 내 반환한다
	dist = (dist01 + dist02 + dist03)/3 
	return dist

#LED를 세팅한다 
#각 매개 변수에 True 또는 False 값을 넣는다
#R : Red / Y : Yellow / G : Green
def set_led(R, Y, G):
	#LED를 켜거나 끈다
	GPIO.output(GPIO_LED_R, R) 
	GPIO.output(GPIO_LED_Y, Y)
	GPIO.output(GPIO_LED_G, G)

	global WarningCnt #RED ZONE에 머무는 횟수 확인

	if R: #R == True → Red zone에 들어가 있으면 
		WarningCnt+=1 #WarningCnt에 1을 증가한다
	else: #Red Zone에 없으면 
		WarningCnt = 0 #WarningCnt를 0으로 바꾼다


print("Ultrasonic Measurement")

GPIO.setmode(GPIO.BCM) #핀번호를 GPIO 모듈 번호로 사용하도록 세팅

#초음파 센서 설정
GPIO.setup(GPIO_TRIG, GPIO.OUT) #출력
GPIO.setup(GPIO_ECHO, GPIO.IN) #입력

#LED 설정
GPIO.setup(GPIO_LED_R, GPIO.OUT) #출력
GPIO.setup(GPIO_LED_Y, GPIO.OUT) #출력
GPIO.setup(GPIO_LED_G, GPIO.OUT) #출력

#부저 설정
GPIO.setup(GPIO_BUZZER, GPIO.OUT) #출력

GPIO.output(GPIO_TRIG, False) #트리거 핀 OFF 상태로 만듦
GPIO.output(GPIO_LED_G, True) #GREEN LED를 켬. 시작은 GREEN LED만 켜두록 함
GPIO.setwarnings(False) # GPIO 사용 경고 해제

try:
	pwm = GPIO.PWM(GPIO_BUZZER, 262) #부저 값 세팅

	while True:
		dist = measure_avg() #초음파 센서로 거리를 받아온다
		print("Distance : %.1f" % dist) #거리 출력
		time.sleep(0.5)

		if dist <= 10: #거리 10cm 이내에 들어오면
			print("----WARNING----")
			set_led(True, False, False) #red led만 켠다

			if WarningCnt > 5: #red zone에 5회 이상 머물 경우
				pwm.start(30) #부저를 울린다
				time.sleep(0.5)
		elif dist <= 30: #10cm 초과, 30cm이내에 들어오면
			print("BACK OFF!")
			if WarningCnt > 5: #red 존에 벗어났으므로
				pwm.stop() #부저를 멈춘다

			set_led(False, True, False) #yellow led만 켠다
			#print("elif %d" %  WarningCnt)
		else: #30cm를 초과할 경우
			if WarningCnt > 5: #red 존에 벗어났으므로
				pwm.stop() #부저를 멈춘다

			set_led(False, False, True) #green led만 켠다
			#print("else %d" % WarningCnt)

except KeyboardInterrupt:
	pass

finally:
	GPIO.cleanup()
