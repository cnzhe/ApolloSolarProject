import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, Send, X } from 'lucide-react';
import './Chat.css';
import botAvatar from '../assets/launcher-logo.png';

const ChatWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;
  
    const userMessage = input;
    setInput('');
    setIsLoading(true);
  
    setMessages((prev) => [...prev, { text: userMessage, sender: 'user' }]);
  
    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage }),
      });
  
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
  
      const data = await response.json();
      // If a final answer is returned, append it
      if (data.response && data.response.trim()) {
        setMessages((prev) => [...prev, { text: data.response, sender: 'bot' }]);
      } else {
        // Handle any ongoing conversation or error message
        setMessages((prev) => [
          ...prev,
          { text: 'Sorry, there was an error processing your request.', sender: 'bot' },
        ]);
      }
    } catch (error) {
      console.error('Error:', error);
      setMessages((prev) => [
        ...prev,
        { text: 'Sorry, there was an error processing your request.', sender: 'bot' },
      ]);
    } finally {
      setIsLoading(false);
    }
  };  

  return (
    <>
    <div className={`chat-container ${isOpen ? 'visible': 'hidden'}`}>
      {isOpen && (
        <div className="chat-content">
          <div className="chat-header">Chat Support</div>
          <div className="messages">
            {messages.map((message, index) => (
              <div key={index} className={`message-wrapper ${message.sender}`}>
                {message.sender === 'bot' && (
                  <img src={botAvatar} alt="Bot Avatar" className="avatar" />
                )}
                <div className={`message ${message.sender}`}>
                  {message.text}
                </div>
              </div>
            ))}
            {isLoading && <div className="loading">Bot is typing...</div>}
            <div ref={messagesEndRef} />
          </div>
          <form onSubmit={sendMessage} className="input-form">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type a message..."
              disabled={isLoading}
            />
            {/* <button type="submit" disabled={isLoading || !input.trim()}>
              <Send size={20} />
            </button> */}
          </form>
        </div>
      )}
    </div>
    <button onClick={toggleChat} className={`chat-toggle ${isOpen ? 'open' : ''}`}>
        {isOpen ? <X size={24} /> : <MessageCircle size={24} />}
    </button>
    </>
  );
};

export default ChatWidget;
