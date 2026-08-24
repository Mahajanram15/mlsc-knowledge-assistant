import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Bot, User, Info, FileText, ChevronDown, ChevronUp, AlertCircle, RefreshCw } from 'lucide-react';

interface Source {
  document: string;
  chunk_id: string;
  content?: string;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
  grounded?: boolean;
  retrievedChunks?: Source[];
}

const API_BASE_URL = 'http://localhost:8000/api';

function App() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'assistant',
      content: 'Hello! I am the MLSC Knowledge Assistant. I can answer questions based on the provided MLSC knowledge base. How can I help you today?'
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showInfo, setShowInfo] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input.trim()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_BASE_URL}/chat`, {
        question: userMessage.content
      });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.data.answer,
        sources: response.data.sources,
        grounded: response.data.grounded,
        retrievedChunks: response.data.retrieval?.chunks
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error fetching answer:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error while trying to answer your question. Please ensure the backend is running.',
        grounded: false
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestedQuestion = (question: string) => {
    setInput(question);
  };

  const SourceCard = ({ source }: { source: Source }) => {
    const [expanded, setExpanded] = useState(false);
    return (
      <div className="mt-2 bg-white border border-slate-200 rounded-md overflow-hidden text-sm">
        <button 
          onClick={() => setExpanded(!expanded)}
          className="w-full flex items-center justify-between px-3 py-2 bg-slate-50 hover:bg-slate-100 transition-colors text-left"
        >
          <div className="flex items-center gap-2 text-slate-700 font-medium">
            <FileText size={14} className="text-mlsc-blue" />
            {source.document}
          </div>
          {expanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </button>
        {expanded && source.content && (
          <div className="px-3 py-2 text-slate-600 bg-white border-t border-slate-100 text-xs leading-relaxed">
            {source.content}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="flex flex-col h-screen bg-mlsc-light">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 px-6 py-4 flex justify-between items-center shadow-sm z-10">
        <div className="flex items-center gap-3">
          <div className="bg-mlsc-blue text-white p-2 rounded-lg">
            <Bot size={24} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-800">MLSC Assistant</h1>
            <p className="text-xs text-slate-500 font-medium">RAG Knowledge System</p>
          </div>
        </div>
        <button 
          onClick={() => setShowInfo(!showInfo)}
          className="text-slate-500 hover:text-mlsc-blue transition-colors p-2 rounded-full hover:bg-slate-100"
        >
          <Info size={20} />
        </button>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Main Chat Area */}
        <main className="flex-1 flex flex-col relative max-w-5xl mx-auto w-full border-x border-slate-200 bg-white shadow-sm">
          
          {/* Chat Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6 chat-scroll">
            {messages.map((msg) => (
              <div key={msg.id} className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {msg.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center flex-shrink-0 text-mlsc-blue border border-slate-200">
                    <Bot size={18} />
                  </div>
                )}
                
                <div className={`max-w-[80%] ${msg.role === 'user' ? 'bg-mlsc-blue text-white rounded-2xl rounded-tr-sm px-5 py-3 shadow-sm' : 'bg-white border border-slate-200 text-slate-800 rounded-2xl rounded-tl-sm px-5 py-4 shadow-sm'}`}>
                  {msg.role === 'assistant' && msg.grounded === false && msg.id !== 'welcome' && (
                    <div className="flex items-center gap-1.5 text-amber-600 mb-2 text-xs font-medium bg-amber-50 px-2 py-1 rounded inline-flex">
                      <AlertCircle size={12} />
                      Unsupported Question
                    </div>
                  )}
                  
                  <div className="whitespace-pre-wrap leading-relaxed">{msg.content}</div>
                  
                  {msg.role === 'assistant' && msg.sources && msg.sources.length > 0 && (
                    <div className="mt-4 pt-3 border-t border-slate-100">
                      <p className="text-xs font-semibold text-slate-500 mb-2 uppercase tracking-wider">Sources Used</p>
                      <div className="space-y-2">
                        {msg.retrievedChunks?.filter(chunk => msg.sources?.some(s => s.chunk_id === chunk.chunk_id)).map((chunk, idx) => (
                          <SourceCard key={idx} source={chunk} />
                        ))}
                      </div>
                    </div>
                  )}
                </div>

                {msg.role === 'user' && (
                  <div className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center flex-shrink-0 text-white">
                    <User size={18} />
                  </div>
                )}
              </div>
            ))}
            
            {isLoading && (
              <div className="flex gap-4 justify-start">
                <div className="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center flex-shrink-0 text-mlsc-blue border border-slate-200">
                  <Bot size={18} />
                </div>
                <div className="bg-white border border-slate-200 text-slate-500 rounded-2xl rounded-tl-sm px-5 py-4 shadow-sm flex items-center gap-2">
                  <RefreshCw size={16} className="animate-spin text-mlsc-blue" />
                  Searching knowledge base...
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="p-4 bg-white border-t border-slate-200">
            {messages.length === 1 && (
              <div className="flex flex-wrap gap-2 mb-4 justify-center">
                {[
                  "What technical domains exist in MLSC?",
                  "How does the leadership structure work?",
                  "What happens during MLSC hackathons?",
                  "What is the salary of a domain lead?"
                ].map((q, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSuggestedQuestion(q)}
                    className="text-xs bg-slate-50 border border-slate-200 text-slate-600 px-3 py-1.5 rounded-full hover:bg-mlsc-blue hover:text-white hover:border-mlsc-blue transition-all"
                  >
                    {q}
                  </button>
                ))}
              </div>
            )}
            
            <form onSubmit={handleSubmit} className="flex gap-3">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about MLSC domains, leadership, hackathons..."
                className="flex-1 bg-slate-50 border border-slate-300 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-mlsc-blue focus:border-transparent transition-all"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={!input.trim() || isLoading}
                className="bg-mlsc-blue text-white px-5 rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center"
              >
                <Send size={20} />
              </button>
            </form>
            <div className="text-center mt-2">
              <span className="text-[10px] text-slate-400">AI can make mistakes. Check the provided sources for verification.</span>
            </div>
          </div>
        </main>

        {/* System Info Sidebar */}
        {showInfo && (
          <aside className="w-80 bg-white border-l border-slate-200 p-6 overflow-y-auto hidden md:block z-10 shadow-lg">
            <h2 className="text-lg font-bold text-slate-800 mb-6 flex items-center gap-2">
              <Info size={18} className="text-mlsc-blue" />
              System Info
            </h2>
            
            <div className="space-y-6">
              <div>
                <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">RAG Pipeline</h3>
                <div className="text-sm text-slate-700 bg-slate-50 p-3 rounded border border-slate-200 space-y-2">
                  <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-green-500"></div> Documents → Chunking</div>
                  <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-green-500"></div> Embeddings (all-MiniLM)</div>
                  <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-green-500"></div> FAISS Vector Search</div>
                  <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-green-500"></div> Top-K Context Selection</div>
                  <div className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-green-500"></div> Grounded LLM (Gemini)</div>
                </div>
              </div>

              <div>
                <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Knowledge Base</h3>
                <ul className="text-sm text-slate-700 space-y-1 bg-slate-50 p-3 rounded border border-slate-200">
                  <li>• about_mlsc.txt</li>
                  <li>• domains.txt</li>
                  <li>• leadership.txt</li>
                  <li>• membership.txt</li>
                  <li>• hackathons.txt</li>
                  <li>• code_of_conduct.txt</li>
                </ul>
              </div>

              <div>
                <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-2">Architecture</h3>
                <div className="text-sm text-slate-700">
                  <p><strong>Frontend:</strong> React + Vite + Tailwind</p>
                  <p><strong>Backend:</strong> FastAPI + LangChain</p>
                  <p><strong>Eval:</strong> Ragas Framework</p>
                </div>
              </div>
            </div>
          </aside>
        )}
      </div>
    </div>
  );
}

export default App;
