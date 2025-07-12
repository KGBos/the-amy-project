import React, { useState } from 'react';
import { Menu, Plus, Settings, Search } from 'lucide-react';
import { useChat } from '../context/ChatContext';

const Sidebar: React.FC<{ isMobile: boolean; toggleSidebar: () => void }> = ({ isMobile, toggleSidebar }) => {
  const { chats, addChat, selectChat, theme, toggleTheme, searchHistory } = useChat();
  const [searchQuery, setSearchQuery] = useState('');

  const filteredChats = searchQuery ? searchHistory(searchQuery) : chats;

  return (
    <aside className={`fixed inset-y-0 left-0 z-10 flex flex-col h-screen border-r transition-all duration-300 ${theme === 'dark' ? 'bg-gray-900 text-white' : 'bg-white text-black'} ${isMobile ? 'w-64 translate-x-0' : 'w-64'}`}>
      <div className="flex items-center justify-between p-4">
        <h1 className="text-xl font-bold">Grok</h1>
        {isMobile && <Menu onClick={toggleSidebar} className="cursor-pointer" />}
      </div>
      <button onClick={() => addChat('New Chat')} className="mx-4 mb-4 flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg">
        <Plus className="mr-2" /> New Chat
      </button>
      <div className="p-4">
        <div className="relative">
          <Search className="absolute left-3 top-3 text-gray-400" size={16} />
          <input
            type="text"
            placeholder="Search chats..."
            value={searchQuery}
            onChange={e => setSearchQuery(e.target.value)}
            className={`w-full pl-10 pr-4 py-2 rounded-lg ${theme === 'dark' ? 'bg-gray-800 text-white' : 'bg-gray-100 text-black'}`}
          />
        </div>
      </div>
      <div className="flex-1 overflow-y-auto px-4">
        {filteredChats.map(chat => (
          <div
            key={chat.id}
            onClick={() => selectChat(chat.id)}
            className={`py-2 cursor-pointer hover:bg-gray-700 rounded ${theme === 'dark' ? 'hover:bg-gray-800' : 'hover:bg-gray-200'}`}
          >
            <p className="truncate">{chat.title}</p>
            <p className="text-xs text-gray-500">{chat.timestamp.toLocaleString()}</p>
          </div>
        ))}
      </div>
      <div className="p-4 border-t">
        <div className="flex items-center justify-between">
          <Settings className="cursor-pointer" />
          <button onClick={toggleTheme} className="text-sm">
            {theme === 'dark' ? 'Light Theme' : 'Dark Theme'}
          </button>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;