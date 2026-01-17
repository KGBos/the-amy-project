"""
Web Interface for Amy

This is a THIN integration layer. All AI logic is in amy.core.brain.
Flask app that provides a simple chat UI.
"""

import asyncio
import logging
from flask import Flask, request, jsonify, render_template_string

from amy.core.amy import get_brain

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('instance/amy_web.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize brain
brain = get_brain()

# Create Flask app
app = Flask(__name__)

# HTML template (embedded for simplicity)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Amy - AI Assistant</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        .container {
            width: 100%;
            max-width: 600px;
        }
        .chat-box {
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            border: 1px solid rgba(255,255,255,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            text-align: center;
            color: white;
        }
        .header h1 { font-size: 1.5rem; margin-bottom: 5px; }
        .header p { opacity: 0.8; font-size: 0.9rem; }
        .messages {
            height: 400px;
            overflow-y: auto;
            padding: 20px;
        }
        .message {
            margin-bottom: 15px;
            padding: 12px 16px;
            border-radius: 15px;
            max-width: 80%;
            animation: fadeIn 0.3s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .user {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            margin-left: auto;
            text-align: right;
        }
        .amy {
            background: rgba(255,255,255,0.1);
            color: #e0e0e0;
        }
        .input-area {
            display: flex;
            padding: 15px;
            gap: 10px;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        input {
            flex: 1;
            padding: 12px 16px;
            border: none;
            border-radius: 25px;
            background: rgba(255,255,255,0.1);
            color: white;
            font-size: 1rem;
        }
        input::placeholder { color: rgba(255,255,255,0.5); }
        input:focus { outline: none; background: rgba(255,255,255,0.15); }
        button {
            padding: 12px 24px;
            border: none;
            border-radius: 25px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, opacity 0.2s;
        }
        button:hover { transform: scale(1.05); }
        button:disabled { opacity: 0.5; cursor: not-allowed; }
        .stats {
            margin-top: 20px;
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            border: 1px solid rgba(255,255,255,0.1);
            padding: 15px 20px;
            color: #a0a0a0;
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="chat-box">
            <div class="header">
                <h1>🤖 Amy</h1>
                <p>AI Assistant with Memory</p>
            </div>
            <div class="messages" id="messages">
                <div class="message amy">
                    Hi! I'm Amy. I remember our conversations. What's on your mind?
                </div>
            </div>
            <div class="input-area">
                <input type="text" id="input" placeholder="Type a message..." 
                       onkeypress="if(event.key==='Enter')send()">
                <button onclick="send()" id="btn">Send</button>
            </div>
        </div>
        <div class="stats" id="stats">Loading memory stats...</div>
    </div>
    <script>
        async function send() {
            const input = document.getElementById('input');
            const msg = input.value.trim();
            if (!msg) return;
            
            addMsg(msg, true);
            input.value = '';
            document.getElementById('btn').disabled = true;
            
            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: msg})
                });
                const data = await res.json();
                addMsg(data.success ? data.response : 'Sorry, something went wrong.');
                updateStats();
            } catch(e) {
                addMsg('Connection error. Please try again.');
            }
            document.getElementById('btn').disabled = false;
        }
        
        function addMsg(text, isUser = false) {
            const div = document.createElement('div');
            div.className = 'message ' + (isUser ? 'user' : 'amy');
            div.textContent = text;
            const msgs = document.getElementById('messages');
            msgs.appendChild(div);
            msgs.scrollTop = msgs.scrollHeight;
        }
        
        async function updateStats() {
            try {
                const res = await fetch('/stats');
                const data = await res.json();
                if (data.success) {
                    document.getElementById('stats').innerHTML = 
                        `🧠 Messages: ${data.message_count} | History: ${data.has_history ? 'Yes' : 'No'}`;
                }
            } catch(e) {}
        }
        updateStats();
    </script>
</body>
</html>
"""


@app.route('/')
def home():
    """Serve the chat interface."""
    return render_template_string(HTML_TEMPLATE)


@app.route('/chat', methods=['POST'])
def chat():
    """Handle chat messages."""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({'success': False, 'error': 'No message'})
        
        session_id = f"web_{request.remote_addr}"
        user_id = request.remote_addr
        
        logger.info(f"[Web] {user_id}: {message[:50]}...")
        
        # Run async brain.process in sync Flask context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            response = loop.run_until_complete(
                brain.chat(session_id, message, user_id, "web")
            )
        finally:
            loop.close()
        
        return jsonify({'success': True, 'response': response})
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({'success': False, 'error': str(e)})


@app.route('/stats')
def stats():
    """Get memory statistics."""
    try:
        session_id = f"web_{request.remote_addr}"
        stats = brain.get_memory_stats(session_id)
        return jsonify({'success': True, **stats})
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({'success': False, 'error': str(e)})


def run_web_interface(host='127.0.0.1', port=8080, debug=False):
    """Run the web interface."""
    print("🌐 Starting Amy Web Interface")
    print(f"📱 Open: http://{host}:{port}")
    print("🛑 Press Ctrl+C to stop")
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    run_web_interface()