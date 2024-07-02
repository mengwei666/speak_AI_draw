import time
import jwt

ak = "2F53088A9F984DB9AD94796FF7CF750F" # 填写您的ak
sk = "019B94FFB2B54771A28545F1EC909C6E" # 填写您的sk

def encode_jwt_token(ak, sk):
    headers = {
        "alg": "HS256",
        "typ": "JWT"
    }
    payload = {
        "iss": ak,
        "exp": int(time.time()) + 1800, # 填写您期望的有效时间，此处示例代表当前时间+30分钟
        "nbf": int(time.time()) - 5 # 填写您期望的生效时间，此处示例代表当前时间-5秒
    }
    token = jwt.encode(payload, sk, headers=headers)
    return token

authorization = encode_jwt_token(ak, sk)
print(authorization) # 打印生成的API_TOKEN
