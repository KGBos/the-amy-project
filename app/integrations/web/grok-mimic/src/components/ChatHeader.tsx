import React from 'react';
import { MoreHorizontal, Share2, Download } from 'lucide-react';
import { useChat } from '../context/ChatContext';
import jsPDF from 'jspdf';

const ChatHeader: React.FC = () => {
  const { currentChat } = useChat();

  const exportToText = () => {
    if (!currentChat) return;
    const text = currentChat.messages.map(m => `${m.sender.toUpperCase()}: ${m.text}`).join('\n');
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${currentChat.title}.txt`;
    a.click();
  };

  const exportToPDF = () => {
    if (!currentChat) return;
    const doc = new jsPDF();
    doc.text(currentChat.title, 10, 10);
    let y = 20;
    currentChat.messages.forEach(m => {
      doc.text(`${m.sender.toUpperCase()}: ${m.text}`, 10, y);
      y += 10;
    });
    doc.save(`${currentChat.title}.pdf`);
  };

  return (
    <header className="flex items-center justify-between p-4 border-b">
      <h2 className="text-lg font-semibold">{currentChat?.title || 'New Chat'}</h2>
      <div className="flex gap-2">
        <Share2 className="cursor-pointer" />
        <Download onClick={exportToText} className="cursor-pointer" title="Export to Text" />
        <Download onClick={exportToPDF} className="cursor-pointer" title="Export to PDF" />
        <MoreHorizontal className="cursor-pointer" />
      </div>
    </header>
  );
};

export default ChatHeader;