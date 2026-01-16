"""
Custom web interface for Amy that uses our MemoryManager for consistent memory
"""

import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from dotenv import load_dotenv
import google.generativeai as genai

# Import the memory system
from amy.features.memory import MemoryManager

# Load environment variables
load_dotenv()

# Configure Gemini/Google Generative AI
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY (or GOOGLE_API_KEY) environment variable is required")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-flash')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('instance/amy_web_interface.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Initialize memory manager
memory_manager = MemoryManager()

# Create Flask app
app = Flask(__name__)

# HTML template for the chat interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Amy - AI Assistant with Memory</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .chat-container {
            background: white;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            height: 500px;
            display: flex;
            flex-direction: column;
        }
        .chat-header {
            background: #007bff;
            color: white;
            padding: 15px;
            border-radius: 10px 10px 0 0;
            text-align: center;
        }
        .chat-messages {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px 15px;
            border-radius: 10px;
            max-width: 70%;
        }
        .user-message {
            background: #007bff;
            color: white;
            margin-left: auto;
        }
        .amy-message {
            background: #e9ecef;
            color: #333;
        }
        .chat-input {
            padding: 20px;
            border-top: 1px solid #ddd;
            display: flex;
        }
        .chat-input input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin-right: 10px;
        }
        .chat-input button {
            padding: 10px 20px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .chat-input button:hover {
            background: #0056b3;
        }
        .memory-stats {
            background: #f8f9fa;
            padding: 15px;
            margin-top: 20px;
            border-radius: 10px;
            border: 1px solid #ddd;
        }
        .loading {
            text-align: center;
            color: #666;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <h2>🤖 Amy - AI Assistant with Memory</h2>
            <p>Chat with Amy and test her memory system!</p>
        </div>
        <div class="chat-messages" id="messages">
            <div class="message amy-message">
                Hi! I'm Amy, your AI assistant with memory. I can remember our conversations and learn about you over time. What would you like to chat about?
            </div>
        </div>
        <div class="chat-input">
            <input type="text" id="messageInput" placeholder="Type your message..." onkeypress="handleKeyPress(event)">
            <button onclick="sendMessage()">Send</button>
        </div>
    </div>
    
    <div class="memory-stats">
        <h3>🧠 Memory Statistics</h3>
        <div id="memoryStats">Loading...</div>
    </div>

    <script>
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        function addMessage(content, isUser = false) {
            const messagesDiv = document.getElementById('messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user-message' : 'amy-message'}`;
            messageDiv.textContent = content;
            messagesDiv.appendChild(messageDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        function showLoading() {
            const messagesDiv = document.getElementById('messages');
            const loadingDiv = document.createElement('div');
            loadingDiv.className = 'message amy-message loading';
            loadingDiv.id = 'loading';
            loadingDiv.textContent = 'Amy is thinking...';
            messagesDiv.appendChild(loadingDiv);
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        function hideLoading() {
            const loadingDiv = document.getElementById('loading');
            if (loadingDiv) {
                loadingDiv.remove();
            }
        }

        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            
            if (!message) return;
            
            // Add user message
            addMessage(message, true);
            input.value = '';
            
            // Show loading
            showLoading();
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ message: message })
                });
                
                const data = await response.json();
                hideLoading();
                
                if (data.success) {
                    addMessage(data.response);
                    updateMemoryStats();
                } else {
                    addMessage('Sorry, I encountered an error. Please try again.');
                }
            } catch (error) {
                hideLoading();
                addMessage('Sorry, I encountered an error. Please try again.');
                console.error('Error:', error);
            }
        }

        async function updateMemoryStats() {
            try {
                const response = await fetch('/memory-stats');
                const data = await response.json();
                
                if (data.success) {
                    const stats = data.stats;
                    document.getElementById('memoryStats').innerHTML = `
                        <p><strong>Active Sessions:</strong> ${stats.stm_sessions}</p>
                        <p><strong>Total Conversations:</strong> ${stats.mtm_sessions}</p>
                        <p><strong>Facts Stored:</strong> ${stats.ltm_facts}</p>
                        <p><strong>Fact Types:</strong> ${Object.entries(stats.fact_types).map(([type, count]) => `${type}: ${count}`).join(', ') || 'None'}</p>
                    `;
                }
            } catch (error) {
                console.error('Error updating memory stats:', error);
            }
        }

        // Load initial memory stats
        updateMemoryStats();
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
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'success': False, 'error': 'No message provided'})
        
        # Create session ID for this conversation
        session_id = f"web_{request.remote_addr}"
        
        # Log the user message
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logger.info(f"--- USER MESSAGE ({timestamp}) ---")
        logger.info(f"IP: {request.remote_addr}")
        logger.info(f"Message: {user_message}")
        
        # Process user message through memory system
        memory_manager.process_message(
            session_id=session_id,
            platform="web",
            role="user",
            content=user_message,
            user_id=request.remote_addr,
            username="web_user"
        )
        
        # Build context for Amy's response
        context = memory_manager.get_context_for_query(session_id, user_message)
        
        # Create the conversation prompt with context
        system_prompt = "You are Amy, a helpful and friendly AI assistant with memory. You can remember past conversations and learn about users over time. Respond directly to the user's message in a conversational way, using context from previous conversations when relevant."
        
        # Build the full prompt with context
        if context:
            full_prompt = f"{system_prompt}\n\n{context}\n\nUser: {user_message}\nAmy:"
        else:
            full_prompt = f"{system_prompt}\n\nUser: {user_message}\nAmy:"
        
        # Log the context being used
        logger.info(f"--- CONTEXT FOR AMY ---")
        logger.info(f"Context length: {len(context)} characters")
        if context:
            logger.info(f"Context: {context[:200]}...")
        
        # Generate response using Google Generative AI
        response = model.generate_content(
            full_prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.7,
                top_p=0.8,
                top_k=40,
                max_output_tokens=1024,
            )
        )
        
        # Check if response was blocked by safety filters
        if response.candidates and response.candidates[0].finish_reason == 2:
            amy_response = "I apologize, but I'm unable to respond to that message due to content safety filters. Could you please rephrase your message?"
        elif response.text:
            amy_response = response.text
        else:
            amy_response = "I'm sorry, I encountered an issue generating a response. Please try again."
        
        # Process Amy's response through memory system
        memory_manager.process_message(
            session_id=session_id,
            platform="web",
            role="model",
            content=amy_response,
            user_id=request.remote_addr,
            username="web_user"
        )
        
        # Log the response
        logger.info(f"--- AMY RESPONSE ({timestamp}) ---")
        logger.info(f"Response: {amy_response}")
        
        return jsonify({'success': True, 'response': amy_response})
        
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/memory-stats')
def memory_stats():
    """Get memory statistics."""
    try:
        stats = memory_manager.get_memory_stats()
        return jsonify({
            'success': True,
            'stats': {
                'stm_sessions': stats['stm']['active_sessions'],
                'mtm_sessions': stats['episodic']['total_sessions'],
                'ltm_facts': sum(stats['ltm']['fact_types'].values()),
                'fact_types': stats['ltm']['fact_types']
            }
        })
    except Exception as e:
        logger.error(f"Error getting memory stats: {e}")
        return jsonify({'success': False, 'error': str(e)})

def run_web_interface(host='127.0.0.1', port=8080, debug=False):
    """Run the web interface."""
    print("🌐 Starting Amy Web Interface with Memory System")
    print("=" * 50)
    print(f"📱 Web interface will be available at: http://{host}:{port}")
    print("💡 Start chatting with Amy to test the memory system!")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    app.run(host=host, port=port, debug=debug)

if __name__ == "__main__":
    run_web_interface() 