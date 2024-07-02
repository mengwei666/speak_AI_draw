import time
import jwt
import requests

ak = "2F53088A9F984DB9AD94796FF7CF750F"  # 填写您的ak
sk = "019B94FFB2B54771A28545F1EC909C6E"  # 填写您的sk

def encode_jwt_token(ak, sk):
    payload = {
        "iss": ak,
        "exp": int(time.time()) + 1800,  # 填写您期望的有效时间，此处示例代表当前时间+30分钟
        "nbf": int(time.time()) - 5      # 填写您期望的生效时间，此处示例代表当前时间-5秒
    }
    token = jwt.encode(payload, sk, algorithm="HS256")

    print("------------------------------------------")
    print(token)
    print("------------------------------------------")

    return token

def send_request_and_print():
    authorization = encode_jwt_token(ak, sk)
    headers = {
        "Authorization": f"Bearer {authorization}",
        "Content-Type": "application/json"
    }
    url = "https://api.sensenova.cn/v1/imgen/models"
    response = requests.get(url, headers=headers)
    print(response.json())

if __name__ == "__main__":
    send_request_and_print()
