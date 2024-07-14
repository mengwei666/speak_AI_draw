import pyaudio
import json
import threading
import time
import jwt
import requests
from flask import Flask, request, jsonify, render_template_string
from vosk import Model, KaldiRecognizer

# 加载Vosk模型，替换为解压后的模型路径
model = Model("vosk-model-cn-0.22")

# Flask应用
app = Flask(__name__)

# 全局变量，用于存储转录文本、图片URL、唤醒词和图片分辨率
transcriptions = []
image_url = None
wake_word = "你好"  # 默认唤醒词
image_resolution = {"height": 1080, "width": 2560}  # 默认图片分辨率为全屏

model_id = "artist-v5"

# API密钥和密钥
ak = "2F53088A9F984DB9AD94796FF7CF750F"  # 填写您的ak
sk = "019B94FFB2B54771A28545F1EC909C6E"  # 填写您的sk

# 生成JWT令牌
def encode_jwt_token(ak, sk):
    payload = {
        "iss": ak,
        "exp": int(time.time()) + 1800,
        "nbf": int(time.time()) - 5
    }
    token = jwt.encode(payload, sk, algorithm="HS256")
    return token

# 检测唤醒词的函数
def detect_wake_word(recognizer, audio_stream):
    while True:
        data = audio_stream.read(4000)
        if len(data) == 0:
            break
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            if "text" in result:
                print("检测到的文字:", result["text"])
                if wake_word in result["text"]:
                    print(f"唤醒词 '{wake_word}' 检测到!")
                    return True
    return False

# 将转录文本发送到API的函数
def send_to_api(text):
    global image_url, image_resolution, model_id
    print(f"发送数据到 API 时: {text}")

    authorization = encode_jwt_token(ak, sk)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {authorization}"
    }
    url = "https://api.sensenova.cn/v1/imgen/internal/generation_tasks"

    resolution = image_resolution

    payload = {
        "max_new_tokens": 1024,
        "model_id": model_id,
        "height": int(resolution["height"]),
        "width": int(resolution["width"]),
        "prompt": text,
        "n": 1,
        "repetition_penalty": 1.0,
        "stream": False,
        "temperature": 0.8,
        "top_p": 0.7,
    }
    print("payload: ", payload)

    response = requests.post(url, json=payload, headers=headers)
    response_json = response.json()
    print(f"response  {response}")
    print(f"response_json  {response_json}")

    if response.status_code == 200:
        task_id = response_json.get('task_id')
        while True:
            url_status = f"https://api.sensenova.cn/v1/imgen/internal/generation_tasks/{task_id}"
            response_status = requests.get(url_status, headers=headers)
            response_json_status = response_status.json()
            if response_status.status_code == 200:
                task_status = response_json_status.get('task', {}).get('state')
                result = response_json_status.get('task', {}).get('result', [])
                print(f"task_status {task_status}")

                if task_status in ['PENDING', 'RUNNING'] and result:
                    image_url = None  # 设置为None以显示加载动画
                    time.sleep(1)
                elif task_status == 'SUCCESS' and result:
                    image_url = result[0].get("raw")  # 获取生成指定分辨率的图片URL
                    print(f"result[0] {result[0]}")
                    print(f"image_url {image_url}")
                    break
            else:
                break

# 检测到唤醒词后继续转录的函数
def transcribe_after_wake_word(audio_stream, sample_rate):
    recognizer = KaldiRecognizer(model, sample_rate)
    print("开始录音...")
    
    global transcriptions
    transcriptions = []  # 用于保存所有转录结果
    
    while True:
        if detect_wake_word(recognizer, audio_stream):
            print("开始转录...")
            while True:
                data = audio_stream.read(4000)
                if len(data) == 0:
                    break
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    if "text" in result:
                        if result["text"]:
                            print("转录结果:", result["text"])
                            transcriptions.append(result["text"])
                            send_to_api(result["text"])
                            break

# 定义一个Flask路由来返回转录结果和图片URL
@app.route('/transcriptions', methods=['GET'])
def get_transcriptions():
    global transcriptions, image_url
    return jsonify(transcriptions=transcriptions, image_url=image_url)

# 更新设置的路由
@app.route('/update_settings', methods=['POST'])
def update_settings():
    global wake_word, image_resolution
    data = request.json
    wake_word = data.get('wakeWord', wake_word)
    image_resolution = {
        "height": data.get('imageHeight', image_resolution['height']),
        "width": data.get('imageWidth', image_resolution['width'])
    }
    model_id = data.get('modelId', model_id)  # 更新model_id
    print("wake_word image_resolution model_id", wake_word, image_resolution, model_id)
    return jsonify(success=True, wake_word=wake_word, image_resolution=image_resolution, model_id=model_id)




@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>实时转录</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                overflow: hidden; /* 隐藏滚动条 */
                height: 100vh; /* 全屏高度 */
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                background-color: #f0f0f0; /* 背景颜色 */
            }

            #settings {
                position: absolute; /* 绝对定位 */
                top: 20px;
                left: 20px;
                z-index: 3; /* 确保在最上层 */
                background: rgba(255, 255, 255, 0.8); /* 半透明背景 */
                border-radius: 10px; /* 圆角 */
                padding: 10px;
            }

            #loader {
                display: none; /* 默认隐藏 */
                animation: pulse 1.5s infinite; /* 渐变效果 */
                width: 100vw; /* 全屏宽度 */
                height: 100vh; /* 全屏高度 */
                background-size: cover; /* 背景填充 */
                background-position: center; /* 背景居中 */
                z-index: 1; /* 在最上层 */
                transform: rotate(90deg); /* 添加旋转90度的样式 */
            }

            @keyframes pulse {
                0% {
                    opacity: 0.7; /* 初始透明度 */
                }
                50% {
                    opacity: 1; /* 中间透明度 */
                }
                100% {
                    opacity: 0.7; /* 恢复透明度 */
                }
            }

            #image {
                display: none; /* 默认隐藏 */
                max-width: 100vw; /* 最大宽度适应屏幕宽度 */
                height: auto; /* 高度自动，根据原始比例调整 */
                width: auto; /* 宽度自动，根据原始比例调整 */
                object-fit: contain; /* 保持宽高比，不裁剪图片 */
                z-index: 0; /* 在下层 */
                transform: rotate(90deg); /* 添加旋转90度的样式 */
            }

            #transcriptions {
                position: relative;
                z-index: 2; /* 确保在最上层 */
                padding: 20px;
                background: rgba(255, 255, 255, 0.8); /* 半透明背景 */
                border-radius: 10px; /* 圆角 */
            }
        </style>
    </head>
    <body>
        <div id="settings">
            <label for="modelId">模型ID:</label>
            <input type="text" id="modelId" value="artist-v5">
            <label for="wakeWord">唤醒词:</label>
            <input type="text" id="wakeWord" value="你好">
            <br>
            <label for="imageWidth">图片宽度:</label>
            <input type="number" id="imageWidth" value="2560">
            <br>
            <label for="imageHeight">图片高度:</label>
            <input type="number" id="imageHeight" value="1080">
        </div>
        <h1 id="title">实时转录结果</h1>
        <div id="transcriptions"></div>
        <h2 id="image-title">生成的图片</h2>
        <div id="loader" style="background-image: url('');"></div>
        <img id="image" src="" alt="生成的图片">
        
        <script>
            let currentImageUrl = ''; // 存储当前图片URL
            let currentImageWidth = 2560; // 默认图片宽度
            let currentImageHeight = 1080; // 默认图片高度
                                  
            function init() {
                document.getElementById('title').style.display = 'none'; // 隐藏标题
                document.getElementById('image-title').style.display = 'none'; // 隐藏生成的图片标题
                document.getElementById('transcriptions').style.display = 'none'; // 隐藏转录结果
            }

            window.onload = init;

            function fetchTranscriptions() {
                fetch('/transcriptions')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('transcriptions').innerHTML = data.transcriptions.join('<br>');
                    if (data.image_url) {
                        currentImageUrl = data.image_url; // 更新当前图片URL
                        const image = document.getElementById('image');
                        image.style.display = 'none'; // 隐藏图片

                        document.getElementById('loader').style.display = 'block'; // 显示加载器
                        image.onload = function() {
                            document.getElementById('loader').style.display = 'none'; // 隐藏加载器
                            image.style.display = 'block'; // 显示图片
                        };
                        image.src = currentImageUrl;
                    } else {
                        document.getElementById('loader').style.backgroundImage = `url(${currentImageUrl})`;
                        document.getElementById('loader').style.display = 'block';
                        document.getElementById('image').style.display = 'none';
                    }
                })
                .catch(error => console.error('Error:', error));
            }

            document.getElementById('wakeWord').addEventListener('change', function() {
                const wakeWord = this.value;
                const imageWidth = document.getElementById('imageWidth').value;
                const imageHeight = document.getElementById('imageHeight').value;
                updateSettings(wakeWord, imageWidth, imageHeight);
            });

            document.getElementById('imageWidth').addEventListener('change', function() {
                const wakeWord = document.getElementById('wakeWord').value;
                const imageWidth = this.value;
                const imageHeight = document.getElementById('imageHeight').value;
                currentImageWidth = imageWidth; // 更新当前宽度
                updateSettings(wakeWord, imageWidth, imageHeight);
            });

            document.getElementById('imageHeight').addEventListener('change', function() {
                const wakeWord = document.getElementById('wakeWord').value;
                const imageWidth = document.getElementById('imageWidth').value;
                const imageHeight = this.value;
                currentImageHeight = imageHeight; // 更新当前高度
                updateSettings(wakeWord, imageWidth, imageHeight);
            });

            function updateSettings(wakeWord, imageWidth, imageHeight) {
                fetch('/update_settings', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ wakeWord, imageWidth, imageHeight }),
                })
                .then(response => response.json())
                .then(data => {
                    console.log('设置已更新:', data);
                })
                .catch(error => console.error('更新设置时出错:', error));
            }

            setInterval(fetchTranscriptions, 1000);  // 每秒刷新一次
        </script>
    </body>
    </html>
    ''')











def start_flask_app():
    app.run(debug=True, use_reloader=False)

def start_audio_detection():
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    audio = pyaudio.PyAudio()

    # 打开麦克风流
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)

    try:
        transcribe_after_wake_word(stream, RATE)
    except KeyboardInterrupt:
        pass
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()

if __name__ == "__main__":
    flask_thread = threading.Thread(target=start_flask_app)
    audio_thread = threading.Thread(target=start_audio_detection)
    
    flask_thread.start()
    audio_thread.start()
    
    flask_thread.join()
    audio_thread.join()
