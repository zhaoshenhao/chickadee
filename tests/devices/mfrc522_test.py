# MRFC522 class
from mfrc522 import Mfrc522

def demo():
    from relay import Relay
    import time
    relay = Relay(2)
    relay.off()
    data = b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f"
    frc = Mfrc522()
    print("Checking Tag")
    print(frc.read())
    relay.on()
    time.sleep(1)
    relay.flip()
    relay.blink()
    print("Writting data to tag")
    print(frc.write(data))
    relay.stop_blink()
    time.sleep(1)
    relay.on()
    print("Check again")
    print(frc.read())
    time.sleep(1)
    relay.off()

if __name__ == "__main__":
    demo()
