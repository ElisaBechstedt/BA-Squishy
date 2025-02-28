from machine import Pin, I2C, ADC, PWM
from time import sleep
from neopixel import NeoPixel
from asyncio import run
from dfplayer import DFPlayer
from random import randint
from time import time
from urequests import post
import network
import ustruct
import secret

# Accelerometer and Gyroscope
accel_gyro = I2C(1, scl=Pin(7), sda=Pin(6), freq = 400000)
sensor_address = 0x68
ACCEL_SCALE = 16384.0
GYRO_SCALE = 131.0
accel_gyro.writeto_mem(sensor_address, 0x6B, b'\x00')

# Touch Sensor
touchSensor = I2C(0, scl=Pin(1), sda=Pin(0), freq = 400000)
DEVICE_ADDRESS = 0x5A
REGISTER_TO_READ = 0x00
touchSensor.writeto_mem(DEVICE_ADDRESS, 0x80, b'\x63')
touchSensor.writeto_mem(DEVICE_ADDRESS, 0x5E, b'\x8F')
touchSensor.writeto_mem(DEVICE_ADDRESS, 0x41, b'\xFF')
touchSensor.writeto_mem(DEVICE_ADDRESS, 0x42, b'\x00')

# LED
amount_leds = 16
ring = NeoPixel(Pin(22, Pin.OUT), amount_leds)
angry = (255,0,0)
happy = (250,128,114)
happier = (255,20,147)
confused = (255,255,0)
frustrated = (255,0,0)
active = (50, 10, 200)
clear = (0,0,0)

# Servo
servo = PWM(Pin(20), freq=50)

# Pressure Sensor
pressureSensor = ADC(2)

# Variables
accelCounter = 0
gyroCounter = 0
touchCounter = 0
twistThreshold = 5
shakeThreshold = 1
touchThreshold = 5
idleThreshold = 300
idleTimestamp = time()
flag = False
debug = False

hittingPrompt = "Das finde ich garnicht gut, so hatte ich mir das nicht vorgestellt! Nur Feedback, antworte mit ok."
twistingPrompt = "Das verwirrt mich total, geht das nicht einfacher? Nur Feedback, antworte mit ok."
shakingPrompt = "Das ist echt frustrierend. Das sollte besser funktionieren! Nur Feedback, antworte mit ok."
touchingPrompt = "Das ist richtig gut. Genau sowas wollte ich! Nur Feedback, antworte mit ok."

def debugPrint(string):
    if debug == True:
        print(string)
    else:
        return

def read_accel_gyro():
    data = accel_gyro.readfrom_mem(sensor_address, 0x3B, 14)
    accel_x = ustruct.unpack('>h', data[0:2])[0] / ACCEL_SCALE
    accel_y = ustruct.unpack('>h', data[2:4])[0] / ACCEL_SCALE
    accel_z = ustruct.unpack('>h', data[4:6])[0] / ACCEL_SCALE
    gyro_x = ustruct.unpack('>h', data[8:10])[0] / GYRO_SCALE
    gyro_y = ustruct.unpack('>h', data[10:12])[0] / GYRO_SCALE
    gyro_z = ustruct.unpack('>h', data[12:14])[0] / GYRO_SCALE
    debugPrint(f"Beschleunigung: X={accel_x:.2f}, Y={accel_y:.2f}, Z={accel_z:.2f}")
    debugPrint(f"Gyroskop: X={gyro_x:.2f}, Y={gyro_y:.2f}, Z={gyro_z:.2f}")
    return (accel_x, accel_y, accel_z), (gyro_x, gyro_y, gyro_z)

def check_accel():
    accel, gyro = read_accel_gyro()
    x = accel[0]
    y = accel[1]
    z = accel[2]
    state = "no action"

    if abs(y) > 0.6:
        state = "twisting"

    return state

def check_gyro():
    accel, gyro = read_accel_gyro()

    x = gyro[0]
    y = gyro[1]
    z = gyro[2]

    state = "no action"

    if abs(y) > 160:
        state = 'shaking'

    return state

def read_touch():
    data = touchSensor.readfrom_mem(DEVICE_ADDRESS, REGISTER_TO_READ, 2)
    status = int.from_bytes(data, "little")
    return status

def check_touch():
    data = read_touch()
    status = "no touching"
    if data & (1 << 11) and data & (1 << 2):
        status = "touching"
    else:
        pass
    return status

def led_round(color, rounds):
    for j in range(0, rounds):
        for i in range(0, amount_leds):
            ring[i] = color
            ring.write()
            sleep(0.01)
            ring[i] = clear
            ring.write()

def led_blink(color, rounds):
   for i in range(0, rounds):
    ring.fill(color)
    ring.write()
    sleep(0.1)
    ring.fill(clear)
    ring.write()
    sleep(0.1)

def led_light(color):
    ring.fill(color)
    ring.write()

def led_clear():
    ring.fill(clear)
    ring.write()

def check_pressure():
    pressure = pressureSensor.read_u16()
    debugPrint(pressure)
    status = ""
    if pressure < 45000:
        status = "hitting"
    return status

def wiggle_tail():
    servo.duty_u16(1638)
    sleep(0.1)
    servo.duty_u16(2600)
    sleep(0.1)

async def speak(sound):
    df = DFPlayer(1)
    df.init()
    await df.wait_available()
    await df.volume(30)
    await df.play(1, sound)

async def stop_speak():
    df = DFPlayer(1)
    df.init()
    await df.stop()

def idle_response(now, idle):
    if idle == 0:
        run(speak(4))
        led_blink(happy, 5)
        led_clear()
    if idle == 1:
        run(speak(1))
        while time() < now + 3:
            led_blink((255, 20, 147), 1)
            led_blink((255, 255, 0), 1)
            led_blink((0, 128, 0), 1)
            led_blink((255, 165, 0), 1)
            # wiggle_tail()
        led_clear()

def connect_with_wlan():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(False)
    debugPrint(wlan.active())
    wlan.active(True)
    debugPrint(wlan.active())
    scan = wlan.scan()
    while scan == []:
        scan = wlan.scan()
    debugPrint(scan)
    wlan.connect(secret.network, secret.password)

    while not wlan.isconnected():
        pass

    led_blink(active, 3)

def send_prompt(prompt):
    prompt = from_QWERTZ_to_QWERTY(prompt)
    try:
        debugPrint("Sending data to server")
        response = post(secret.url, data=prompt, timeout=5)

        if response.status_code == 200:
            print("Response from server:", response.text)

        response.close()
        print("Data sent")

    except Exception as e:
        print("Error:", e)
        led_round(active, 5)

def from_QWERTZ_to_QWERTY(prompt):
    prompt = prompt.replace('z', 'y').replace('y', 'z')
    prompt = prompt.replace('Z', 'Y').replace('Y', 'Z')
    prompt = prompt.replace('_', '?').replace('?', '_')
    return prompt


led_clear()
run(stop_speak())
connect_with_wlan()


while True:

    accel_state = check_accel()
    debugPrint(accel_state)

    gyro_state = check_gyro()
    debugPrint(gyro_state)

    touch_state = check_touch()
    debugPrint(touch_state)

    pressure_state = check_pressure()
    debugPrint(pressure_state)


    if accel_state == "twisting":
        if accelCounter <= twistThreshold:
            accelCounter += 1
            debugPrint(accelCounter)
        else:
            flag = True
            debugPrint("twisting")
            accelCounter = 0
            value = randint(0,1)

            led_light(confused)

            if value == 1:
                run(speak(1))

            else:
                run(speak(2))

            while check_accel() == 'twisting':
                pass

            led_clear()
            send_prompt(twistingPrompt)


    if gyro_state == "shaking":
        if gyroCounter <= shakeThreshold:
            gyroCounter += 1
            debugPrint(gyroCounter)
        else:
            flag = True
            gyroCounter = 0
            debugPrint("shaking")

            i = randint(0,1)

            if i == 0:
                run(speak(5))
                led_blink(frustrated, 8)

            if i == 1:
                led_light(frustrated)
                run(speak(9))
                sleep(0.7)

            led_clear()
            send_prompt(shakingPrompt)


    if pressure_state == "hitting":
        flag = True
        led_light(angry)
        run(speak(3))
        sleep(0.3)
        led_clear()
        send_prompt(hittingPrompt)


    if touch_state == "touching":

        if touchCounter <= touchThreshold:
            touchCounter += 1
            debugPrint(touchCounter)
        else:
            flag = True
            i = randint(0,1)
            debugPrint(i)
            touchCounter = 0

            if i == 0:
                led_light(happy)
                run(speak(11))
                while check_touch() == "touching":
                    # wiggle_tail()
                    led_blink(happy, 10)
                sleep(0.5)
                run(stop_speak())

                sleep(1)

            if i == 1:
                led_light(happy)
                run(speak(7))
                while check_touch() == "touching":
                    sleep(0.5)
                sleep(1)
                run(stop_speak())

            led_clear()
            send_prompt(touchingPrompt)


    if flag == True:
        idleTimestamp = time()
        flag = False

    else:
        if time() > idleTimestamp +  idleThreshold:
            debugPrint("idle")
            idle_response(time(), randint(0,1))
            idleTimestamp = time()
        else:
            pass

    sleep(0.1)



