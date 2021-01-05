from pir import Pir
import time

ON = 0
OFF = not ON

def demo():
    pir = Pir(22)

    def hi(arg):
        print("-------------------Hi", arg)

    pir.set_handler(hi)
    time.sleep(20)
    pir.remove_handler()

if __name__ == "__main__":
    demo()
