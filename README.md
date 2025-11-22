# 🎧 Voice Assistant

本项目实现一个本地运行的 AI 语音对话助手，集成以下模块：
- Whisper (语音识别)
- Ollama + Mistral (大模型对话)
- Coqui TTS (语音合成)
- Gradio (网页UI)

## 🧩 功能流程
🎙️ 语音输入 → 🧠 Whisper 转文字 → 💬 LLM 回复 → 🔊 TTS 合成语音

## 🚀 快速启动

1️⃣ 安装依赖：
```bash
pip install -r requirements.txt
```

2️⃣ 启动 Ollama 并下载模型：
```bash
ollama pull mistral
ollama serve
```

3️⃣ 运行应用：
```bash
python main.py
```

浏览器打开 http://127.0.0.1:7860 即可使用。

## 🎛️ 可选参数
- 可在 `main.py` 中修改 speaker 选择不同性别或口音。

## ⚙️ 系统要求

- **操作系统**: Windows 11
- **Python 版本**: 3.10
- **内存**: 32GB
- **显卡**: NVIDIA GeForce RTX 4070 (12GB 显存)
- **额外依赖**: 如果未安装 Visual Studio 的 C++ 工具，请前往 [Visual Studio 下载页面](https://visualstudio.microsoft.com/) 安装 "Desktop development with C++" 工作负载。

## 🛠️ GPU 支持

如果未识别到 GPU，请根据提示重新安装以下库：
```bash
pip uninstall torch torchvision torchaudio -y
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```
