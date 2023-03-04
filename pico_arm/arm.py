import re
from servo import SmallServo, ServoException


class Arm:
    """Main class to control pico-arm. Reads from serial and moves servos
    according to commands. This class is specific for 4 servos arm.
    """
    set_angle_re = re.compile(r'^set_angle:([a-z0-9_-]+):(\d+)$')
    speed_re = re.compile(r'^set_speed:([0-9]+)$')

    def __init__(self):
        self.servos = {
            "ss_0": SmallServo(2),  # base
            "ss_1": SmallServo(3),  # lower incline
            "ss_2": SmallServo(4),  # upper incline
            "ss_3": SmallServo(5),  # claw
        }

    def process_command(self, command):
        """Process command received from serial"""
        command = command.strip()
        if command == "ping":
            print("pong")
        elif command.startswith("set_angle:"):
            self.process_set_angle(command)
        elif command.startswith("set_speed:"):
            self.process_speed(command)
        else:
            return

    def process_speed(self, speed):
        """Set speed with which servos are moving"""
        m = self.speed_re.match(speed)
        if m:
            speed = m.group(1)
            for servo in self.servos.values():
                servo.set_speed(speed)
            print("done")
        else:
            print("wrong set_speed command format")

    def process_set_angle(self, angle):
        """set angle for specific servo"""
        m = self.set_angle_re.match(angle)
        if m:
            (servo, angle) = m.groups()
            if servo in self.servos:
                try:
                    self.servos[servo].set_angle(angle)
                    print("done")
                except ServoException as ex:
                    print(f"failed:error=[{ex}]")
            else:
                print("Error: servo {} is not available".format(servo))
        else:
            print("Bad set_angle syntax, got: [{}]".format(angle))

