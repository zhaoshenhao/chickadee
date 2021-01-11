from pir import Pir
import time

ON = 0
OFF = not ON

def demo():
    pir = Pir(22)

    def hi(arg):
        print("-------------------Hi", arg)

    pir.handler = hi
    pir.enable()
    time.sleep(20)
    pir.handler = None

if __name__ == "__main__":
    demo()
