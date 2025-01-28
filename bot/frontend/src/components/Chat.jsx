import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, Send, X } from 'lucide-react';
import './Chat.css';
import botAvatar from '../assets/launcher-logo.png';

const ChatMessage = ({ message }) => {
  if (message.sender === 'user') {
    return <div className="message user">{message.text}</div>;
  }

  // For bot messages with the new structure
  const { summary, details } = message;
  
  return (
    <div className="message bot">
      {/* Summary Section */}
      <div className="summary-section">
        {/* <h3 className="font-bold mb-2">Summary</h3> */}
        <p className="mb-2">{summary.text}</p>
        <br /> {/* Empty line */}
        {summary.actions && summary.actions.length > 0 && (
          <>
            <h4 className="font-semibold mt-2">Recommended Next Steps:</h4>
            <ul>
              {summary.actions.map((action, idx) => (
                <li key={idx}>{action}</li>
              ))}
            </ul>
          </>
        )}
      </div>

      {/* Expert Details (Collapsible) */}
      {/* {details && Object.keys(details).length > 0 && (
        <div className="expert-details mt-4">
          <div className="collapsible-section">
            <details>
              <summary className="font-semibold cursor-pointer p-2 bg-gray-100 rounded hover:bg-gray-200 transition-colors">
                Technical Assessment
              </summary>
              <div className="p-2">
                <p>{details.technical.assessment}</p>
                {details.technical.recommendations && (
                  <ul className="list-disc pl-4 mt-2">
                    {details.technical.recommendations.map((rec, idx) => (
                      <li key={idx}>{rec}</li>
                    ))}
                  </ul>
                )}
              </div>
            </details>
          </div>

          <div className="collapsible-section mt-2">
            <details>
              <summary className="font-semibold cursor-pointer p-2 bg-gray-100 rounded hover:bg-gray-200 transition-colors">
                Financial Analysis
              </summary>
              <div className="p-2">
                <p>{details.financial.analysis}</p>
                {details.financial.steps && (
                  <ul className="list-disc pl-4 mt-2">
                    {details.financial.steps.map((step, idx) => (
                      <li key={idx}>{step}</li>
                    ))}
                  </ul>
                )}
              </div>
            </details>
          </div>

          <div className="collapsible-section mt-2">
            <details>
              <summary className="font-semibold cursor-pointer p-2 bg-gray-100 rounded hover:bg-gray-200 transition-colors">
                Policy Insights
              </summary>
              <div className="p-2">
                <p>{details.policy.overview}</p>
                {details.policy.incentives && (
                  <ul className="list-disc pl-4 mt-2">
                    {details.policy.incentives.map((incentive, idx) => (
                      <li key={idx}>{incentive}</li>
                    ))}
                  </ul>
                )}
              </div>
            </details>
          </div>
        </div>
      )} */}
    </div>
  );
};

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
      
      setMessages((prev) => [...prev, { 
        ...data,
        sender: 'bot' 
      }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages((prev) => [
        ...prev,
        { 
          summary: { 
            text: 'Sorry, there was an error processing your request.',
            actions: []
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
      <div className={`chat-container ${isOpen ? 'visible': 'hidden'}`}>
        {isOpen && (
          <div className="chat-content">
            <div className="chat-header">
              <div className="flex items-center gap-2">
                {/* <img src={botAvatar} alt="Bot Avatar" className="w-6 h-6" /> */}
                <span>Chat Support</span>
              </div>
              <button onClick={toggleChat} className={`chat-toggle ${isOpen ? 'open' : ''}`}>
                {isOpen ? <X size={24} /> : <MessageCircle size={24} />}
              </button>
            </div>
            <div className="messages">
              {messages.map((message, index) => (
                <div key={index} className={`message-wrapper ${message.sender}`}>
                  {message.sender === 'bot' && (
                    <img src={botAvatar} alt="Bot Avatar" className="avatar" />
                  )}
                  <ChatMessage message={message} />
                </div>
              ))}
              {isLoading && (
                <div className="loading">
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
                placeholder="Ask me a question about solar energy..."
                disabled={isLoading}
                className="flex-1 p-3 border-0 focus:outline-none focus:ring-0"
              />
              <button 
                type="submit" 
                disabled={isLoading || !input.trim()}
                className="p-3 text-blue-600 hover:bg-gray-100 disabled:text-gray-400 disabled:hover:bg-transparent transition-colors"
              >
                <Send size={20} />
              </button>
            </form>
          </div>
        )}
      </div>
      <button 
        onClick={toggleChat} 
        className={`chat-toggle ${isOpen ? 'hidden' : ''}`}
      >
        <MessageCircle size={24} />
      </button>
    </>
  );
};

export default ChatWidget;