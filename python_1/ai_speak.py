import pyaudio
import wave
import json
from vosk import Model, KaldiRecognizer

# 加载Vosk模型，替换为解压后的模型路径
model = Model("vosk-model-cn-0.22")

def detect_wake_word(recognizer, audio_stream, sample_rate, wake_word="你好"):
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



def send_to_api(text):
    print(f"发送数据到 API 时")

def transcribe_after_wake_word(audio_stream, sample_rate):
    rec = KaldiRecognizer(model, sample_rate)
    print("开始录音...")

    all_transcriptions = []  # 用于保存所有转录结果
    
    while True:
        if detect_wake_word(rec, audio_stream, sample_rate):
            # 开始继续录音和转录
            print("开始转录...")
            while True:
                data = audio_stream.read(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    if "text" in result:
                        if result["text"]:
                            print("转录结果:", result["text"])
                             # 将转录结果添加到列表中
                            all_transcriptions.append(result["text"])
                        else:
                            print("未检测到转录结果。")
                            # 将所有转录结果合并为一个文本字符串并打印
                            combined_text = "\n".join(all_transcriptions)
                            print("所有转录结果:")
                            print(combined_text)

                             # 发送合并后的文本到 API
                            send_to_api(combined_text)
                            break


            

if __name__ == "__main__":
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
