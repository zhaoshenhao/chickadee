import enc

key = "1234567890123456"
e = enc.cipher(key)
d = enc.cipher(key)
plain = "asfadsfasljasldkasdlfkasdkfnlkjfasjlkdsf"
data = enc.encrypt(e, plain)
plain2 = enc.decrypt(d, data)
print(plain2)