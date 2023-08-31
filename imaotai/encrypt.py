from Crypto.Cipher import AES
import base64

PRIVATE_KEY = """
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDHpyKBkBkoRStJ
8bFuQ/06gM+FQ77ssy4v7Te2g6Xi8AJNbcrt9s05wktZU6N9jILza8pWLkemIbLO
6rOHhBtaUiaw0FNnA2mwWjKopBRubsqmJ1lORP6XE/azBaarJS3gV6kOoYytw6XF
/LYDTXskRnIibobpyk8mFQBGqS6HYQdn9GEJPsPMbvCO8RA7YCk0Ol2qN844ECWk
jEg91rgCGVlyOOhi4NTPSs6wTYW7hdur6FIn4+H0iFLwC2pePtZmh/T7z2Mb7Hk4
qw+sVua4MFfaJXSBH1aur/nI7uplNdXTB9ICOZjS2Y+VrGabFLsIYPWMORDoH+7f 
R08aKT/FAgMBAAECggEAKZScciFhq+pj7p2Al3dfeNy024tVaxSSLPcZoFBgrxfP
UvLnzZGWAk59xNfPd+lYqHutgy9WSro/9CobQ8D2tWPgnPh2NkEWtNzEKi0p+Cno
2JvfVJa38xz8RyKJKKGwoUWAdwScOOBDWS2ddqifWdm2EYe1X2F8BHFhQlYf05+6
N7hm6cbRt9C5Etm6YkSqOhUWbxdFN5VDcYDLKJxj4i6kWOX5hcExOimq8pvJ6jl9
ijtiHou1UMDfZ/gNnG4+yQRGhdPgeTeh9Sdlzj4YfdtGPPymxRa7NNm+4XO3+8Fm
o0nYIHtZTrhSFTrJ7+UE93pDvSrI5rNHgLJnnmhrrQKBgQDyL005SDUQ/wjJqV/z
u1QmpZ0kcRXSqbHjpRTccDO6VC2dX/Im3AUMAlUw4oVXA4uwvwNCM0do4+OefXtr
EOKsku1XEsjaxkpi24Qb+LUhk6TAMulkvlHb9MTk4Asa5i3X0IJnGtUejKWiy/qU
kXRXlJwAXFekZobDjzDu0priRwKBgQDTCroMpfpiYjggfX5oQWt8vPRHawd0uOqb
rKxbU/TewkLdaMqj0otNjHDg44Gc30NqAcC5t4uJ9JmF+SWHEUTFSi2PQopJmBVg
fcyy9n+tP6Id1BUI9RjCoCrRx0lnQq+k8ZNTo+/p0IjzCsLsOhLvBlL0fCa1AfXu
rN/1ivunkwKBgQCOwqNa6N2fLzcW6OjO29Y3EdkX6jFbBPz/nAg4CUv0wjpBUpWD
op62/YkKT/0Z1dU6Ut6w31lw0yUSABYIfuOfptyRP1l23PxsWcn+UxUyvb2YLmq2
IBpQ9nA6GndxW84aMacs7/xBDdd1p5gGi9dw6QEslUJ0fptiG75UiYETcQKBgB+O
0xNhHnfnyAzTtztPzQryFnU3g/3oSOzOfVeKzmshEW6aZPLqYPpPrfFzE8apfCM1
7+PVloAim3J1Ny9jXa1C0l1BzfwDSe8L4LhCNAVsJonfVOXqALHZ0Y1dB5TxW+KG
XUl8kjuce14cldlNNdeYUn9MsV0P1f7Cyxqklc0RAoGATNbWT+j6uoTltEpN0JdH
DiLL9RWyJYhG0u5eKxHKb+Hqb6YSQqAZ39zP5reMoi2f9ijmjPe1hExpqGU3QjeO
bctyS5VPSk+YtimNKaJJSbIN9OUKbbxThf+0iLoafsgpCPsoTuxCXB4W1wDq7Afw
ZWdIIX8Wvll5ciIXkaTIQGQ=
"""

PREFIX = "lpe0x9die8*jd92="

aLpe0x9die8Jd92 = f"{PREFIX}{PRIVATE_KEY}".encode()


def get_seed(string: str) -> str:
    arr = string.encode()
    str_c_len = len(arr)
    v10 = [0] * 16

    for v4 in range(16):
        v8 = v10[v4]
        if v4 < str_c_len:
            v8 = arr[v4]
        v10[v4] = v8 | aLpe0x9die8Jd92[v4]

    return ''.join([chr(v) for v in v10])


class Encrypt:
    def __init__(self, key, iv):
        self.key = key.encode('utf-8')
        self.iv = iv.encode('utf-8')
        self.coding = ""

    # @staticmethod
    def pkcs7padding(self, text):
        """明文使用PKCS7填充 """
        bs = 16
        length = len(text)
        bytes_length = len(text.encode('utf-8'))
        padding_size = length if (bytes_length == length) else bytes_length
        padding = bs - padding_size % bs
        padding_text = chr(padding) * padding
        self.coding = chr(padding)
        return text + padding_text

    def aes_encrypt(self, content):
        """ AES加密 """
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        # 处理明文
        content_padding = self.pkcs7padding(content)
        # 加密
        encrypt_bytes = cipher.encrypt(content_padding.encode('utf-8'))
        # 重新编码
        result = str(base64.b64encode(encrypt_bytes), encoding='utf-8')
        return result

    def aes_decrypt(self, content):
        """AES解密 """
        cipher = AES.new(self.key, AES.MODE_CBC, self.iv)
        content = base64.b64decode(content)
        text = cipher.decrypt(content).decode('utf-8')
        return text.rstrip(self.coding)

if __name__ == '__main__':
#     key = 'ONxYDyNaCoyTzsp83JoQ3YYuMPHxk3j7'
#     iv = 'yNaCoyTzsp83JoQ3'
#
#     ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
#     p_json = {
#         "CompanyName": "testmall",
#         "UserId": "test",
#         "Password": "grasp@101",
#         "TimeStamp": "2019-05-05 10:59:26"
#     }
#     a = Encrypt(key=key, iv=iv)
#     e = a.aes_encrypt(json.dumps(p_json))
#     d = a.aes_decrypt(e)
#     print("加密:", e)
#     print("解密:", d)

    print(get_seed("sadfsadfasdfasdfasdfaasdfasdfasdf"))
    pass
