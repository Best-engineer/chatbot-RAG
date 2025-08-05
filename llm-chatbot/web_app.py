#!/usr/bin/env python3
"""
LLM Chatbot Web Application
교육 서비스 챗봇 웹 인터페이스
"""

from flask import Flask, render_template, request, jsonify, session
import os
import sys
from pathlib import Path
import logging

# src 모듈 import를 위한 경로 추가
sys.path.append(str(Path(__file__).parent / "src"))

from src.search import ChatbotSearch
from src.embedding import DocumentEmbedder

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # 실제 운영시에는 환경변수로 설정

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 챗봇 초기화
embedder = DocumentEmbedder()
chatbot = ChatbotSearch(embedder)

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    """챗봇 대화 API"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                'success': False,
                'message': '메시지를 입력해주세요.'
            })
        
        # 챗봇 응답 생성
        response = chatbot.search_and_respond(user_message)
        
        return jsonify({
            'success': True,
            'message': response,
            'user_message': user_message
        })
        
    except Exception as e:
        logger.error(f"Chat API error: {e}")
        return jsonify({
            'success': False,
            'message': '죄송합니다. 일시적인 오류가 발생했습니다.'
        })

@app.route('/health')
def health_check():
    """헬스 체크 API"""
    try:
        info = embedder.get_collection_info()
        return jsonify({
            'status': 'healthy',
            'document_count': info['document_count'],
            'collection_name': info['collection_name']
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

if __name__ == '__main__':
    # 템플릿 디렉토리 생성
    templates_dir = Path(__file__).parent / 'templates'
    templates_dir.mkdir(exist_ok=True)
    
    # 기본 HTML 템플릿 생성
    create_basic_template()
    
    print("=" * 50)
    print("LLM Chatbot Web Application")
    print("=" * 50)
    print("웹 서버를 시작합니다...")
    print("브라우저에서 http://localhost:5000 으로 접속하세요.")
    print("종료하려면 Ctrl+C를 누르세요.")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

def create_basic_template():
    """기본 HTML 템플릿 생성"""
    template_content = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>교육 서비스 챗봇</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        
        .chat-container {
            width: 90%;
            max-width: 600px;
            height: 80vh;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        
        .chat-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            text-align: center;
        }
        
        .chat-header h1 {
            font-size: 24px;
            margin-bottom: 5px;
        }
        
        .chat-header p {
            font-size: 14px;
            opacity: 0.9;
        }
        
        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background: #f8f9fa;
        }
        
        .message {
            margin-bottom: 15px;
            display: flex;
            align-items: flex-start;
        }
        
        .message.user {
            justify-content: flex-end;
        }
        
        .message.bot {
            justify-content: flex-start;
        }
        
        .message-content {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            word-wrap: break-word;
        }
        
        .message.user .message-content {
            background: #667eea;
            color: white;
            border-bottom-right-radius: 4px;
        }
        
        .message.bot .message-content {
            background: white;
            color: #333;
            border: 1px solid #e0e0e0;
            border-bottom-left-radius: 4px;
        }
        
        .chat-input {
            padding: 20px;
            background: white;
            border-top: 1px solid #e0e0e0;
        }
        
        .input-container {
            display: flex;
            gap: 10px;
        }
        
        .chat-input input {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #e0e0e0;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
            transition: border-color 0.3s;
        }
        
        .chat-input input:focus {
            border-color: #667eea;
        }
        
        .chat-input button {
            padding: 12px 24px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .chat-input button:hover {
            transform: translateY(-2px);
        }
        
        .chat-input button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .typing-indicator {
            display: none;
            padding: 12px 16px;
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 18px;
            border-bottom-left-radius: 4px;
            color: #666;
            font-style: italic;
        }
        
        .welcome-message {
            text-align: center;
            color: #666;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h1>🎓 교육 서비스 챗봇</h1>
            <p>궁금한 교육 과정에 대해 언제든 물어보세요!</p>
        </div>
        
        <div class="chat-messages" id="chatMessages">
            <div class="welcome-message">
                안녕하세요! 교육 과정에 대한 문의사항이 있으시면 언제든 말씀해주세요. 
                머신러닝, 데이터 사이언스, 프로그래밍 등 다양한 과정을 안내해드립니다.
            </div>
        </div>
        
        <div class="chat-input">
            <div class="input-container">
                <input type="text" id="messageInput" placeholder="교육 과정에 대해 질문해주세요..." maxlength="500">
                <button id="sendButton" onclick="sendMessage()">전송</button>
            </div>
        </div>
        
        <div class="typing-indicator" id="typingIndicator">
            상담원이 답변을 작성하고 있습니다...
        </div>
    </div>

    <script>
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        const chatMessages = document.getElementById('chatMessages');
        const typingIndicator = document.getElementById('typingIndicator');

        // Enter 키로 메시지 전송
        messageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });

        // 메시지 전송 함수
        async function sendMessage() {
            const message = messageInput.value.trim();
            if (!message) return;

            // 사용자 메시지 표시
            addMessage(message, 'user');
            messageInput.value = '';
            sendButton.disabled = true;

            // 타이핑 인디케이터 표시
            typingIndicator.style.display = 'block';
            chatMessages.scrollTop = chatMessages.scrollHeight;

            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message })
                });

                const data = await response.json();
                
                // 타이핑 인디케이터 숨기기
                typingIndicator.style.display = 'none';

                if (data.success) {
                    // 봇 응답 표시
                    addMessage(data.message, 'bot');
                } else {
                    // 오류 메시지 표시
                    addMessage('죄송합니다. 일시적인 오류가 발생했습니다.', 'bot');
                }
            } catch (error) {
                console.error('Error:', error);
                typingIndicator.style.display = 'none';
                addMessage('죄송합니다. 네트워크 오류가 발생했습니다.', 'bot');
            }

            sendButton.disabled = false;
            messageInput.focus();
        }

        // 메시지 추가 함수
        function addMessage(content, sender) {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;
            
            const messageContent = document.createElement('div');
            messageContent.className = 'message-content';
            messageContent.textContent = content;
            
            messageDiv.appendChild(messageContent);
            chatMessages.appendChild(messageDiv);
            
            // 스크롤을 맨 아래로
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }

        // 페이지 로드 시 입력 필드에 포커스
        window.onload = function() {
            messageInput.focus();
        };
    </script>
</body>
</html>
"""
    
    template_file = templates_dir / 'index.html'
    with open(template_file, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print(f"✅ HTML 템플릿이 생성되었습니다: {template_file}") 