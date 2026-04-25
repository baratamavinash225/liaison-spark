import React, { useState, useRef, useEffect } from 'react';

type Message = {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  plan?: string;
  code?: string;
  errors?: string;
  loading?: boolean;
};

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'assistant',
      content: 'Hello! I am Liaison-Spark, your Autonomous Big Data Analyst. What insights do you want to extract from your Data Lake today?'
    }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage: Message = { id: Date.now().toString(), role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    const tempAssistantId = (Date.now() + 1).toString();
    setMessages(prev => [...prev, { id: tempAssistantId, role: 'assistant', content: 'Analyzing schema and planning execution...', loading: true }]);

    try {
      const response = await fetch("http://localhost:8000/api/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: userMessage.content })
      });

      if (!response.ok) {
        const errData = await response.json();
        throw new Error(errData.detail || "Something went wrong");
      }

      const data = await response.json();
      
      setMessages(prev => prev.map(msg => 
        msg.id === tempAssistantId 
          ? { 
              ...msg, 
              content: data.chat_response ? data.chat_response : 'Here is the generated Spark logic based on your request:', 
              loading: false,
              plan: data.plan,
              code: data.code,
              errors: data.errors
            }
          : msg
      ));
    } catch (err: any) {
      setMessages(prev => prev.map(msg => 
        msg.id === tempAssistantId 
          ? { ...msg, content: `Error: ${err.message}`, loading: false }
          : msg
      ));
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', backgroundColor: '#f9f9f9', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
      
      {/* Header */}
      <header style={{ padding: '1rem 2rem', backgroundColor: '#ffffff', borderBottom: '1px solid #e5e5e5', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
        <h1 style={{ margin: 0, fontSize: '1.25rem', color: '#1a1a1a' }}>Liaison-Spark: The Autonomous Big Data Analyst</h1>
      </header>

      {/* Chat Area */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '2rem', display: 'flex', flexDirection: 'column', gap: '1.5rem', scrollBehavior: 'smooth' }}>
        <div style={{ maxWidth: '800px', margin: '0 auto', width: '100%', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          {messages.map((msg) => (
            <div key={msg.id} style={{ display: 'flex', gap: '1rem', flexDirection: msg.role === 'user' ? 'row-reverse' : 'row' }}>
              
              {/* Avatar */}
              <div style={{
                width: '36px', height: '36px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                backgroundColor: msg.role === 'user' ? '#007aff' : '#10a37f', color: '#fff', fontSize: '1.2rem'
              }}>
                {msg.role === 'user' ? '👤' : '🤖'}
              </div>

              {/* Message Bubble */}
              <div style={{
                backgroundColor: msg.role === 'user' ? '#007aff' : '#ffffff',
                color: msg.role === 'user' ? '#ffffff' : '#333333',
                padding: '1rem 1.25rem',
                borderRadius: '12px',
                borderTopRightRadius: msg.role === 'user' ? '4px' : '12px',
                borderTopLeftRadius: msg.role === 'assistant' ? '4px' : '12px',
                maxWidth: '85%',
                boxShadow: msg.role === 'assistant' ? '0 2px 5px rgba(0,0,0,0.05)' : 'none',
                border: msg.role === 'assistant' ? '1px solid #e5e5e5' : 'none'
              }}>
                {/* Content */}
                <div style={{ lineHeight: '1.5', whiteSpace: 'pre-wrap' }}>
                  {msg.content}
                </div>

                {msg.loading && (
                  <div style={{ marginTop: '0.5rem', color: '#666', fontStyle: 'italic', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <div className="spinner" style={{width: '12px', height: '12px', border: '2px solid #ccc', borderTopColor: '#10a37f', borderRadius: '50%', animation: 'spin 1s linear infinite'}}></div>
                    Working on it...
                  </div>
                )}

                {/* Optional Assistant Data (Plan, Code, Errors) */}
                {msg.plan && (
                  <div style={{ marginTop: '1rem' }}>
                    <details style={{ backgroundColor: '#f0f4f8', padding: '0.75rem', borderRadius: '6px', marginBottom: '1rem', border: '1px solid #d9e2ec' }}>
                      <summary style={{ cursor: 'pointer', fontWeight: 'bold', color: '#334e68' }}>🧠 Architect Plan</summary>
                      <pre style={{ marginTop: '0.5rem', fontSize: '0.85rem', overflowX: 'auto', whiteSpace: 'pre-wrap', color: '#486581' }}>
                        {msg.plan}
                      </pre>
                    </details>
                    
                    {msg.errors ? (
                      <div style={{ backgroundColor: '#fff3cd', color: '#856404', padding: '0.75rem', borderRadius: '6px', marginBottom: '1rem', border: '1px solid #ffeeba', fontSize: '0.9rem' }}>
                        <strong>⚠️ QA Issues Detected:</strong>
                        <div style={{ marginTop: '0.25rem' }}>{msg.errors}</div>
                      </div>
                    ) : (
                      <div style={{ backgroundColor: '#d4edda', color: '#155724', padding: '0.5rem 0.75rem', borderRadius: '6px', marginBottom: '1rem', border: '1px solid #c3e6cb', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span>✅</span> <strong>QA Approved</strong>
                      </div>
                    )}

                    <div style={{ position: 'relative' }}>
                      <div style={{ backgroundColor: '#282c34', color: '#abb2bf', padding: '1rem', borderRadius: '6px', overflowX: 'auto', fontSize: '0.9rem', border: '1px solid #21252b' }}>
                        <pre style={{ margin: 0, fontFamily: '"Fira Code", monospace' }}>
                          <code>{msg.code}</code>
                        </pre>
                      </div>
                    </div>
                  </div>
                )}

              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div style={{ padding: '1.5rem', backgroundColor: '#ffffff', borderTop: '1px solid #e5e5e5' }}>
        <div style={{ maxWidth: '800px', margin: '0 auto', position: 'relative' }}>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask Liaison-Spark to generate a PySpark job..."
            disabled={loading}
            style={{
              width: '100%',
              padding: '1rem 4rem 1rem 1rem',
              borderRadius: '12px',
              border: '1px solid #d1d5db',
              fontSize: '1rem',
              resize: 'none',
              minHeight: '60px',
              maxHeight: '200px',
              boxShadow: '0 2px 6px rgba(0,0,0,0.05)',
              boxSizing: 'border-box',
              fontFamily: 'inherit',
              backgroundColor: loading ? '#f3f4f6' : '#ffffff'
            }}
            rows={1}
          />
          <button
            onClick={handleSend}
            disabled={loading || !input.trim()}
            style={{
              position: 'absolute',
              right: '0.75rem',
              bottom: '0.75rem',
              height: '36px',
              width: '36px',
              borderRadius: '8px',
              backgroundColor: (loading || !input.trim()) ? '#e5e5e5' : '#10a37f',
              color: '#ffffff',
              border: 'none',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: (loading || !input.trim()) ? 'not-allowed' : 'pointer',
              transition: 'background-color 0.2s'
            }}
          >
            <svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" height="20" width="20" xmlns="http://www.w3.org/2000/svg">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          </button>
        </div>
        <div style={{ textAlign: 'center', fontSize: '0.8rem', color: '#999', marginTop: '0.75rem' }}>
          Liaison-Spark can make mistakes. Verify important PySpark jobs before execution.
        </div>
      </div>
      
      {/* Global Styles for Spinner */}
      <style>
        {`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}
      </style>
    </div>
  );
};

export default App;
