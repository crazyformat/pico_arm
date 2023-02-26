#!/usr/bin/env python
# coding: utf-8
from robo_arm import RoboArm
from gamepad.Controllers import PG9099
from gamepad.Gamepad import available as gamepad_available
import sys
import time
import serial
import logging


def get_joystick():
    if not gamepad_available():
        print('Please connect your gamepad...')
        while not gamepad_available():
            time.sleep(1.0)
    js = PG9099()
    print('Gamepad connected')
    js.startBackgroundUpdates()
    return js


def get_serial():
    return serial.Serial(
        port='/dev/ttyACM0',
        baudrate=115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
    )


if __name__ == "__main__":
    logger = logging.getLogger("robo-arm")
    logger.info("Starting PicoArm controller...")
    try:
        ser = get_serial()
    except serial.serialutil.SerialException as ex:
        logger.error(f"Failed to get serial port, got exception: {ex}")
        sys.exit(1)

    print("Setting up PicoArm control side")
    try:
        js = get_joystick()
    except Exception as ex:
        logger.error(f"Failed to setup joystick, exception: {ex}")

    arm = RoboArm(logger, js, ser)
    logger.info("PicoArm has responded, moving on to main event loop")
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
