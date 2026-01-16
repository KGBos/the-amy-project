import React, { useState } from 'react';
import { Send, Paperclip, Mic } from 'lucide-react';
import { useChat } from '../context/ChatContext';
import { Message } from '../types';

const InputArea: React.FC = () => {
  const { currentChat, addMessage, theme } = useChat();
  const [text, setText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [file, setFile] = useState<File | null>(null);

  const handleSend = () => {
    if (!currentChat || !text.trim()) return;
    const userMsg: Message = { id: Date.now().toString(), text, sender: 'user', timestamp: new Date() };
    addMessage(currentChat.id, userMsg);
    // Simulate AI response with streaming
    setIsTyping(true);
    let aiText = '';
    const streamText = 'AI response streaming: ' + text;
    const interval = setInterval(() => {
      if (aiText.length < streamText.length) {
        aiText += streamText[aiText.length];
        // Update last message or add if new
      } else {
        clearInterval(interval);
        const aiMsg: Message = { id: Date.now().toString(), text: streamText, sender: 'ai', timestamp: new Date() };
        addMessage(currentChat.id, aiMsg);
        setIsTyping(false);
      }
    }, 50);
    setText('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) setFile(e.target.files[0]);
    // Preview: Add file preview to message if sent
  };

  const handleVoice = () => {
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.onresult = (e: any) => setText(e.results[0][0].transcript);
      recognition.start();
    } else {
      console.warn('SpeechRecognition not supported');
    }
  };

  return (
    <div className="p-4 border-t flex items-center gap-2">
      <label htmlFor="file-upload">
        <Paperclip className="cursor-pointer" />
        <input id="file-upload" type="file" className="hidden" onChange={handleFileChange} />
      </label>
      <Mic onClick={handleVoice} className="cursor-pointer" />
      <textarea
        value={text}
        onChange={e => setText(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type a message..."
        className={`flex-1 p-2 rounded-lg resize-none ${theme === 'dark' ? 'bg-gray-800 text-white' : 'bg-gray-100 text-black'}`}
        rows={1}
      />
      <button onClick={handleSend} className="bg-blue-600 text-white p-2 rounded">
        <Send />
      </button>
      {text.length > 0 && <span className="text-xs">{text.length}/500</span>}
      {isTyping && <span className="text-gray-500">Grok is typing...</span>}
    </div>
  );
};

export default InputArea;