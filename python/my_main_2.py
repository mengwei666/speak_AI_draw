import time
import jwt
import requests
from flask import Flask, request, render_template, jsonify

app = Flask(__name__)

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_image():
    prompt = request.form['prompt']
    print(f"prompt {prompt}")

    authorization = encode_jwt_token(ak, sk)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {authorization}"
    }
    url = "https://api.sensenova.cn/v1/imgen/internal/generation_tasks"
    
    payload = {
        "max_new_tokens": 1024,
        "model_id": "artist-v5",
        "prompt": prompt,
        "n": 1,
        "repetition_penalty": 1.0,
        "stream": False,
        "temperature": 0.8,
        "top_p": 0.7,
    }

    response = requests.post(url, json=payload, headers=headers)
    response_json = response.json()
    print(f"response  {response}")
    print(f"response_json  {response_json}")

    if response.status_code == 200:
        task_id = response_json.get('task_id')
        return jsonify(task_id=task_id)
    else:
        return jsonify(error="Failed to create generation task"), 400

@app.route('/status/<task_id>')
def check_task_status(task_id):
    authorization = encode_jwt_token(ak, sk)
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {authorization}"
    }
    url = f"https://api.sensenova.cn/v1/imgen/internal/generation_tasks/{task_id}"

    response = requests.get(url, headers=headers)
    response_json = response.json()
    print(f"Task  {response_json}")

    if response.status_code == 200:
        task_status = response_json.get('task', {}).get('state')
        result = response_json.get('task', {}).get('result', [])
        print(f"task_status {task_status}")

        if task_status == 'PENDING' and result:
            image_url = result[0].get('small')  # 获取生成的小尺寸图片URL
            print(f"image_url {image_url}")
            return jsonify(status="pending", image_url=image_url)
        
        elif task_status == 'RUNNING' and result:
            image_url = result[0].get('small')  # 获取生成的小尺寸图片URL
            print(f"image_url {image_url}")
            return jsonify(status="running", image_url=image_url)
        
        elif task_status == 'SUCCESS' and result:
            image_url = result[0].get('small')  # 获取生成的小尺寸图片URL
            print(f"image_url {image_url}")
            return jsonify(status="success", image_url=image_url)
        else:
            return jsonify(status="processing")
    else:
        return jsonify(status="error", message="Failed to fetch task status"), 400

if __name__ == "__main__":
    app.run(debug=True)
