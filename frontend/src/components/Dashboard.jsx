import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip as RechartsTooltip, Legend } from 'recharts';
import { Activity, ShieldAlert, ShieldCheck, AlertTriangle } from 'lucide-react';

const COLORS = ['#ef4444', '#f59e0b', '#22c55e']; // Red (Phishing), Yellow (Suspicious), Green (Safe)

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get('http://localhost:8000/api/stats');
        setStats(response.data);
      } catch (err) {
        setError('Failed to load threat analytics. Is the backend running?');
      } finally {
        setLoading(false);
      }
    };
    
    fetchStats();
    // Refresh every 15 seconds
    const interval = setInterval(fetchStats, 15000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="text-center p-12 text-gray-400">Loading Threat Intelligence Data...</div>;
  if (error) return <div className="text-center p-12 text-red-400">{error}</div>;

  const { metrics, recent } = stats;
  
  const pieData = [
    { name: 'Phishing', value: metrics.phishing },
    { name: 'Suspicious', value: metrics.suspicious },
    { name: 'Safe', value: metrics.safe },
  ];

  return (
    <div className="space-y-6">
      
      {/* Top Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gray-800 border border-gray-700 p-6 rounded-xl flex items-center justify-between">
          <div>
            <p className="text-gray-400 mb-1">Total Scans</p>
            <h3 className="text-3xl font-bold text-white">{metrics.total}</h3>
          </div>
          <div className="p-3 bg-blue-500/20 rounded-full text-blue-400"><Activity size={24} /></div>
        </div>
        
        <div className="bg-gray-800 border border-red-900/50 p-6 rounded-xl flex items-center justify-between">
          <div>
            <p className="text-gray-400 mb-1">Critical Threats</p>
            <h3 className="text-3xl font-bold text-red-500">{metrics.phishing}</h3>
          </div>
          <div className="p-3 bg-red-500/20 rounded-full text-red-500"><ShieldAlert size={24} /></div>
        </div>
        
        <div className="bg-gray-800 border border-yellow-900/50 p-6 rounded-xl flex items-center justify-between">
          <div>
            <p className="text-gray-400 mb-1">Suspicious Sites</p>
            <h3 className="text-3xl font-bold text-yellow-500">{metrics.suspicious}</h3>
          </div>
          <div className="p-3 bg-yellow-500/20 rounded-full text-yellow-500"><AlertTriangle size={24} /></div>
        </div>
        
        <div className="bg-gray-800 border border-green-900/50 p-6 rounded-xl flex items-center justify-between">
          <div>
            <p className="text-gray-400 mb-1">Safe Sites</p>
            <h3 className="text-3xl font-bold text-green-500">{metrics.safe}</h3>
          </div>
          <div className="p-3 bg-green-500/20 rounded-full text-green-500"><ShieldCheck size={24} /></div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Pie Chart */}
        <div className="bg-gray-800 border border-gray-700 p-6 rounded-xl lg:col-span-1">
          <h3 className="text-xl font-semibold mb-6 flex items-center text-gray-200">
             Threat Distribution
          </h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                  stroke="none"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <RechartsTooltip 
                  contentStyle={{ backgroundColor: '#1f2937', borderColor: '#374151', color: '#fff' }}
                  itemStyle={{ color: '#fff' }}
                />
                <Legend verticalAlign="bottom" height={36}/>
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        
        {/* Recent Scans Table */}
        <div className="bg-gray-800 border border-gray-700 p-6 rounded-xl lg:col-span-2 overflow-hidden flex flex-col">
          <h3 className="text-xl font-semibold mb-4 text-gray-200">Live Threat Feed</h3>
          <div className="flex-1 overflow-auto">
            <table className="w-full text-left text-sm">
              <thead className="text-gray-400 border-b border-gray-700">
                <tr>
                  <th className="pb-3 font-medium">Target URL</th>
                  <th className="pb-3 font-medium">Risk Score</th>
                  <th className="pb-3 font-medium">Verdict</th>
                  <th className="pb-3 font-medium">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-700">
                {recent.map((row, idx) => (
                  <tr key={idx} className="hover:bg-gray-700/50 transition-colors">
                    <td className="py-3 text-gray-300 max-w-[200px] truncate pr-4" title={row.url}>{row.url}</td>
                    <td className="py-3 text-gray-300 font-mono">{row.score}%</td>
                    <td className="py-3">
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${
                        row.classification === 'Phishing' ? 'bg-red-500/20 text-red-400 border border-red-500/30' : 
                        row.classification === 'Suspicious' ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/30' : 
                        'bg-green-500/20 text-green-400 border border-green-500/30'
                      }`}>
                        {row.classification}
                      </span>
                    </td>
                    <td className="py-3 text-gray-500 text-xs">{row.date}</td>
                  </tr>
                ))}
                {recent.length === 0 && (
                  <tr>
                    <td colSpan="4" className="py-8 text-center text-gray-500">No telemetry data recorded yet.</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
