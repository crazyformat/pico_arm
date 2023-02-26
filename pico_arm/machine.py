# pylint: disable=too-few-public-methods

class Pin:
    """mock for pin"""
    def __init__(self, pin):
        self.pin = pin


class PWM:
    """mock for pwn"""
    def __init__(self, pin):
        self.pin = pin
        self.frequency = 0
        self.duty = 0

    def freq(self, freq):
        self.frequency = freq
        
    def duty_u16(self, angle):
        self.duty = angle