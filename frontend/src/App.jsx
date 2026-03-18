import React, { useState } from 'react';
import axios from 'axios';
import UrlInput from './components/UrlInput';
import ResultDisplay from './components/ResultDisplay';
import ExplainabilityView from './components/ExplainabilityView';
import Dashboard from './components/Dashboard';
import { ShieldAlert, BarChart3, Search } from 'lucide-react';

function App() {
  const [currentView, setCurrentView] = useState('scanner');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleAnalyze = async (url, rawText = null) => {
    setIsLoading(true);
    setResult(null);
    setError(null);
    
    try {
      // In a real environment, this would point to the FastAPI backend URL
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      
      const payload = { url };
      if (rawText) payload.raw_text = rawText;
      
      const response = await axios.post(`${apiUrl}/api/analyze-url`, payload);
      setResult(response.data);
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail || 
        'Failed to connect to the analysis engine. Please ensure the backend is running.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 selection:bg-blue-500/30">
      {/* Background Decor */}
      <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden flex items-center justify-center">
        <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-blue-600/20 blur-[120px] rounded-full mix-blend-screen" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-indigo-600/20 blur-[120px] rounded-full mix-blend-screen" />
      </div>

      {/* Main Content */}
      <main className="relative z-10 container mx-auto px-4 py-16 flex flex-col items-center min-h-screen">
        
        {/* Header / Nav */}
        <header className="w-full flex justify-between items-center mb-10 border-b border-gray-800 pb-6">
          <div className="flex items-center gap-3 text-2xl font-bold bg-gradient-to-r from-slate-100 to-slate-400 bg-clip-text text-transparent cursor-pointer" onClick={() => setCurrentView('scanner')}>
            <ShieldAlert className="text-blue-500" size={32} />
            Phish Fighter
          </div>
          
          <nav className="flex space-x-2 bg-gray-900/50 p-1 rounded-lg border border-gray-800 backdrop-blur-sm">
            <button 
              onClick={() => setCurrentView('scanner')}
              className={`flex items-center gap-2 px-4 py-2 rounded-md transition-all ${currentView === 'scanner' ? 'bg-blue-600 shadow-lg text-white' : 'text-gray-400 hover:text-white hover:bg-gray-800'}`}
            >
              <Search size={18} />
              <span>Live Scanner</span>
            </button>
            <button 
              onClick={() => setCurrentView('dashboard')}
              className={`flex items-center gap-2 px-4 py-2 rounded-md transition-all ${currentView === 'dashboard' ? 'bg-blue-600 shadow-lg text-white' : 'text-gray-400 hover:text-white hover:bg-gray-800'}`}
            >
              <BarChart3 size={18} />
              <span>Global Intelligence</span>
            </button>
          </nav>
        </header>

        {/* View Router */}
        {currentView === 'scanner' ? (
          <section className="w-full flex-grow flex flex-col items-center justify-start space-y-8 max-w-5xl mx-auto pt-8">
            <UrlInput onAnalyze={handleAnalyze} isLoading={isLoading} />
            
            {error && (
              <div className="w-full max-w-3xl animate-in fade-in p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400 text-center">
                {error}
              </div>
            )}

            {result && (
              <div className="w-full space-y-6 animate-in slide-in-from-bottom-4 duration-500">
                <ResultDisplay result={result} />
                
                {result.explainability && (
                  <ExplainabilityView explainData={result.explainability} result={result} />
                )}
              </div>
            )}
          </section>
        ) : (
          <section className="w-full flex-grow max-w-6xl mx-auto pt-4 animate-in fade-in">
            <Dashboard />
          </section>
        )}

        {/* Footer */}
        <footer className="w-full text-center mt-16 text-slate-500 text-sm">
          <p>© {new Date().getFullYear()} Phish Fighter. Advanced Threat Detection System.</p>
        </footer>
      </main>
    </div>
  );
}

export default App;
