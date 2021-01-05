import dh

def demo():
    import time
    d1 = dh.DiffieHellman(2)
    d2 = dh.DiffieHellman(2)
    start = time.time()
    print("start: ", start)
    d1_pubkey = d1.gen_public_key()
    g1 = time.time()
    print("g1: ", g1-start)
    d2_pubkey = d2.gen_public_key()
    g2 = time.time()
    print("g2: ", g2-g1)

    d1_sharedkey = d1.gen_shared_key(d2_pubkey)
    s1 = time.time()
    print("s1: ", s1-g2)

    d2_sharedkey = d2.gen_shared_key(d1_pubkey)
    s2 = time.time()
    print("s2: ", s2-s1)
    print(d1_sharedkey == d2_sharedkey)
    print(d1_pubkey)
    print(d2_pubkey)
    print(d1_sharedkey)
    print(len(d1_sharedkey))

if __name__ == "__main__":
    demo()
