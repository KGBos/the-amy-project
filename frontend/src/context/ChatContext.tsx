import React, { createContext, useState, useContext, useEffect } from 'react';
import { Chat, Message } from '../types';

interface ChatContextType {
  chats: Chat[];
  currentChat: Chat | null;
  theme: 'dark' | 'light';
  addChat: (title: string) => void;
  selectChat: (id: string) => void;
  addMessage: (chatId: string, message: Message) => void;
  toggleTheme: () => void;
  searchHistory: (query: string) => Chat[];
}

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [chats, setChats] = useState<Chat[]>([]);
  const [currentChat, setCurrentChat] = useState<Chat | null>(null);
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');

  useEffect(() => {
    // Sample data
    const sampleChats: Chat[] = [
      {
        id: '1',
        title: 'Sample Chat 1',
        messages: [
          { id: 'm1', text: 'Hello!', sender: 'user', timestamp: new Date() },
          { id: 'm2', text: 'Hi there!', sender: 'ai', timestamp: new Date() },
        ],
        timestamp: new Date(),
      },
      // Add more samples
    ];
    setChats(sampleChats);
    setCurrentChat(sampleChats[0]);
  }, []);

  const addChat = (title: string) => {
    const newChat: Chat = {
      id: Date.now().toString(),
      title,
      messages: [],
      timestamp: new Date(),
    };
    setChats([...chats, newChat]);
    setCurrentChat(newChat);
  };

  const selectChat = (id: string) => {
    const chat = chats.find(c => c.id === id);
    if (chat) setCurrentChat(chat);
  };

  const addMessage = (chatId: string, message: Message) => {
    setChats(prev => prev.map(c => 
      c.id === chatId ? { ...c, messages: [...c.messages, message] } : c
    ));
    if (currentChat?.id === chatId) {
      setCurrentChat(prev => prev ? { ...prev, messages: [...prev.messages, message] } : null);
    }
  };

  const toggleTheme = () => {
    setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  };

  const searchHistory = (query: string) => {
    return chats.filter(c => c.title.toLowerCase().includes(query.toLowerCase()));
  };

  return (
    <ChatContext.Provider value={{ chats, currentChat, theme, addChat, selectChat, addMessage, toggleTheme, searchHistory }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) throw new Error('useChat must be used within ChatProvider');
  return context;
};