#!/usr/bin/env python3
import time
from termcolor import colored

BASE_SERVO_AXIS = 'LAS -X'
LOWER_INCLINE_AXIS = 'RAS -Y'
UPPER_INCLINE_AXIS = 'RAS -X'
MAX_SERVO_ANGLE = 165
SERVO_SPEED = 200
MIN_SERVO_SPEED = 50
MAX_SERVO_SPEED = 500
POLL_INTERVAL = 0.05
AXIS_MAX_VALUE = 32767


def js_position_to_step(pos):
    # min-max: -32767:32767
    return (pos // 0.4) + 1

LEVEL_TO_FORMAT = {
    "info": ["green", "on_dark_grey"],
    "err": ["red", "on_dark_grey"],
}

def print_local(level, msg):
    format = LEVEL_TO_FORMAT[level]
    print(f"[{colored(level, *format)}] {msg}") 

class Servo:
    def __init__(
        self,
        log,
        servo_id,
        ser,
        max_angle=MAX_SERVO_ANGLE,
        min_angle=0,
    ):
        self.angle = min_angle
        self.serial = ser
        self.servo_id = servo_id
        self.max_angle = max_angle
        self.min_angle = min_angle
        self.log = log
        self.set_angle(min_angle)

    def move(self, step):
        new_angle = self.angle + step
        if self.min_angle < new_angle < self.max_angle:
            self.angle = int(new_angle)
            self.set_angle(int(new_angle))

    def set_angle(self, angle):
        if self.min_angle <= angle <= self.max_angle:
            self.angle = int(angle)
            print_local("info", f"set_angle:{self.servo_id}:{int(angle)}\n".encode('utf-8'))
            self.serial.write(f"set_angle:{self.servo_id}:{int(angle)}\n".encode('utf-8'))
            res = self.serial.readline()
            res = res.strip().decode('utf-8')
            if res == "done":
                print_local("info", "command accepted")
            else:
                print_local("err", f"didn't get expected response: res = {colored(res, attrs=['bold'])}")
        else:
            print_local("err",f"trying to set angle out of allowed values: {angle}")



class Claw(Servo):
    def grab(self):
        # open claw wide
        print_local("info", "setting angle to 50")
        self.set_angle(50)
        time.sleep(0.4)
        print_local("info", "setting angle to 150")
        self.set_angle(150)
        time.sleep(0.4)

    def open(self):
        self.set_angle(90)
        time.sleep(0.4)

    def close(self):
        self.set_angle(150)
        time.sleep(0.4)

# update angles to duty for wider range
class RoboArm:
    def __init__(self, log, js, ser):
        self.log = log
        self.js = js
        self.serial = ser
        self.servo_speed = SERVO_SPEED
        if not self.ping():
            raise Exception("Failed to ping robo arm")
        self.base = Servo(log, "ss_0", ser)
        self.lower_incl = Servo(log, "ss_1", ser, max_angle=160)
        self.upper_incl = Servo(log, "ss_2", ser, min_angle=90, max_angle=150)
        self.claw = Claw(log, "ss_3", ser, max_angle=150)
        self.reset()
        self.log.info("Initialised Robo Arm")

   # run main robo arm loop
    def run(self):
        while self.js.isConnected():
            self.process_actions()
            self.process_movements()
            self.process_claw()
            self.process_speed()
            time.sleep(POLL_INTERVAL)

    def ping(self):
        self.serial.write("ping\n".encode('utf-8'))
        res = self.serial.readline()
        res = res.strip().decode('utf-8')
        if res == "pong":
            return True
        else:
            False

    def process_speed(self):
        # buttons 10 (select) and 11 (start) to increase or decrease speed
        if self.js.beenPressed('START'):
            new_speed = self.servo_speed + 10
            if MIN_SERVO_SPEED < new_speed < MAX_SERVO_SPEED:
                print_local("info", f"start pressed, increasing speed, new speed: {new_speed}")
                self.servo_speed = new_speed
                self.set_servo_speed()
        elif self.js.beenPressed('SELECT'):
            new_speed = self.servo_speed - 10
            if MIN_SERVO_SPEED < new_speed < MAX_SERVO_SPEED:
                print_local("info", f"select pressed, decreasing speed, new speed: {new_speed}")
                self.servo_speed = new_speed
                self.set_servo_speed()


    def process_claw(self):
        # claw control, either open or closed
        if self.js.isPressed('RB') or self.js.isPressed('RB'):
            print_local("info", "RB, moving right")
            self.claw.move(2)
        elif self.js.isPressed('LB') or self.js.isPressed('LB'):
            print_local("info", "LB, moving left")
            self.claw.move(-2)

        # claw is a different type of axis
        # when button is not pushed, claw should not move
        # but when axis changes from default we want to set
        # claw in according position
        # where 0 means middle claw position
        # 32767 means claw is close
        # values close to -32767 means claw is open
        claw_axis_pos = self.js.axis('RT')
        if claw_axis_pos != -1:
            print_local("info", f"moving claw, {claw_axis_pos}")
            claw_axis_pos += 1
            pos_to_angle = claw_axis_pos / \
                ( 2 / MAX_SERVO_ANGLE)
            self.claw.set_angle(pos_to_angle)

    def process_movements(self):
        base_axis_pos = self.js.axis(BASE_SERVO_AXIS)
        if base_axis_pos > 0.05 or base_axis_pos < -0.05:
            print_local("info", "moving base servo")
            self.base.move(js_position_to_step(base_axis_pos))

        upper_incl_axis_pos = self.js.axis(UPPER_INCLINE_AXIS)
        if upper_incl_axis_pos > 0.05 or upper_incl_axis_pos < -0.05:
            print_local("info", "moving upper incline servo")
            self.upper_incl.move(js_position_to_step(
                upper_incl_axis_pos
            ))
        lower_incl_axis_pos = self.js.axis(LOWER_INCLINE_AXIS)
        if lower_incl_axis_pos > 0.05 or lower_incl_axis_pos < -0.05:
            print_local("info", "moving lower incline servo")
            self.lower_incl.move(js_position_to_step(
                lower_incl_axis_pos
            ))

    def process_actions(self):
        if self.js.beenPressed('A'):
            print_local("info", "A - claw grab")
            self.claw_grab()
        if self.js.beenPressed('B'):
            print_local("info", "B - attack")
            self.attack()
        if self.js.beenPressed('X'):
            print_local("info", "X - cobra pose")
            self.cobra_pose()
        if self.js.beenPressed('Y'):
            print_local("info", "Y - shrunk pose")
            self.shrunk()

    # get back to balanced pose, reset servo speed
    def reset(self):
        # send reset command over serial to put arm in default state (shrunk pose?)
        self.servo_speed = SERVO_SPEED
        self.set_servo_speed()
        self.balanced_pose()

    # send servo speed to pico-arm
    def set_servo_speed(self):
        self.serial.write(f"set_speed:{self.servo_speed}\n".encode('utf-8'))

    def claw_grab(self):
        self.claw.grab()

    def attack(self):
        self.balanced_pose()
        time.sleep(0.2)
        self.claw.open()
        self.lower_incl.set_angle(100)
        self.upper_incl.set_angle(100)
        time.sleep(0.1)
        self.claw.grab()
        time.sleep(0.1)
        self.claw.grab()
        time.sleep(0.1)
        self.claw.grab()
        time.sleep(0.1)
        self.balanced_pose()
        time.sleep(0.1)
        pass

    def balanced_pose(self):
        # set all servos to some middle values
        self.base.set_angle(100)
        time.sleep(0.4)
        self.lower_incl.set_angle(70)
        time.sleep(0.4)
        self.upper_incl.set_angle(100)
        time.sleep(0.05)
        self.claw.set_angle(90)
        pass

    def cobra_pose(self):
        # raise arm as high as possible
        # open claw
        self.lower_incl.set_angle(20)
        self.upper_incl.set_angle(100)
        self.claw.open()
        time.sleep(0.2)
        pass

    def shrunk(self):
        pass

    def speed_up(self):
        if MIN_SERVO_SPEED < self.servo_speed + 10 < MAX_SERVO_SPEED:
            self.servo_speed += 10
            self.set_servo_speed()
        else:
            pass

    def speed_down(self):
        if MIN_SERVO_SPEED < self.servo_speed - 10 < MAX_SERVO_SPEED:
            self.servo_speed -= 10
            self.set_servo_speed()
        else:
            pass
