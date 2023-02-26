from utime import sleep
from _thread import start_new_thread

from serial_reader import *
from machine import Pin

from arm import Arm

POLL_INTERVAL = 0.005

if __name__ == "__main__":
    arm = Arm()
    # start serial reader thread
    bufferSTDINthread = start_new_thread(bufferSTDIN, ())
    led = Pin(25, Pin.OUT)
    while True:
        line = getLineBuffer()
        if line:
            arm.process_command(line)
        led.toggle()
        sleep(POLL_INTERVAL)
