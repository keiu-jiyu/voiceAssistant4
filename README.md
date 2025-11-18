# 🤖 AI 语音助手 (AI Voice Assistant)

这是一个功能完善的、基于 Web 的 AI 语音助手项目。它通过 WebSocket 实现前后端的实时通信，能够将用户的语音输入实时转换为文字，并调用大语言模型（LLM）进行智能对话，最终将 AI 的回答呈现在聊天界面中。

## ✨ 主要功能

- **实时语音识别 (ASR)**: 按住按钮说话，松开后即可将语音转换为文字。
- **智能 AI 对话**: 识别出的文本会自动发送给大语言模型（通义千问），实现流畅的问答交流。
- **文本输入支持**: 除了语音，也支持通过输入框发送文字消息与 AI 对话。
- **清晰的交互界面**: 实时展示用户输入、AI 思考状态和最终回答。
- **高鲁棒性**: 前后端代码都包含了详细的日志和错误处理，易于调试和扩展。

## 🛠️ 技术栈

- **后端**: Python, FastAPI, Uvicorn, WebSockets
- **前端**: React, JavaScript (JSX), CSS
- **AI 服务**: 阿里云灵积平台 (Dashscope SDK)
  - 语音识别: Paraformer Realtime ASR
  - 大语言模型: Qwen-Turbo LLM
- **音频处理**: Pydub, FFmpeg

---

## 📋 环境与依赖准备 (Prerequisites)

在开始之前，请确保您的系统已经安装了以下所有必需的软件和工具。

### 1. Python

- **要求**: Python 3.10 或更高版本。
- **检查**: 在终端输入 `python --version` 来查看您的 Python 版本。
- **下载**: [https://www.python.org/downloads/](https://www.python.org/downloads/)
  > **注意**: 在 Windows 上安装时，请务必勾选 **"Add Python to PATH"** 选项。

### 2. Node.js 和 npm

- **要求**: Node.js 16.x 或更高版本 (npm 会随之安装)。
- **检查**: 在终端输入 `node -v` 和 `npm -v` 来查看版本。
- **下载**: [https://nodejs.org/](https://nodejs.org/)

### 3. FFmpeg (至关重要)

- **作用**: 这是 `pydub` 库的底层依赖，用于处理和转换各种音频格式。**没有它，后端服务将无法处理前端发送的音频文件。**
- **检查**: 在终端输入 `ffmpeg -version`。如果命令能够成功执行并显示版本信息，则表示已安装成功。
- **安装**:
  - **Windows**:
    1.  访问 [FFmpeg for Windows Builds](https://www.gyan.dev/ffmpeg/builds/) (推荐 `essentials` 版本)。
    2.  下载 ZIP 文件并解压到一个永久的位置，例如 `C:\ffmpeg`。
    3.  将解压后的 `bin` 目录 (例如 `C:\ffmpeg\bin`) 添加到系统的 **环境变量 `Path`** 中。
    4.  重启您的终端或 PyCharm 以使环境变量生效。
  - **macOS (使用 Homebrew)**:
    ```bash
    brew install ffmpeg
    ```
  - **Linux (Debian/Ubuntu)**:
    ```bash
    sudo apt update && sudo apt install ffmpeg
    ```

---

## 🚀 安装与配置步骤

请严格按照以下步骤进行操作，以确保项目顺利运行。

### 第 1 步：克隆或下载项目

```bash
# 如果您使用 Git
git clone <your-repository-url>
cd VoiceAssistant4

# 或者直接将项目文件夹解压到您的工作区
```

### 第 2 步：配置后端 (`backend` 文件夹)

1.  **进入后端目录**:
    ```bash
    cd backend
    ```

2.  **创建 Python 虚拟环境**:
    > 虚拟环境可以隔离项目依赖，避免与全局 Python 环境冲突，这是一个非常好的习惯。
    ```bash
    python -m venv venv
    ```

3.  **激活虚拟环境**:
    - **Windows**:
      ```bash
      .\venv\Scripts\activate
      ```
    - **macOS / Linux**:
      ```bash
      source venv/bin/activate
      ```
    > 激活成功后，您会在命令行提示符前看到 `(venv)` 字样。

4.  **创建 `requirements.txt` 文件**:
    在 `backend` 目录下创建一个名为 `requirements.txt` 的文件，并将以下内容复制进去：

    ```txt
    fastapi==0.104.1
    uvicorn[standard]==0.24.0.post1
    python-dotenv==1.0.0
    loguru==0.7.2
    dashscope>=1.14.0
    pydub==0.25.1
    python-multipart==0.0.6
    websockets==12.0
    ```

5.  **安装所有 Python 依赖**:
    ```bash
    pip install -r requirements.txt
    ```

6.  **配置 API Key**:
    - 在 `backend` 目录下创建一个名为 `.env` 的新文件。
    - 从[阿里云灵积平台](https://dashscope.console.aliyun.com/apiKey)获取您的 API Key。
    - 将以下内容复制到 `.env` 文件中，并替换为您自己的 Key：
      ```env
      DASHSCOPE_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
      ```

### 第 3 步：配置前端 (`frontend` 文件夹)

1.  **打开一个新的终端窗口**。

2.  **进入前端目录**:
    ```bash
    cd frontend
    ```

3.  **安装所有 Node.js 依赖**:
    ```bash
    npm install
    ```
    > 这会根据 `package.json` 文件下载所有必需的前端库（如 React）。

---

## ▶️ 运行应用

您需要**同时启动后端服务和前端应用**。

### 1. 启动后端服务

- 确保您位于 `backend` 目录，并且虚拟环境已激活 `(venv)`。
- 运行以下命令：
  ```bash
  python main.py
  ```
- 如果一切顺利，您将在终端看到类似 `Uvicorn running on http://0.0.0.0:8000` 的输出。

### 2. 启动前端应用

- 确保您位于 `frontend` 目录（在**另一个**终端窗口中）。
- 运行以下命令：
  ```bash
  npm start
  ```
- 这会自动在您的默认浏览器中打开 `http://localhost:3000`，并加载应用界面。

现在，您可以开始与您的 AI 语音助手对话了！

---

## ⚙️ 工作流程解析

1.  **前端**: 用户按住说话按钮，浏览器通过 `MediaRecorder` API 录制音频。
2.  **前端**: 用户松开按钮，录制的音频 (`Blob`) 被转换为 Base64 字符串。
3.  **WebSocket**: 前端通过 WebSocket 将包含 Base64 音频的 JSON 消息发送到后端。
4.  **后端**: FastAPI 接收到消息，解码 Base64 字符串得到原始音频字节。
5.  **后端**: 使用 `pydub` (依赖 FFmpeg) 将音频转换为 16kHz、16-bit 单声道的 WAV 格式，这是 ASR 模型要求的标准。
6.  **ASR**: 后端将处理后的音频写入临时文件，调用 Dashscope `Recognition` API 进行语音识别。
7.  **WebSocket**: ASR 结果（用户说的文本）立刻通过 WebSocket 发回前端，用于界面更新。
8.  **LLM**: 同时，后端将 ASR 结果作为 `prompt` 调用 Dashscope `Generation` API (qwen-turbo 模型)。
9.  **WebSocket**: 大语言模型的回答通过 WebSocket 再次发送给前端。
10. **前端**: 接收并显示 AI 的最终回答，完成一次完整的对话。

---

## 🔍 故障排查 (Troubleshooting)

- **后端启动失败，提示 `ModuleNotFoundError`**:
  - **原因**: 虚拟环境未激活，或依赖未安装。
  - **解决**: 确认已激活 `(venv)` 环境，并重新运行 `pip install -r requirements.txt`。

- **后端报错 `FileNotFoundError: [WinError 2] The system cannot find the file specified` 或类似 FFmpeg 错误**:
  - **原因**: 系统找不到 `ffmpeg.exe`。
  - **解决**: 确认您已正确安装 FFmpeg，并将其 `bin` 目录添加到了系统环境变量 `Path` 中。修改环境变量后需重启终端或IDE。

- **前端显示“❌ 未连接”**:
  - **原因**: 后端服务未启动，或 WebSocket URL 错误。
  - **解决**: 确认后端服务正在运行，并检查 `App.jsx` 中 `new WebSocket('ws://localhost:8000/ws/chat')` 地址是否正确。

- **语音识别失败，后端报 API Key 错误**:
  - **原因**: `.env` 文件配置错误或 API Key 无效。
  - **解决**: 检查 `backend` 目录下是否存在 `.env` 文件，并确认 `DASHSCOPE_API_KEY` 的值是正确的、没有多余的空格或字符。
