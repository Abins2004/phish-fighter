import React from 'react';
import { Target, AlertCircle, FileCode2, Info, Download, Globe, Activity } from 'lucide-react';
import html2pdf from 'html2pdf.js';

const ExplainabilityView = ({ explainData, result }) => {
  if (!explainData) return null;

  const { highlighted_elements = [], risk_factors = [], threat_intel, predictive_basis = [] } = explainData;

  const handleDownloadPdf = () => {
    const element = document.getElementById('forensic-report-container');
    const opt = {
      margin:       10,
      filename:     `PhishFighter_Report_${new Date().toISOString().slice(0,10)}.pdf`,
      image:        { type: 'jpeg', quality: 0.98 },
      html2canvas:  { scale: 2, useCORS: true, backgroundColor: '#1e293b' }, // matches slate-800
      jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
    };
    
    html2pdf().set(opt).from(element).save();
  };

  return (
    <div className="mt-8 w-full max-w-3xl mx-auto bg-slate-800 rounded-2xl shadow-xl overflow-hidden border border-slate-700 animate-in fade-in slide-in-from-bottom-6 duration-700">
      <div className="border-b border-slate-700 p-6 flex justify-between items-center bg-slate-800/50">
        <h3 className="text-xl font-semibold text-slate-100 flex items-center gap-2">
          <Info className="w-5 h-5 text-blue-400" />
          Forensic Threat Report
        </h3>
        <button 
          onClick={handleDownloadPdf}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600/20 hover:bg-blue-600 border border-blue-500/30 text-blue-400 hover:text-white rounded-lg transition-all text-sm font-medium"
        >
          <Download size={16} />
          Export PDF
        </button>
      </div>

      <div id="forensic-report-container" className="p-6">
        {result && (
          <div className="mb-8 p-4 bg-slate-900/50 rounded-xl border border-slate-700">
            <h4 className="text-slate-400 text-sm font-medium mb-2 uppercase tracking-wider">Target Signature</h4>
            <p className="text-slate-200 font-mono break-all">{result.url}</p>
            <div className="flex gap-6 mt-4">
              <div>
                <span className="text-slate-500 text-xs">AI Verdict</span>
                <p className={`font-bold ${result.classification === 'Phishing' ? 'text-rose-500' : result.classification === 'Suspicious' ? 'text-amber-500' : 'text-emerald-500'}`}>
                  {result.classification}
                </p>
              </div>
              <div>
                <span className="text-slate-500 text-xs">Risk Matrix</span>
                <p className="font-mono text-slate-300">{(result.score * 100).toFixed(1)}%</p>
              </div>
            </div>
          </div>
        )}

        {/* Global Threat Intelligence */}
        {threat_intel && threat_intel.status !== "disabled" && (
          <div className="mb-6">
            <h4 className="flex items-center gap-2 text-slate-300 font-medium pb-2 border-b border-slate-700/50">
              <Globe className="w-4 h-4 text-emerald-400" />
              Global Threat Intelligence (VirusTotal)
            </h4>
            <div className="mt-3 bg-slate-900/50 p-4 rounded-lg border border-slate-800 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
              <div>
                <p className="text-slate-300">
                  Vendors Flagging as Malicious: <strong className={threat_intel.malicious_votes > 0 ? "text-rose-500" : "text-emerald-500"}>{threat_intel.malicious_votes || 0} / {threat_intel.total_votes || 0}</strong>
                </p>
                <p className="text-xs text-slate-500 mt-1">{threat_intel.message || "Scanned against 90+ global security vendors"}</p>
              </div>
              {threat_intel.permalink && (
                <a href={threat_intel.permalink} target="_blank" rel="noreferrer" className="px-3 py-1.5 bg-blue-600/20 text-blue-400 rounded hover:bg-blue-600 hover:text-white transition-colors text-sm shrink-0 border border-blue-500/30">
                  View VT Report
                </a>
              )}
            </div>
          </div>
        )}

        {/* ML Prediction Basis */}
        {predictive_basis.length > 0 && (
          <div className="mb-6">
            <h4 className="flex items-center gap-2 text-slate-300 font-medium pb-2 border-b border-slate-700/50">
              <Activity className="w-4 h-4 text-purple-400" />
              AI Prediction Basis (LightGBM Decision Matrix)
            </h4>
            <div className="mt-3 grid grid-cols-1 sm:grid-cols-3 gap-4">
              {predictive_basis.map((basis, idx) => (
                <div key={idx} className="bg-slate-900/50 p-4 rounded-lg border border-slate-800 border-l-2 border-l-purple-500">
                  <p className="text-slate-400 text-xs font-mono mb-1 text-purple-400 uppercase tracking-widest">Heuristic #{idx + 1}</p>
                  <p className="text-slate-200 font-semibold mb-2 break-words">{basis.feature}</p>
                  <p className="text-slate-500 text-xs mt-1">Relative Math Priority: <span className="font-mono text-purple-400">{basis.weight}</span></p>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Risk Factors */}
        <div className="space-y-4">
          <h4 className="flex items-center gap-2 text-slate-300 font-medium pb-2 border-b border-slate-700/50">
            <AlertCircle className="w-4 h-4 text-rose-400" />
            Key Risk Factors
          </h4>
          {risk_factors.length > 0 ? (
            <ul className="space-y-3">
              {risk_factors.map((factor, idx) => (
                <li key={idx} className="flex gap-3 text-slate-400 bg-slate-900/50 p-3 rounded-lg border border-slate-800">
                  <span className="text-rose-500 shrink-0 mt-0.5">•</span>
                  <span className="text-sm">{factor}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-slate-500 text-sm">No specific high-risk heuristics triggered.</p>
          )}
        </div>

        {/* DOM Highlights */}
        <div className="space-y-4">
          <h4 className="flex items-center gap-2 text-slate-300 font-medium pb-2 border-b border-slate-700/50">
            <FileCode2 className="w-4 h-4 text-indigo-400" />
            Suspicious Elements
          </h4>
          {highlighted_elements.length > 0 ? (
            <div className="space-y-3">
              {highlighted_elements.map((el, idx) => (
                <div key={idx} className="bg-slate-900/50 p-3 rounded-lg border border-slate-800">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="px-2 py-0.5 rounded bg-indigo-500/20 text-indigo-400 text-xs font-mono border border-indigo-500/20">
                      &lt;{el.tag}&gt;
                    </span>
                  </div>
                  <p className="text-sm text-slate-400">{el.reason}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-slate-500 text-sm">No specifically matched structural threats.</p>
          )}
        </div>
        </div>
      </div>
    </div>
  );
};

export default ExplainabilityView;
