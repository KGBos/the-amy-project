import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ChatHeader from './components/ChatHeader';
import MessageList from './components/MessageList';
import InputArea from './components/InputArea';
import { ChatProvider, useChat } from './context/ChatContext';
import { Menu } from 'lucide-react';

const AppContent: React.FC = () => {
  const { theme } = useChat();
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
      if (window.innerWidth < 768) setSidebarOpen(false);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const toggleSidebar = () => setSidebarOpen(!sidebarOpen);

  return (
    <div className="flex h-screen" className={theme === 'dark' ? 'dark' : ''}>
      {(!isMobile || sidebarOpen) && <Sidebar isMobile={sidebarOpen} toggleSidebar={toggleSidebarOpen} />}
      <main className="flex-1 flex flex-col h-screen">
        {isMobile && (
          <button onClick={toggleSidebar} className="p-4">
            <Menu />
          </button>
        )}
        <ChatHeader />
        <MessageList />
        <InputArea />
      </main>
    </div>
  );
};

const App = () => (
  <ChatProvider>
    <AppContent />
  </ChatProvider>
);

export default App;