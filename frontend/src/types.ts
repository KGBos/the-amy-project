export interface Message {
    id: string;
    text: string;
    sender: 'user' | 'ai';
    timestamp: Date;
    reactions?: string[];
  }
  
  export interface Chat {
    id: string;
    title: string;
    messages: Message[];
    timestamp: Date;
  }