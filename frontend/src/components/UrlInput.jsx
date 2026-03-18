import React, { useState, useEffect } from 'react';
import { ShieldAlert, Search, Loader2, QrCode, FileText, Link as LinkIcon, Upload } from 'lucide-react';
import jsQR from 'jsqr';

const UrlInput = ({ onAnalyze, isLoading }) => {
  const [inputType, setInputType] = useState('url'); // 'url', 'qr', 'text'
  const [url, setUrl] = useState('');
  const [rawText, setRawText] = useState('');

  // Auto-scan current tab if running inside Chrome Extension
  useEffect(() => {
    if (typeof chrome !== 'undefined' && chrome.tabs) {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (tabs && tabs[0] && tabs[0].url) {
          const activeUrl = tabs[0].url;
          // Ignore internal browser pages
          if (!activeUrl.startsWith('chrome://') && !activeUrl.startsWith('edge://')) {
            setUrl(activeUrl);
            onAnalyze(activeUrl);
          }
        }
      });
    }
  }, []); // Run once on component mount

  const handleSubmit = (e) => {
    e.preventDefault();
    if (inputType === 'url' && url.trim()) {
      onAnalyze(url);
    } else if (inputType === 'text' && rawText.trim()) {
      const urlRegex = /(https?:\/\/[^\s]+)/g;
      const matches = rawText.match(urlRegex);
      if (matches && matches.length > 0) {
        setUrl(matches[0]);
        // Note: We could pass the rawText to the backend as well for NLP processing
        onAnalyze(matches[0], rawText);
      } else {
        alert("No identifiable HTTP/HTTPS URLs found in this text block.");
      }
    }
  };

  const handleFileUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (event) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        canvas.width = img.width;
        canvas.height = img.height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0);
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        
        const code = jsQR(imageData.data, imageData.width, imageData.height);
        if (code) {
          setUrl(code.data);
          onAnalyze(code.data);
        } else {
          alert('AI could not detect any QR code payload in this image. Is it blurry?');
        }
      };
      img.src = event.target.result;
    };
    reader.readAsDataURL(file);
  };

  return (
    <div className="w-full max-w-3xl mx-auto bg-slate-800 rounded-2xl shadow-xl overflow-hidden border border-slate-700">
      <div className="p-8 text-center">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-500/10 text-blue-400 mb-6">
          <ShieldAlert size={32} />
        </div>
        <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent mb-4">
          Phish Fighter
        </h2>
        <p className="text-slate-400 mb-6 max-w-lg mx-auto">
          Multi-modal detection system analyzing links, QR images, and manipulative text in real-time.
        </p>

        {/* Multi-modal Tabs */}
        <div className="flex justify-center gap-2 mb-8">
          <button 
            type="button"
            onClick={() => setInputType('url')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${inputType === 'url' ? 'bg-blue-600/20 text-blue-400 border border-blue-500/30' : 'bg-slate-900/50 text-slate-400 hover:text-slate-200 border border-transparent'}`}
          >
            <LinkIcon size={18} /> Direct URL
          </button>
          <button 
            type="button"
            onClick={() => setInputType('qr')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${inputType === 'qr' ? 'bg-purple-600/20 text-purple-400 border border-purple-500/30' : 'bg-slate-900/50 text-slate-400 hover:text-slate-200 border border-transparent'}`}
          >
            <QrCode size={18} /> QR Image
          </button>
          <button 
            type="button"
            onClick={() => setInputType('text')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium transition-all ${inputType === 'text' ? 'bg-emerald-600/20 text-emerald-400 border border-emerald-500/30' : 'bg-slate-900/50 text-slate-400 hover:text-slate-200 border border-transparent'}`}
          >
            <FileText size={18} /> Raw Email / SMS
          </button>
        </div>

        {inputType === 'url' && (
          <form onSubmit={handleSubmit} className="relative group">
            <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400 group-focus-within:text-blue-400 transition-colors">
              <Search size={20} />
            </div>
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="Enter URL to scan (e.g., https://example.com)"
              required
              className="w-full pl-12 pr-36 py-4 bg-slate-900/50 border border-slate-700 rounded-xl text-lg text-slate-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all placeholder:text-slate-500"
            />
            <button
              type="submit"
              disabled={isLoading || !url}
              className="absolute inset-y-2 right-2 px-6 flex items-center gap-2 bg-blue-600 hover:bg-blue-500 disabled:bg-slate-700 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors"
            >
              {isLoading ? (
                <>
                  <Loader2 size={18} className="animate-spin" />
                  Scanning...
                </>
              ) : (
                'Analyze URL'
              )}
            </button>
          </form>
        )}

        {inputType === 'qr' && (
          <div className="w-full border-2 border-dashed border-slate-700 hover:border-purple-500/50 transition-colors rounded-xl bg-slate-900/50 p-8 flex flex-col items-center justify-center group relative overflow-hidden">
            <input 
              type="file" 
              accept="image/*" 
              onChange={handleFileUpload} 
              disabled={isLoading}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10 disabled:cursor-not-allowed" 
            />
            {isLoading ? (
              <div className="flex flex-col items-center gap-3 text-purple-400">
                 <Loader2 size={32} className="animate-spin" />
                 <p className="font-medium">Decoding Payload...</p>
              </div>
            ) : (
              <div className="flex flex-col items-center gap-3 text-slate-400 group-hover:text-purple-400 transition-colors">
                 <Upload size={32} />
                 <p className="font-medium">Click or Drag malicious QR Code image here</p>
                 <p className="text-xs text-slate-500">Supports PNG, JPG, JPEG</p>
              </div>
            )}
          </div>
        )}

        {inputType === 'text' && (
          <form onSubmit={handleSubmit} className="relative flex flex-col items-end gap-3">
            <textarea
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              placeholder="Paste suspicious Email or SMS text here. AI will detect manipulative language and extract hidden URLs automatically..."
              required
              rows={4}
              className="w-full p-4 bg-slate-900/50 border border-slate-700 rounded-xl text-slate-200 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all placeholder:text-slate-500 resize-none font-sans"
            />
            <button
              type="submit"
              disabled={isLoading || !rawText}
              className="px-6 py-3 flex items-center gap-2 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-700 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors w-full sm:w-auto justify-center"
            >
              {isLoading ? (
                <>
                  <Loader2 size={18} className="animate-spin" />
                  Extracting URL...
                </>
              ) : (
                'Extract & Scan Payload'
              )}
            </button>
          </form>
        )}
      </div>
    </div>
  );
};

export default UrlInput;
