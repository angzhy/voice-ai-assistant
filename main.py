import gradio as gr
from faster_whisper import WhisperModel
from TTS.api import TTS
import requests
import os
import json

# -----------------------------
# 模型配置
# -----------------------------
STT_MODEL = "large-v3"
TTS_MODEL = "tts_models/en/vctk/vits"
LLM_API = "http://localhost:11434/api/chat"
DEFAULT_SPEAKER = "p225"
SPEAKERS = ["p225", "p226", "p248", "p249"]

# -----------------------------
# 初始化
# -----------------------------
print("加载 Whisper 模型...")
whisper = WhisperModel(STT_MODEL, device="cuda")

print("加载 TTS 模型...")
tts = TTS(TTS_MODEL)
tts.to("cuda")

# -----------------------------
# 主逻辑
# -----------------------------
def process_audio(audio, speaker, dual_output, speed):
    if audio is None:
        return "请先录音。", None, None

    os.makedirs("audio", exist_ok=True)
    input_path = "audio/input.wav"
    en_path = "audio/reply_en.wav"
    cn_path = "audio/reply_cn.wav"

    # 保存录音
    if isinstance(audio, str):
        input_path = audio
    else:
        audio[1].export(input_path, format="wav")

    # Whisper 语音转文字
    segments, _ = whisper.transcribe(input_path)
    text_in = " ".join([s.text for s in segments])

    # 构建 Prompt
    prompt = f"""
你是一个双语助手，请用中英文回答问题。
请严格以 JSON 格式输出，不要输出其他内容。

问题：{text_in}

输出格式如下：
{{
  "chinese": "中文回答内容",
  "english": "英文翻译内容"
}}
"""

    # 调用本地 Mistral LLM
    payload = {"model": "mistral", "messages": [{"role": "user", "content": prompt}]}

    cn_text = ""
    en_text = ""
    try:
        response = requests.post(LLM_API, json=payload)
        response.raise_for_status()
        # 如果返回是逐行流
        try:
            reply_lines = response.json()
        except Exception:
            reply_lines = response.text.splitlines()

        # 拼接 content
        all_content = ""
        for line in reply_lines:
            try:
                line_json = json.loads(line)
                if "message" in line_json and "content" in line_json["message"]:
                    all_content += line_json["message"]["content"]
            except Exception:
                continue

        # 解析最终 JSON
        try:
            reply_json = json.loads(all_content)
            cn_text = reply_json.get("chinese", "").strip()
            en_text = reply_json.get("english", "").strip()
        except Exception:
            # 如果无法解析 JSON，直接把拼接后的内容当英文
            en_text = all_content.strip()

    except Exception as e:
        print(f"❌ LLM 调用错误: {e}")
        en_text = "LLM 返回异常。"

    # 生成英文语音
    if en_text:
        tts.tts_to_file(text=en_text, speaker=speaker, file_path=en_path, speed=speed)

    # 生成中文语音（如果选择了 dual_output）
    if dual_output and cn_text:
        tts.tts_to_file(text=cn_text, speaker=speaker, file_path=cn_path, speed=speed)
        return f"🗣️ 你说: {text_in}\n\n🤖 中文: {cn_text}\n\n💬 English: {en_text}", en_path, cn_path
    else:
        return f"🗣️ 你说: {text_in}\n\n💬 English: {en_text}", en_path, None

# -----------------------------
# Gradio UI
# -----------------------------
def build_ui():
    with gr.Blocks() as demo:
        gr.Markdown("## 🎧 本地语音对话 AI 助手（中英双语版）")

        with gr.Row():
            audio_input = gr.Audio(sources=["microphone"], type="filepath", label="🎙️ 录音输入")
            speaker_choice = gr.Dropdown(SPEAKERS, value=DEFAULT_SPEAKER, label="🔊 声音选择")
            dual_output = gr.Checkbox(label="🎵 同时输出中文和英文", value=False)
            speed_slider = gr.Slider(minimum=0.6, maximum=1.2, step=0.05, value=1.0, label="⏩ 语速")

        output_text = gr.Textbox(label="💬 对话文字", lines=5, interactive=False)
        with gr.Row():
            audio_output_en = gr.Audio(label="🔊 英文语音")
            audio_output_cn = gr.Audio(label="🔊 中文语音（可选）")

        btn = gr.Button("开始对话")

        btn.click(
            process_audio,
            inputs=[audio_input, speaker_choice, dual_output, speed_slider],
            outputs=[output_text, audio_output_en, audio_output_cn],
        )

    return demo

# -----------------------------
# 启动
# -----------------------------
if __name__ == "__main__":
    ui = build_ui()
    ui.launch()
