from sec import Sec

st = Sec("kB8nd4GLzz2ACrWZhCLiq4ImGjDpRkiz", "12345678")
p1 = {"_": "npbrNOssxJvxu9Nb6x/+5O/rVFmtn4luFve48iDNKeGIwJjEMi3SqA8RYHSd3M0Y7py1KkHhEJV4Xzv0fru8wPo1gttaumudzZ/QSm9q3l+EsOIDzgr+HPJhHcrU7dCqZXDgybrY+I6ODu/xsvuhuA==", "i": "ybb-switch-fcf5c429b4bc"}
p2 = {"_": "BZRqwde0T3AGUwM/sB89VnUsa8+12qfB39V6pnGj3hIzohKzDbMn1bhJhLMsJnGDFDU8jswQRQCBWw0lacDzmtgMe8DRYuIxFaunHEzoSVWo4Z6QWHIIu32lvipOrErQ0ivs1rtEaRyH6xFFg0so/g=="}
print(st.dec_payload(p1))
print(st.dec_payload(p2))
