import React, { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { MessageCircle, Send, X } from 'lucide-react';
import './Chat.css';
import botAvatar from '../assets/launcher-logo.png';

const ChatMessage = ({ message, onQuickReplyClick, messageIndex }) => {
  if (message.sender === 'user') {
    return <div className="message user">{message.text}</div>;
  }

  return (
    <div className="message bot">
      <div className="summary-section">
        <ReactMarkdown>{message.summary.text}</ReactMarkdown>

        {message.summary.quick_replies?.length > 0 && (
          <div className="quick-replies">
            {message.summary.quick_replies.map((reply, idx) => (
              <button
                key={idx}
                onClick={() => onQuickReplyClick(reply, messageIndex)}
                className="quick-reply-button"
              >
                {reply}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

const ChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const hasGreeted = useRef(false);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && !hasGreeted.current) {
      sendInitialGreeting();
      hasGreeted.current = true;
    }
  }, [isOpen]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const sendInitialGreeting = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: "", is_initial_greeting: true }),
      });

      if (!response.ok) throw new Error('Network response was not ok');

      const data = await response.json();
      setMessages([{ ...data, sender: 'bot' }]);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickReplyClick = (reply, messageIndex) => {
    setInput(reply);
    sendMessage(null, reply);

    // Remove quick replies from the clicked message
    setMessages((prevMessages) =>
      prevMessages.map((msg, idx) =>
        idx === messageIndex
          ? { ...msg, summary: { ...msg.summary, quick_replies: [] } }
          : msg
      )
    );
  };

  const sendMessage = async (e, quickReply = null) => {
    if (e) e.preventDefault();
    const messageText = quickReply || input;
    if (!messageText.trim()) return;

    setInput('');
    setIsLoading(true);
    setMessages((prev) => [...prev, { text: messageText, sender: 'user' }]);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: messageText }),
      });

      if (!response.ok) throw new Error('Network response was not ok');

      const data = await response.json();
      setMessages((prev) => [...prev, { ...data, sender: 'bot' }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages((prev) => [
        ...prev,
        {
          summary: {
            text: 'Sorry, there was an error processing your request.',
            quick_replies: [
              "What solar incentives are available?",
              "How much could I save with solar?",
              "Tell me about installation"
            ]
          },
          details: {},
          sender: 'bot'
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <div className={`chat-container ${isOpen ? 'visible' : 'hidden'}`}>
        <div className="chat-content">
          <div className="chat-header">
              <span>Soli</span>
          </div>
          
          <div className="messages">
            {messages.map((message, index) => (
              <div key={index} className={`message-wrapper ${message.sender}`}>
                {message.sender === 'bot' && (
                  <img src={botAvatar} alt="Bot Avatar" className="avatar" />
                )}
                <ChatMessage 
                  message={message}
                  onQuickReplyClick={handleQuickReplyClick}
                  messageIndex={index}
                />
              </div>
            ))}
            {isLoading && (
              <div className="message-wrapper">
                <img src={botAvatar} alt="Bot Avatar" className="avatar" />
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={sendMessage} className="input-form">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask me about solar energy..."
              disabled={isLoading}
            />
            <button 
              type="submit" 
              disabled={isLoading || !input.trim()}
            >
              <Send size={20} />
            </button>
          </form>
        </div>
      </div>

      <button 
        onClick={() => setIsOpen(!isOpen)}
        className="chat-toggle"
        aria-label={isOpen ? "Close chat" : "Open chat"}
      >
        {isOpen ? <X size={24} /> : <MessageCircle size={24} />}
      </button>
    </>
  );
};

export default ChatWidget;
