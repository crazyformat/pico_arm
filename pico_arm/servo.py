"""
Servo module is for Servo class and few additional
classes with correct min/max values for diffrent types of servos.
"""
from machine import Pin, PWM
import utime

MOVE_DELAY = 0.005  # 5ms

class ServoException(Exception):
    """Indicate failure on servo commands"""
    pass

class Servo:
    """Simple wrapper class for servos"""
    # safe default values, redefined per servo type
    min = 2000
    max = 7000
    # how fast servo is moving, lower step - smoother go
    step = 200
    # how long to wait after moving the servo
    delay = 0.05

    def __init__(self, pin):
        self.pin = pin
        self.pwm = PWM(Pin(pin))
        self.curr_pos = 0
        self.reset()

    def reset(self):
        """Set servo to min position"""
        # set default freq to 50
        self.pwm.freq(50)
        self.set_angle(0)
        self.curr_pos = self.min

    def calibrate(self):
        """Move servo from min to max position and backwards"""
        self.reset()
        for angle in range(self.min, self.max, self.step):
            self.pwm.duty_u16(angle)
            utime.sleep(self.delay)
        for angle in range(self.max, self.min, -self.step):
            self.pwm.duty_u16(angle)
            utime.sleep(self.delay)

    def set_angle(self, angle):
        """Set servo position to a certain agnle"""
        angle_int = int(angle)
        if angle_int < 0 or angle_int > 165:    
            raise ServoException("can't set angle outside of range [0;165]")
        else:
            self.move_to_angle(angle_int)

    def move_to_angle(self, angle):
        """
        Move smoothly to certain angle.
        Servo will move faster and less smooth with higher speed and
        smoother with lower speed.
        """
        angle = int(angle)
        # angle to duty u16
        ratio = (self.max - self.min) / 165
        target_pos = int(angle * ratio + self.min)
        direction = 1  # move forward
        if target_pos < self.curr_pos:
            direction = -1
        for pos in range(int(self.curr_pos), target_pos, self.step * direction):
            # print(f"DEBUG: moving to {pos}")
            self.pwm.duty_u16(pos)
            utime.sleep(MOVE_DELAY)
        self.curr_pos = target_pos

    def set_speed(self, speed):
        """Set speed with which servo will be moving to a certain angle"""
        self.step = int(speed)

class SmallServo(Servo):
    """Micro (8g) servo"""
    min = 1700
    max = 8700


class BigServo(Servo):
    """Medium (15g) servo"""
    min = 2600
    max = 7200
