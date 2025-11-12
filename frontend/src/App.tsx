import React, { useState } from 'react';
import { ChatInterface } from './components/ChatInterface';
import { VoiceInterface } from './components/VoiceInterface';
import { AgentDashboard } from './components/AgentDashboard';
import { MessageSquare, Mic, BarChart3 } from 'lucide-react';

type Tab = 'chat' | 'voice' | 'dashboard';

function App() {
  const [activeTab, setActiveTab] = useState<Tab>('chat');

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <h1 className="text-2xl font-bold text-gray-900">AI Agent System</h1>
        </div>
      </header>

      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            <button
              onClick={() => setActiveTab('chat')}
              className={`flex items-center space-x-2 py-4 border-b-2 transition ${
                activeTab === 'chat'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <MessageSquare size={20} />
              <span>Chat</span>
            </button>
            <button
              onClick={() => setActiveTab('voice')}
              className={`flex items-center space-x-2 py-4 border-b-2 transition ${
                activeTab === 'voice'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <Mic size={20} />
              <span>Voice</span>
            </button>
            <button
              onClick={() => setActiveTab('dashboard')}
              className={`flex items-center space-x-2 py-4 border-b-2 transition ${
                activeTab === 'dashboard'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              <BarChart3 size={20} />
              <span>Dashboard</span>
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="h-[calc(100vh-200px)]">
          {activeTab === 'chat' && <ChatInterface />}
          {activeTab === 'voice' && <VoiceInterface />}
          {activeTab === 'dashboard' && <AgentDashboard />}
        </div>
      </main>
    </div>
  );
}

export default App;

