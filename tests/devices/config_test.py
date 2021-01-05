from config import Config

def demo():
    c = Config()
    cfg = c.load()
    print(c.ntphost)
    print(cfg)
    c2 = Config()
    print(c2.__config)

if __name__ == "__main__":
    demo()