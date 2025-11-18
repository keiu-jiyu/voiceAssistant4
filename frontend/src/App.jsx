// App.jsx
import { useState, useRef, useEffect } from 'react';
import './App.css';

export default function App() {
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isListening, setIsListening] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  
  const ws = useRef(null);
  const mediaRecorder = useRef(null);
  const audioChunks = useRef([]);
  const chatBoxRef = useRef(null); // <-- 新增: 用于自动滚动

  // 自动滚动到聊天框底部
  useEffect(() => {
    if (chatBoxRef.current) {
      chatBoxRef.current.scrollTop = chatBoxRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
    ws.current = new WebSocket('ws://localhost:8000/ws/chat');
    
    ws.current.onopen = () => setIsConnected(true);
    ws.current.onclose = () => setIsConnected(false);
    ws.current.onerror = (error) => console.error('❌ WebSocket 错误:', error);

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('📨 收到消息:', data);
      
      setMessages(prev => {
        let newMessages = [...prev];
        switch (data.type) {
          // 步骤1: ASR结果返回，替换"正在识别..."
          case 'asr_result':
            newMessages[newMessages.length - 1] = { type: 'user', content: data.text };
            // 立刻添加一个"AI思考中"的占位符
            newMessages.push({ type: 'assistant', content: '🤖 正在思考...' });
            break;

          // 步骤2: LLM结果返回，替换"AI思考中..."
          case 'llm_response':
            // 查找并替换最后一个助手的消息
            const lastAssistantMsgIndex = newMessages.map(m => m.type).lastIndexOf('assistant');
            if (lastAssistantMsgIndex !== -1) {
              newMessages[lastAssistantMsgIndex] = { type: 'assistant', content: data.text };
            } else { // 如果没有找到占位符（例如纯文本输入），则直接添加
              newMessages.push({ type: 'assistant', content: data.text });
            }
            break;

          case 'error':
            alert('❌ ' + data.message);
            // 出错时，移除最后的占位消息
            newMessages = prev.filter(msg => !msg.content.includes('...'));
            break;
            
          default:
            break;
        }
        return newMessages;
      });
    };

    return () => ws.current?.close();
  }, []);

  const startRecording = async () => {
    if (!isConnected) return alert('❌ 未连接到服务器');
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorder.current = new MediaRecorder(stream);
      audioChunks.current = [];
      mediaRecorder.current.ondataavailable = (event) => audioChunks.current.push(event.data);
      mediaRecorder.current.onstop = () => {
        const audioBlob = new Blob(audioChunks.current, { type: 'audio/webm' });
        const reader = new FileReader();
        reader.onloadend = () => {
          const base64String = reader.result.split(',')[1];
          console.log(`🎙️ 发送音频: ${audioBlob.size} 字节`);
          ws.current.send(JSON.stringify({ type: 'audio', data: base64String }));
        };
        reader.readAsDataURL(audioBlob);
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.current.start();
      setIsListening(true);
      setMessages(prev => [...prev, { type: 'user', content: '🎙️ 正在识别...' }]);
    } catch (error) {
      console.error('❌ 获取麦克风失败:', error);
      alert('❌ 无法访问麦克风: ' + error.message);
    }
  };

  const stopRecording = () => {
    if (mediaRecorder.current?.state === 'recording') {
      mediaRecorder.current.stop();
      setIsListening(false);
    }
  };

  const handleSendText = () => {
    if (!inputText.trim() || !isConnected) return;
    setMessages(prev => [...prev, 
      { type: 'user', content: inputText },
      { type: 'assistant', content: '🤖 正在思考...' } // 文本发送也加占位符
    ]);
    ws.current.send(JSON.stringify({ type: 'text', data: inputText }));
    setInputText('');
  };
  
  return (
    <div className="container">
      <h1>🤖 AI 语音助手</h1>
      <div className="chat-box" ref={chatBoxRef}> {/* <-- 新增 ref */}
        {messages.length === 0 ? (
          <div className="empty-state">👈 按住按钮与 AI 对话</div>
        ) : (
          messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.type}`}>
              <span>{msg.content}</span>
            </div>
          ))
        )}
      </div>
      <div className="input-area">
        <input
          type="text" value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendText()}
          placeholder="输入消息..." disabled={!isConnected}
        />
        <button onClick={handleSendText} disabled={!isConnected}>发送</button>
      </div>
      <div className="voice-area">
        <button
          onMouseDown={startRecording} onMouseUp={stopRecording}
          onTouchStart={startRecording} onTouchEnd={stopRecording}
          disabled={!isConnected}
          className={`voice-btn ${isListening ? 'listening' : ''}`}
        >
          {isListening ? '🎤 聆听中...' : '🎙️ 按住说话'}
        </button>
        <div className="status">
          {isConnected ? '✅ 已连接' : '❌ 未连接'}
        </div>
      </div>
    </div>
  );
}