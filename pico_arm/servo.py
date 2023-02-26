from machine import Pin, PWM
import utime


class Servo:
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
        self.reset()

    def reset(self):
        # set default freq to 50
        self.pwm.freq(50)
        self.pwm.duty_u16(self.min)

    def calibrate(self):
        self.reset()
        for angle in range(self.min, self.max, self.step):
            self.pwm.duty_u16(angle)
            utime.sleep(self.delay)
        for angle in range(self.max, self.min, -self.step):
            self.pwm.duty_u16(angle)
            utime.sleep(self.delay)

    def set_angle(self, angle):
        angle = int(angle)
        if angle < 0 or angle > 165:
            print("can't set angle outside of range [0;165]")
        else:
            ratio = (self.max - self.min) / 165
            # angle to duty u16
            duty = angle * ratio + self.min
            self.pwm.duty_u16(int(duty))

    def set_speed(self, speed):
        self.step = speed

class SmallServo(Servo):
    min = 1700
    max = 8700


class BigServo(Servo):
    min = 2600
    max = 7200
    

