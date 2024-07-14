import pyaudio
import json
import threading
from flask import Flask, request, jsonify, render_template_string
from vosk import Model, KaldiRecognizer

# 加载Vosk模型，替换为解压后的模型路径
model = Model("vosk-model-cn-0.22")

app = Flask(__name__)

# 全局变量，用于存储转录文本
transcriptions = []

# 检测唤醒词的函数。
# 参数：
# 	  recognizer: KaldiRecognizer 对象，用于识别音频数据。
#     audio_stream: PyAudio Stream 对象，用于读取音频数据。
#     wake_word: 需要检测的唤醒词，默认为 "你好"。
# 返回：
# 	  如果检测到唤醒词，返回 True；否则返回 False。
def detect_wake_word(recognizer, audio_stream, wake_word="你好"):
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

# 将转录文本发送到API的函数。
# 参数：
#    text: 要发送的文本。
def send_to_api(text):
    print(f"发送数据到 API 时: {text}")

# 检测到唤醒词后继续转录的函数。
# 参数：
#    audio_stream: PyAudio Stream 对象，用于读取音频数据。
#    sample_rate: 音频采样率。
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
                        else:
                            combined_text = "\n".join(transcriptions)
                            send_to_api(combined_text)
                            break

# 定义一个Flask路由来返回转录结果
@app.route('/transcriptions', methods=['GET'])
def get_transcriptions():
    global transcriptions
    return jsonify(transcriptions)

# 定义一个Flask路由来返回主页
@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>实时转录</title>
    </head>
    <body>
        <h1>实时转录结果</h1>
        <div id="transcriptions"></div>
        
        <script>
            function fetchTranscriptions() {
                fetch('/transcriptions')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('transcriptions').innerHTML = data.join('<br>');
                })
                .catch(error => console.error('Error:', error));
            }
            
            setInterval(fetchTranscriptions, 1000);  // 每秒刷新一次
        </script>
    </body>
    </html>
    ''')

def start_flask_app():
    app.run(debug=True, use_reloader=False)

def start_audio_detection():
    # 录音参数
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
        # 停止并关闭流
        stream.stop_stream()
        stream.close()
        audio.terminate()

if __name__ == "__main__":
    # 创建两个线程，一个运行Flask应用，另一个进行音频检测
    flask_thread = threading.Thread(target=start_flask_app)
    audio_thread = threading.Thread(target=start_audio_detection)
    
    # 启动线程
    flask_thread.start()
    audio_thread.start()
    
    # 等待线程结束
    flask_thread.join()
    audio_thread.join()
