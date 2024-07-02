# from flask import Flask, render_template, request, jsonify
# import threading
# import time
# import requests

# app = Flask(__name__)


# API_URL = "https://api.sensenova.cn/v1/llm/chat-completions"
# API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIyRjUzMDg4QTlGOTg0REI5QUQ5NDc5NkZGN0NGNzUwRiIsImV4cCI6MTcxOTY2NTU2MiwibmJmIjoxNzE5NjYzNzU3fQ.XadaIf2TL43Zi6iyJxHyHjBnlGU8y1hGFLLPKUYPJ14"

# # 全局变量，用于控制定时打印任务的运行状态
# print_task_running = False

# def print_task():
#     global print_task_running
#     while print_task_running:

#         # 准备请求数据
#         payload = {
#             "model": "SenseMirage",
#             "messages": [
#                 {
#                     "role": "user",
#                     "content": [
#                         {
#                             "type": "image_url", 
#                             "image_url": "string"
#                         },
#                         {
#                             "type": "text",
#                             "text": "端午节油画风格"
#                         }
#                     ]
#                 }
#             ],
#             "max_new_tokens": 1024, 
#             "repetition_penalty": 1.0, 
#             "stream": False,
#             "temperature": 0.8,
#             "top_p": 0.7,
#             "user": "string"    

#         }
#         headers = {
#             "Content-Type": "application/json",
#             "Authorization": f"Bearer {API_TOKEN}"
#         }

#         # 发送请求并打印响应
#         response = requests.post(API_URL, json=payload, headers=headers)
#         print(response.json())






#         print("定时打印内容")
#         time.sleep(5)  # 每隔5秒打印一次

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/start_printing', methods=['POST'])
# def start_printing():
#     global print_task_running
#     if not print_task_running:
#         print_task_running = True
#         threading.Thread(target=print_task).start()
#     return jsonify({"status": "started"})

# @app.route('/stop_printing', methods=['POST'])
# def stop_printing():
#     global print_task_running
#     print_task_running = False
#     return jsonify({"status": "stopped"})

# if __name__ == '__main__':
#     app.run(debug=True)






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
    # print(f"Generated JWT Token: {authorization}")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {authorization}"
    }
    url = "https://api.sensenova.cn/v1/llm/chat-completions"
    
    payload = {
        "model": "SenseChat-Vision",
        "messages": [
            {
                "role": "user",
                "content": [
                    # {"type": "image_url", "image_url": "string"},
                    {"type": "text", "text": "Hello, how are you?"}
                ]
            }
        ],
        "max_new_tokens": 150,
        "repetition_penalty": 1.0,
        "stream": False,
        "temperature": 0.8,
        "top_p": 0.7,
    }

    # print(f"Request URL: {url}")
    # print(f"Request Headers: {headers}")
    # print(f"Request Payload: {payload}")

    response = requests.post(url, json=payload, headers=headers)
    # print(f"Response Status Code: {response.status_code}")
    print(f"Response Content: {response.json()}")

if __name__ == "__main__":
    send_request_and_print()

