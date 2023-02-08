#!/usr/bin/env python
# coding: utf-8
from robo_arm import RoboArm
import Gamepad.Gamepad
from Gamepad.Gamepad import available as gamepad_available
import time
import serial
import logging


def get_joystick():
    if not gamepad_available():
        print('Please connect your gamepad...')
        while not gamepad_available():
            time.sleep(1.0)
    js = Gamepad.PG9099()
    print('Gamepad connected')
    js.startBackgroundUpdates()
    return js


def get_serial():
    return serial.Serial(
        port='/dev/ttyS0',  # Change this according to connection methods, e.g. /dev/ttyUSB0
        baudrate=115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
    )


if __name__ == "__main__":
    print("Starting PicoArm controller...")
    js = get_joystick()
    ser = get_serial()
    logger = logging.getLogger("robo-arm")
    print("Setting up PicoArm control side")
    arm = RoboArm(logger, js, ser)
    print("PicoArm has responded, moving on to main event loop")
    print(
        "PicoArm controls:\n"
        " - speed controls: Select - "
        "decrease servo speed, Start - increase servo speed\n"
        " - claw:\n"
        "  * slowly open/close - right shift and left shift (RB/LB)\n"
        "  * direct claw controrl with ZR - right lower shift\n"
        " - movements:\n"
        "  * base left/right - Left joystick X axis\n"
        "  * lower arm - Right joystick Y axis\n"
        "  * upper arm - Right joystick X axis\n"
        " - actions:\n"
        "  * A - claw grab\n"
        "  * B - attack, lean forward and bite few times\n"
        "  * X - cobra pose\n"
        "  * Y - shrunk pose\n"
    )
    # Joystick events handled in the background
    try:
        arm.run()
    finally:
        # Ensure the background thread is always terminated when we are done
        js.disconnect()
