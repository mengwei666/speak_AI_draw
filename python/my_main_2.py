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
    return token

def send_request_and_print():
    authorization = encode_jwt_token(ak, sk)
    print(f"Generated JWT Token: {authorization}")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {authorization}"
    }
    url = "https://api.sensenova.cn/v1/llm/chat-completions"
    
    payload = {
        "max_new_tokens": 1024,
        "messages": [
            {
                "content": "Hello, how can I assist you today?",  # 假设的有效内容
                "role": "user"  # 假设的有效角色
            }
        ],
        "model": "sgl_artist_v0.3.5_0925",  # 假设的有效模型名称
        "n": 1,
        "repetition_penalty": 1.0,
        "stream": False,
        "temperature": 0.8,
        "top_p": 0.7,
        "user": "user_123",  # 假设的有效用户ID
    }

    print(f"Request URL: {url}")
    print(f"Request Headers: {headers}")
    print(f"Request Payload: {payload}")

    response = requests.post(url, json=payload, headers=headers)
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Content: {response.json()}")

if __name__ == "__main__":
    send_request_and_print()