from sec import Sec
from op import request, result
import dev

st = Sec("", "12345678")

req = request('sys/info', 'get', {'a': 'a', 'b': 1, 'c': True})
req['t'] = 'get-tm1'
req2 = request('sys/echo', 'set', 'Hi2')
ret = result(200, 'test', v={'alert': 1, 'n': 'pir'})
req2['t'] = 'get-tm1'

print("Test request")
print("1: %r" % req)
p = st.enc_paylaod(req)
print("2: %r" % p)
d = st.dec_payload(p)
print("3: %r" % d)

print("Test request2")
print("1: %r" % req2)
p = st.enc_paylaod(req2)
print("2: %r" % p)
d = st.dec_payload(p)
print("3: %r" % d)

print("Test result")
print("1: %r" % ret)
p = st.enc_paylaod(ret)
print("2: %r" % p)
d = st.dec_payload(p)
print("3: %r" % d)

t1 = 'abcd:qpU6bYHAdqV9rVNCG1l6RSfcrDqVui19HhHMq92VrMM='
t2 = 'abcd:kvRCIid6W5E7WT7bL9Cih2djOml1bbltk+kah7qoo7U=:1611094134'
#t1 = 'abcd:GbL7k5tYkk3P3jLhdtE63Xh7nzmhSZbE6ZeBoOk643c='
#t2 = 'abcd:lrdUVKznVWqR/yQX03Px2wZvhb58simNK4jk2aK3cEk=:1611095471'

print("\n\nTest token 1")
t = st.create_token(True)
print("Special token: %s" % t)
print("Verify %s" % str(st.check_token(t)))
print("Verify ext t1: %s, result: %r" % (t1, st.check_token(t1)))
print("Set state = 2")
dev.state = 2
print("Verify %s" % str(st.check_token(t)))
print("Verify ext t1: %s, result: %r" % (t1, st.check_token(t1)))

print("\nTest token 2")
t = st.create_token()
print("Normal token: %s" % t)
print("Verify %s" % str(st.check_token(t)))
print("Verify %s" % str(st.check_token(t)))
print("Verify ext t2: %s, result: %r" % (t1, st.check_token(t2)))
