"""
Robo arm is simple 4-servo robotic arm. 
This file can be used directly on Raspberry pico to control the arm.
"""

import sys
from utime import sleep

from machine import Pin
from pico_bootsel import bootsel

from arm import Arm

POLL_INTERVAL = 0.005

def read_command():
    """Read new line from serial"""
    buf = []
    while True:
        new_chr = sys.stdin.read(1)
        if new_chr == '\x0a':
            cmd = str(buf)
            return cmd
        buf.append(new_chr)

def run_arm():
    """Run while loop with arm controller"""
    arm = Arm()
    led = Pin(25, Pin.OUT)
    led.toggle()
    while True:
        command = read_command()
        if command == "exit":
            sys.exit()
        arm.process_command(command)
        if bootsel.pressed():
            print("exiting back to micropython")
            sys.exit()
        sleep(POLL_INTERVAL)

if __name__ == "__main__":
    run_arm()
