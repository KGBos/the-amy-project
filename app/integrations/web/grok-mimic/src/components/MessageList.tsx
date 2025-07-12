import React, { useRef, useEffect } from 'react';
import Message from './Message';
import { useChat } from '../context/ChatContext';

const MessageList: React.FC = () => {
  const { currentChat, addMessage } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [currentChat?.messages]);

  const handleReact = (msgId: string, reaction: string) => {
    // Simulate adding reaction
  };

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
  };

  const handleEdit = (msgId: string) => {
    // Simulate edit
  };

  const handleRegenerate = (msgId: string) => {
    // Simulate regenerate
  };

  return (
    <div className="flex-1 overflow-y-auto p-4">
      {currentChat?.messages.map(msg => (
        <Message
          key={msg.id}
          message={msg}
          onReact={reaction => handleReact(msg.id, reaction)}
          onCopy={() => handleCopy(msg.text)}
          onEdit={() => handleEdit(msg.id)}
          onRegenerate={() => handleRegenerate(msg.id)}
        />
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList;