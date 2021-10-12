# NTP Clock using MicroPython  
ESP8266 (Wemos D1 Mini) with DHT11 sensor and dot LED matrix on MAX7219  

## Connect sensors and display to ESP32
Connect DHT11 to GND, 3.3V and GPIO-16  

Connect MAX7219 to SPI:

| My ESP8266  | ESP8266       | max7219 8x8x4 LED Matrix |
| ----------  | ------------- | ------------------------ |
| 3V          | 3.3V          | VCC                      |
| GND         | GND           | GND                      |
| D5          | GPIO14        | CLK                      |
| D7          | GPIO13        | DIN                      |
| D8          | GPIO15        | CS (software)            |

# Credits

This library is based on:
- [micropython-max7219](https://github.com/mcauser/micropython-max7219) by [mcauser](https://github.com/mcauser)
- [esp8266-captive-portal](https://github.com/anson-vandoren/esp8266-captive-portal) by [anson-vandoren](https://github.com/anson-vandoren)