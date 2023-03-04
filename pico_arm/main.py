import sys
from utime import sleep
from _thread import start_new_thread

from serial_reader import *
from machine import Pin
from pico_bootsel import bootsel

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
        if bootsel.pressed():
            print("exiting back to micropython")
            sys.exit()
        sleep(POLL_INTERVAL)
