from arm import Arm


def test_arm():
    arm = Arm()
    assert arm is not None

def test_ping(capsys):
    arm = Arm()
    arm.process_command("ping")
    captured = capsys.readouterr()
    assert captured.out == "pong\n"
    
def test_set_angle(capsys):
    arm = Arm()
    arm.process_command("set_angle:")
    captured = capsys.readouterr()
    assert captured.out == "Bad set_angle syntax, got: [set_angle:]\n"    
    
    arm.process_command("set_angle:ss_0")
    captured = capsys.readouterr()
    assert captured.out == "Bad set_angle syntax, got: [set_angle:ss_0]\n"    
    
    arm.process_command("set_angle:ss_0:abc")
    captured = capsys.readouterr()
    assert captured.out == "Bad set_angle syntax, got: [set_angle:ss_0:abc]\n"

    arm.process_command("set_angle:ss_123:0")
    captured = capsys.readouterr()
    assert captured.out == "Error: servo ss_123 is not available\n"

    arm.process_command("set_angle:ss_0:1000")
    captured = capsys.readouterr()
    assert captured.out == "can't set angle outside of range [0;165]\ndone\n"
    
    # good cases
    arm.process_command("set_angle:ss_0:0")
    arm.process_command("set_angle:ss_0:180")
    
    
def test_set_speed(capsys):
    arm = Arm()
    arm.process_command("set_speed:123")
    capsys.readouterr()
    arm.process_command("set_speed:-100")
    captured = capsys.readouterr()
    assert captured.out == "wrong set_speed command format\n"
    
    arm.process_command("set_speed:abc")
    captured = capsys.readouterr()
    assert captured.out == "wrong set_speed command format\n"
    
    
    