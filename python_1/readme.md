# 2024.07.02

> 最新接口文档的地址如下
> https://docs.google.com/document/d/1fecHRD-sMooUnnUe4H0SL9b5EB-6OHMjfZjxkvhUD5o/edit?usp=sharing
> 如果谷歌文档无法打开，可使用飞书文档
> https://p87mj0ne7k.feishu.cn/docx/ElrEdkpQbooXwgxF5x8c6Il3nBe?from=from_copylink

# 2024.07.11

> 测试麦克风是否正常连接工作
>
> ### 1. 使用 `arecord` 命令
>
> `arecord` 是一个简单的命令行工具，用于录制音频。您可以使用它来列出可用的音频设备并测试麦克风。
>
> `arecord -l`
>
> 这将列出所有可用的录音设备。如果麦克风连接正确，您应该会在输出中看到它。
>
> card 0: AudioPCI [Ensoniq AudioPCI], device 0: ES1371/1 [ES1371 DAC2/ADC]
> 子设备: 1/1
> 子设备 #0: subdevice #0
> card 1: Device [USB PnP Sound Device], device 0: USB Audio [USB Audio]
> 子设备: 1/1
> 子设备 #0: subdevice #0
>
> 要测试连接的USB麦克风，您可以使用以下命令：
>
> `arecord -D plughw:1,0 -d 5 test.wav`
>
> 解释：
>
> * `-D plughw:1,0`：指定要使用的音频设备。`1,0`表示card 1, device 0。
> * `-d 5`：录制5秒。
>
> 录制完成后，使用以下命令播放音频：
>
> aplay test.wav
>
> 您还可以使用 `pavucontrol`来确认麦克风的输入音量：
>
> sudo apt install pavucontrol
> pavucontrol

# 2024.07.14

> transform: rotate(90deg); /* 添加旋转90度的样式 */
>
> artist-v5
>
> sgl_artist_v0.4.0
>
>
>     loader.style.display = 'none'; // 隐藏加载器
>
>     const image = document.getElementById('image');
>
>     image.style.display = 'block'; // 显示图片
>
>     image.src = currentImageUrl;


使用现有音频文件进行本地测试
以下是完整的程序示例，使用本地的pocketsphinx库进行语音识别：

安装依赖库
首先安装pocketsphinx库：

bash
复制代码
pip install pocketsphinx









使用 Vosk 本地语音识别
安装Vosk
bash
复制代码
pip install vosk
下载Vosk中文模型
下载模型文件并解压：Vosk 模型下载链接

wget https://alphacephei.com/vosk/models/vosk-model-cn-0.22.zip


这个错误表明您的Python环境中缺少了vosk模块。请按照以下步骤检查和安装vosk模块：

步骤 1: 确保pip安装
首先，请确保您使用的是正确的pip命令进行安装。有时候，特定的Python环境可能需要使用pip3来安装Python 3.x的模块。

bash
复制代码
pip install vosk



