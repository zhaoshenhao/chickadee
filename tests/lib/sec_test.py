from sec import Sec
from op import request, result
import dev

st = Sec("1234567890123456", "12345678")

req = request('sys', 'get', {'a': 'a', 'b': 1, 'c': True})
ret = result(200, 'test', v={'alert': 1, 'n': 'pir'})

print("Test request")
print("1: %r" % req)
p = st.enc_paylaod(req)
print("2: %r" % p)
d = st.dec_payload(p)
print("3: %r" % d)

print("Test result")
print("1: %r" % ret)
p = st.enc_paylaod(ret)
print("2: %r" % p)
d = st.dec_payload(p)
print("3: %r" % d)


print("Test token 1")
t = st.create_token(True)
print("Special token: %s" % t)
print("Verify %s" % str(st.check_token(t)))
print("Set state = 2")
dev.state = 2
print("Verify %s" % str(st.check_token(t)))

print("Test token 2")
t = st.create_token()
print("Special token: %s" % t)
print("Verify %s" % str(st.check_token(t)))
