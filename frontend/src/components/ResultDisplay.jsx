import React from 'react';
import { AlertTriangle, CheckCircle, ShieldX } from 'lucide-react';

const ResultDisplay = ({ result }) => {
  if (!result) return null;

  const { classification, score } = result;
  
  const getStyle = () => {
    switch(classification) {
      case 'Phishing':
        return {
          icon: <ShieldX className="w-16 h-16 text-rose-500" />,
          color: 'text-rose-500',
          bg: 'bg-rose-500/10',
          border: 'border-rose-500/20',
          progress: 'bg-rose-500'
        };
      case 'Suspicious':
        return {
          icon: <AlertTriangle className="w-16 h-16 text-amber-500" />,
          color: 'text-amber-500',
          bg: 'bg-amber-500/10',
          border: 'border-amber-500/20',
          progress: 'bg-amber-500'
        };
      case 'Safe':
      default:
        return {
          icon: <CheckCircle className="w-16 h-16 text-emerald-500" />,
          color: 'text-emerald-500',
          bg: 'bg-emerald-500/10',
          border: 'border-emerald-500/20',
          progress: 'bg-emerald-500'
        };
    }
  };

  const style = getStyle();

  return (
    <div className={`mt-8 w-full max-w-3xl mx-auto rounded-2xl shadow-xl overflow-hidden border ${style.border} ${style.bg} backdrop-blur-sm p-8 transition-all duration-500 animate-in fade-in slide-in-from-bottom-4`}>
      <div className="flex flex-col md:flex-row items-center gap-8">
        <div className="flex-shrink-0 animate-pulse">
          {style.icon}
        </div>
        
        <div className="flex-grow space-y-4 text-center md:text-left w-full">
          <div>
            <h3 className={`text-4xl font-extrabold tracking-tight ${style.color}`}>
              {classification}
            </h3>
            <p className="text-slate-300 mt-2 font-medium">
              We analyzed {result.url}
            </p>
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-sm font-medium">
              <span className="text-slate-400">Threat Probability</span>
              <span className="text-slate-200">{(score * 100).toFixed(1)}%</span>
            </div>
            <div className="h-3 w-full bg-slate-800 rounded-full overflow-hidden">
              <div 
                className={`h-full ${style.progress} transition-all duration-1000 ease-out`}
                style={{ width: `${score * 100}%` }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ResultDisplay;
