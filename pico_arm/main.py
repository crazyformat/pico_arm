#!/usr/bin/env python3
from serial_reader import *
from _thread import start_new_thread
from time import sleep
from servo import SmallServo
import re

POLL_INTERVAL = 0.005


class Arm:
    set_angle_re = re.compile(r'^set_angle:([a-z0-9_-]+):(\d+)$')
    speed_re = re.compile(r'^speed:(\d+)$'
    def __init__(self):
        self.servos = {
            "ss_0": SmallServo(2), # base
            "ss_1": SmallServo(3), # lower incline
            "ss_2": SmallServo(4), # upper incline
            "ss_3": SmallServo(5), # claw
        }

    def process_command(self, line):
        line = line.strip()
        if line == "ping":
            print("pong")
        elif line.starts_with("set_angle:"):
            self.process_set_angle(line)
        elif line.starts_with("speed:"):
            self.process_speed(line)
        else:
            return

    def process_speed(self, line):
        m = self.speed_re.match(line)
        if m:
            speed = m.group(1)
            for servo in self.servos:
                servo.set_speed(speed)
                          
    def process_set_angle(self, line):
        m = self.set_angle_re.match(line)
        if m:
            (_c, servo, angle) m.groups()
            if servo in self.servos:
                self.servo[servo].set_angle(angle)
            else:
                print(f"Error: servo {servo} is not available")
        else:
            print(f"Bad set_angle syntax, got: [{line}]")

if __name__ == "__main__":
    arm = Arm()
    # start serial reader thread
    bufferSTDINthread = start_new_thread(bufferSTDIN, ())
    while True:
        line = getLineBuffer()
        if line:
            arm.process_command(line)
        sleep(POLL_INTERVAL)
