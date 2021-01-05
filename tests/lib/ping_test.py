from uping import ping, ping_check

def demo():
    r = ping('192.168.0.1', quiet=True)
    print(r)
    r = ping('8.8.8.8', quiet=True)
    print(r)
    print(ping_check('8.8.8.8'))

if __name__ == "__main__":
    demo()
