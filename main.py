from captive_portal import CaptivePortal
from machine import Pin, SPI, Timer
# from font_4x6 import font_4x6 as FONT
from font_6x8 import font_6x8 as FONT
import dht
import max7219
import ntptime
import utime
import time
import gc

portal = CaptivePortal()
portal.start()

gc.collect()

# config parameters
MAX7219_NUM          = 4      # Number of MAX7219 LED modules
MAX7219_BRIGHTNESS   = 1      # MAX7219 brightness (0-15)

spi = SPI(1, baudrate=10000000, polarity=0, phase=0)
display = max7219.Matrix8x8(spi, Pin(15, Pin.OUT), MAX7219_NUM)
display.brightness(MAX7219_BRIGHTNESS)
display.fill(0)
display.show()

"""
# put text (4x6 font) on frame buffer
def put_text(fbuf, text, x=0, y=0):
    for uchr in text:
        sym = FONT[ord(uchr)]
        for i in range(4):
            for j in range(6):
                fbuf.pixel(x + i, y + j, 1 if (sym[i] & (0x20 >> j)) else 0)
        x += 4
"""

# put text (6x8 font) on frame buffer
def put_text(fbuf, text, x=0, y=0):
    for uchr in text:
        sym = FONT[ord(uchr)]
        for i in range(6):
            for j in range(8):
                fbuf.pixel(x + i, y + j, 1 if (sym[i] & (0x80 >> j)) else 0)
        x += 6

# Set time
ntptime.settime()
rtc = machine.RTC()
utc_shift = 3

tm = utime.localtime(utime.mktime(utime.localtime()) + utc_shift*3600)
tm = tm[0:3] + (0,) + tm[3:6] + (0,)
rtc.datetime(tm)

# blink blue LED 3 times
led = Pin(2, Pin.OUT) # blue LED
for i in range(3):
    led.value(1)
    display.fill(1)
    display.show()
    time.sleep_ms(250)
    led.value(0)
    display.fill(0)
    display.show()
    time.sleep_ms(250)

put_text(display, "HELLO", x=1)
display.show()
time.sleep_ms(1000)

# FSM
cnt = 0
fsm = 0
days = {0: "Mon", 1: "Tues", 2: "Wed", 3: "Thurs", 4: "Fri", 5: "Sat", 6: "Sun"}


# DHT11 wrapper
class _DHT11_:
    def __init__(self, gpio_n):
        self.sensor = dht.DHT11(machine.Pin(gpio_n))
        self.t = 0
        self.h = 0
        self.m = True

    def run(self):
        if self.m:
            self.m = False
            self.sensor.measure() # poll DHT11 sensor
        else:
            self.m = True
            self.t = self.sensor.temperature()
            self.h = self.sensor.humidity()
            #print("DHT11: t=%f, h=%f" % (self.t, self.h))

    def get(self):
        return self.t, self.h


# DHT11 on GPIO-16
dht11 = _DHT11_(16)

def tick(timer):
    global dht, rtc, cnt, fsm, days
    dht11.run()

    # FSM
    cnt -= 1
    if cnt > 0:
        return

    # get data from sensors
    t, h = dht11.get()
    dt = rtc.datetime()

    if fsm == 1:
        fsm = 2  # show temperature
        cnt = 3
        txt = "%.1f°" % t
        # txt = "fsm1"
    elif fsm == 2:
        fsm = 3  # showh humidity
        cnt = 2
        txt = "%.1f%%" % h
        # txt = "fsm2"
    elif fsm == 3:
        fsm = 4  # show weekday
        cnt = 1
        txt = days[dt[3]]
    else:  # fsm == 4
        fsm = 1  # show time
        cnt = 6
        txt = "%02i:%02i" % (dt[4], dt[5])

    display.fill(0)
    put_text(display, txt, x=1, y=0)
    display.show()
    gc.collect()

# init periodic timer
timer = Timer(-1)
timer.init(period=1000, mode=Timer.PERIODIC, callback=tick)
