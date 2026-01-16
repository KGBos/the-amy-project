import { FC } from 'react';
import { Copy, ThumbsUp, ThumbsDown, Edit, RefreshCw } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'prism-react-renderer';
import { Message } from '../types';

const MessageComponent: FC<{
  message: Message;
  onReact: (reaction: string) => void;
  onCopy: () => void;
  onEdit: () => void;
  onRegenerate: () => void;
}> = ({ message, onReact, onCopy, onEdit, onRegenerate }) => {
  return (
    <div className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`max-w-xl p-4 rounded-2xl ${message.sender === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-800 text-white'}`}>
        <ReactMarkdown
          components={{
            code: ({ node, inline, className, children, ...props }: {
              node: any;
              inline?: boolean;
              className?: string;
              children: React.ReactNode;
              [key: string]: any;
            }) => {
              const match = /language-(\w+)/.exec(className || '');
              return !inline && match ? (
                <SyntaxHighlighter language={match[1]} children={String(children).replace(/\n$/, '')} {...props} />
              ) : (
                <code className={className} {...props}>
                  {children}
                </code>
              );
            },
          }}
        >
          {message.text}
        </ReactMarkdown>
        <p className="text-xs text-gray-400 mt-1">{message.timestamp.toLocaleString()}</p>
        {message.sender === 'user' ? null : (
          <div className="flex gap-2 mt-2">
            <ThumbsUp onClick={() => onReact('👍')} className="cursor-pointer" />
            <ThumbsDown onClick={() => onReact('👎')} className="cursor-pointer" />
            <Copy onClick={onCopy} className="cursor-pointer" />
            <Edit onClick={onEdit} className="cursor-pointer" />
            <RefreshCw onClick={onRegenerate} className="cursor-pointer" />
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageComponent;