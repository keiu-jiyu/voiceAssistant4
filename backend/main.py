# main.py

import os
import asyncio
import base64
import io
import tempfile
import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from loguru import logger
import dashscope
from dashscope.audio.asr import Recognition
from dashscope import Generation
from pydub import AudioSegment

# 加载环境变量并设置API Key
load_dotenv()
dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
if dashscope.api_key:
    logger.info("✅ API Key 已设置")
else:
    logger.error("❌ 未找到 DASHSCOPE_API_KEY，请检查 .env 文件")
    exit()


# ==================== 音频格式转换 ====================
# (此函数保持不变)
async def convert_audio_to_wav_16k_mono(audio_bytes: bytes) -> bytes:
    try:
        logger.info("🔊 开始音频格式转换...")
        audio = AudioSegment.from_file(io.BytesIO(audio_bytes))
        audio = audio.set_frame_rate(16000).set_channels(1).set_sample_width(2)
        wav_buffer = io.BytesIO()
        audio.export(wav_buffer, format="wav")
        wav_bytes = wav_buffer.getvalue()
        logger.info(f"✅ 音频转换成功，WAV 大小: {len(wav_bytes)} 字节")
        return wav_bytes
    except Exception as e:
        logger.error(f"❌ 音频转换失败: {e}", exc_info=True)
        return None


# ==================== ASR 识别 ====================
# (此部分保持不变)
def sync_recognition_call(wav_audio_bytes: bytes):
    temp_dir = tempfile.gettempdir()
    temp_filename = os.path.join(temp_dir, f"asr_audio_{uuid.uuid4()}.wav")
    try:
        with open(temp_filename, "wb") as f:
            f.write(wav_audio_bytes)
        logger.info(f"💾 音频已写入临时文件: {temp_filename}")
        recognition_instance = Recognition(
            model='paraformer-realtime-v2', format='wav',
            sample_rate=16000, callback=None
        )
        result = recognition_instance.call(file=temp_filename)
        return result
    except Exception as e:
        logger.error(f"❌ 同步调用 Recognition.call 时发生异常: {e}", exc_info=True)
        return None
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
            logger.info(f"🗑️ 已删除临时文件: {temp_filename}")


async def asr_recognize(audio_bytes: bytes) -> str:
    try:
        wav_audio_bytes = await convert_audio_to_wav_16k_mono(audio_bytes)
        if not wav_audio_bytes: return "音频处理失败"
        logger.info(f"🎙️ 开始识别，音频大小: {len(wav_audio_bytes)} 字节")
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, sync_recognition_call, wav_audio_bytes)
        if result is None: return "ASR服务调用内部错误"
        if result.status_code == 200:
            sentences = result.get_sentence()
            if sentences:
                text = ' '.join([s.get('text', '') for s in sentences]).strip()
                logger.info(f"✅ ASR 识别结果: '{text}'")
                return text
            else:
                logger.warning(f"⚠️ ASR 服务返回成功，但识别文本为空。")
                return ""
        else:
            logger.error(f"❌ ASR 失败: {result.status_code} - {result.message}")
            return ""
    except Exception as e:
        logger.error(f"❌ 语音识别异常: {e}", exc_info=True)
        return ""


# ==================== LLM 对话（新增部分） ====================
async def get_llm_response(prompt: str) -> str:
    """调用大语言模型获取响应"""
    logger.info(f"🤖 正在为提示生成回答: '{prompt}'")
    try:
        # 使用 run_in_executor 运行同步的SDK调用
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,  # 使用默认线程池
            lambda: Generation.call(
                model='qwen-turbo',
                messages=[{'role': 'system', 'content': '你是一个乐于助人的语音助手。'},
                          {'role': 'user', 'content': prompt}],
                result_format='message'
            )
        )

        if response.status_code == 200:
            llm_text = response.output.choices[0].message.content
            logger.info(f"✅ LLM 回答: '{llm_text}'")
            return llm_text
        else:
            logger.error(f"❌ LLM API 错误: {response.code} - {response.message}")
            return "抱歉，AI思考时出了一点小问题。"

    except Exception as e:
        logger.error(f"❌ 调用 LLM 时发生异常: {e}", exc_info=True)
        return "抱歉，我的大脑连接好像断开了。"


# ==================== WebSocket, FastAPI (逻辑更新) ====================
# (ConnectionManager 保持不变)
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"✅ 客户端连接，总连接数: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"❌ 客户端断开，总连接数: {len(self.active_connections)}")


manager = ConnectionManager()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)


@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            logger.info(f"📨 收到消息类型: {message_type}")

            if message_type == "audio":
                audio_base64 = data.get("data")
                if not audio_base64: continue

                try:
                    audio_bytes = base64.b64decode(audio_base64)
                    logger.info(f"🎙️ 收到原始音频: {len(audio_bytes)} 字节")

                    # 步骤 1: 语音识别
                    user_text = await asr_recognize(audio_bytes)

                    if user_text:
                        # 步骤 1.1: 立刻将识别结果发回前端
                        await websocket.send_json({"type": "asr_result", "text": user_text})

                        # 步骤 2: 获取 LLM 回答
                        ai_response = await get_llm_response(user_text)

                        # 步骤 3: 将 LLM 回答发回前端
                        await websocket.send_json({"type": "llm_response", "text": ai_response})
                    else:
                        await websocket.send_json({"type": "error", "message": "识别失败或未检测到有效语音"})

                except Exception as e:
                    logger.error(f"❌ 音频处理流程异常: {e}", exc_info=True)
                    await websocket.send_json({"type": "error", "message": f"服务器处理音频时出错: {e}"})

            # (文本输入逻辑保持不变)
            elif message_type == "text":
                text = data.get("data")
                logger.info(f"💬 收到文本: {text}")
                ai_response = await get_llm_response(text)
                await websocket.send_json({"type": "llm_response", "text": ai_response})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"❌ WebSocket 异常: {e}", exc_info=True)
        manager.disconnect(websocket)


@app.get("/health")
async def health(): return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="info", reload=True)