import React, { useState, useEffect } from 'react';
import { 
  Loader2, Download, Send, Clock, CheckCircle, 
  XCircle, AlertTriangle, FileText, Sparkles 
} from 'lucide-react';
import { Link } from 'react-router-dom';
import api from '../utils/api';

const Tailor = () => {
  const [jdText, setJdText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRefining, setIsRefining] = useState(false);
  
  const [currentResume, setCurrentResume] = useState(null);
  const [versions, setVersions] = useState([]);
  const [selectedVersionId, setSelectedVersionId] = useState(null);
  const [selectedTemplate, setSelectedTemplate] = useState('modern');
  
  const [feedback, setFeedback] = useState('');
  const [chatMessages, setChatMessages] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchVersions();
  }, []);

  const fetchVersions = async () => {
    try {
      const res = await api.get('/api/resume-versions');
      setVersions(res.data);
      if (res.data.length > 0 && !currentResume) {
        const latest = res.data[0];
        setCurrentResume(latest.data);
        setSelectedVersionId(latest.id);
      }
    } catch (err) {
      console.error('Failed to fetch versions', err);
    }
  };

  const handleGenerate = async () => {
    if (!jdText.trim()) {
      setError('Please enter a job description');
      return;
    }
    setError('');
    setIsLoading(true);
    try {
      const res = await api.post('/api/tailor-resume', { jd_text: jdText });
      const newVersion = { id: res.data.id, version: res.data.version, data: res.data.data, created_at: res.data.created_at };
      setCurrentResume(newVersion.data);
      setSelectedVersionId(newVersion.id);
      
      // Prepend to versions to update list immediately
      setVersions([newVersion, ...versions]);
    } catch (err) {
      if (err.response?.status === 404) {
        setError('No profile found. Please create your profile first.');
      } else {
        setError(err.response?.data?.detail || 'Failed to generate tailored resume');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleRefine = async () => {
    if (!feedback.trim()) return;
    setIsRefining(true);
    setError('');
    
    // Optimistically add user message
    const userMsg = { role: 'user', content: feedback };
    setChatMessages([...chatMessages, userMsg]);
    const currentFeedback = feedback;
    setFeedback('');
    
    try {
      const res = await api.post('/api/refine-resume', {
        current_resume_json: currentResume,
        feedback: currentFeedback,
        jd_text: jdText || "Not provided in this session"
      });
      
      const newVersion = { id: res.data.id, version: res.data.version, data: res.data.data, created_at: res.data.created_at };
      setCurrentResume(newVersion.data);
      setSelectedVersionId(newVersion.id);
      setVersions([newVersion, ...versions]);
      
      setChatMessages(prev => [...prev, { role: 'ai', content: `Updated to Version ${newVersion.version}` }]);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to refine resume');
    } finally {
      setIsRefining(false);
    }
  };

  const handleDownload = async () => {
    if (!selectedVersionId) return;
    try {
      const response = await api.post('/api/generate-pdf', {
        version_id: selectedVersionId,
        template: selectedTemplate
      }, {
        responseType: 'blob' // Important for downloading binary data
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      // Try to get filename from content-disposition header if available
      const contentDisposition = response.headers['content-disposition'];
      let filename = 'tailored_resume.pdf';
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
        if (filenameMatch && filenameMatch.length === 2) {
          filename = filenameMatch[1];
        }
      }
      
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
    } catch (err) {
      setError('Failed to download PDF. The LaTeX compiler might have encountered an issue.');
      console.error(err);
    }
  };

  const handleVersionSelect = (verId) => {
    const ver = versions.find(v => v.id === parseInt(verId));
    if (ver) {
      setSelectedVersionId(ver.id);
      setCurrentResume(ver.data);
      setChatMessages(prev => [...prev, { role: 'system', content: `Reverted preview to Version ${ver.version}` }]);
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6 pb-20">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">Tailor Resume</h2>
          <p className="text-gray-500 mt-1">Paste a job description to get started.</p>
        </div>
        
        {/* Version Selector */}
        {versions.length > 0 && (
          <div className="flex items-center space-x-3 bg-white p-2 rounded-lg shadow-sm border border-gray-100">
            <Clock className="w-5 h-5 text-gray-400" />
            <select 
              value={selectedVersionId || ''} 
              onChange={(e) => handleVersionSelect(e.target.value)}
              className="bg-transparent border-none text-sm font-medium focus:ring-0 text-gray-700"
            >
              {versions.map(v => (
                <option key={v.id} value={v.id}>
                  Version {v.version} - {new Date(v.created_at).toLocaleString()}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-r-md">
          <div className="flex items-center">
            <AlertTriangle className="h-5 w-5 text-red-500 mr-2" />
            <p className="text-red-700">{error}</p>
          </div>
          {error.includes('No profile found') && (
            <Link to="/profile" className="text-red-700 font-bold underline mt-2 inline-block">Go to Profile Setup</Link>
          )}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* LEFT COLUMN: Input */}
        <div className="lg:col-span-1 space-y-4">
          <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-100 h-full flex flex-col">
            <label className="flex items-center text-sm font-semibold text-gray-700 mb-2">
              <Briefcase className="w-4 h-4 mr-2 text-indigo-500"/>
              Job Description
            </label>
            <textarea
              className="w-full flex-1 min-h-[300px] p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent resize-none text-sm"
              placeholder="Paste the full job posting here..."
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
            />
            <button
              onClick={handleGenerate}
              disabled={isLoading}
              className="mt-4 w-full flex items-center justify-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {isLoading ? (
                <><Loader2 className="animate-spin w-5 h-5 mr-2" /> Processing...</>
              ) : (
                <><Sparkles className="w-5 h-5 mr-2" /> Generate Tailored Resume</>
              )}
            </button>
          </div>
        </div>

        {/* RIGHT COLUMN: Results Preview */}
        <div className="lg:col-span-2 space-y-6">
          {currentResume ? (
            <>
              {/* ATS & Keywords Card */}
              <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6">
                  <h3 className="text-lg font-bold text-gray-900 flex items-center">
                    <CheckCircle className="w-5 h-5 mr-2 text-green-500" />
                    ATS Analysis
                  </h3>
                  <div className="mt-2 sm:mt-0 flex items-center space-x-3">
                    <span className="text-sm font-medium text-gray-500">Score:</span>
                    <div className="w-32 bg-gray-200 rounded-full h-2.5">
                      <div 
                        className={`h-2.5 rounded-full ${currentResume.ats_score > 80 ? 'bg-green-500' : currentResume.ats_score > 60 ? 'bg-yellow-400' : 'bg-red-500'}`}
                        style={{ width: `${currentResume.ats_score || 85}%` }}
                      ></div>
                    </div>
                    <span className="font-bold text-gray-800">{currentResume.ats_score || 85}/100</span>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="font-semibold text-gray-700 block mb-2">Matched Keywords</span>
                    <div className="flex flex-wrap gap-1">
                      {(currentResume.matched_keywords || []).map((kw, i) => (
                        <span key={i} className="bg-green-50 text-green-700 px-2 py-1 rounded border border-green-200">{kw}</span>
                      ))}
                      {(!currentResume.matched_keywords || currentResume.matched_keywords.length === 0) && <span className="text-gray-400 italic">None specifically identified</span>}
                    </div>
                  </div>
                  <div>
                    <span className="font-semibold text-gray-700 block mb-2">Missing Keywords</span>
                    <div className="flex flex-wrap gap-1">
                      {(currentResume.missing_keywords || []).map((kw, i) => (
                        <span key={i} className="bg-red-50 text-red-700 px-2 py-1 rounded border border-red-200">{kw}</span>
                      ))}
                      {(!currentResume.missing_keywords || currentResume.missing_keywords.length === 0) && <span className="text-gray-400 italic">None missing!</span>}
                    </div>
                  </div>
                </div>
              </div>

              {/* Resume Preview Card */}
              <div className="bg-white p-8 rounded-xl shadow-sm border border-gray-100 font-sans">
                <div className="flex justify-between items-start border-b pb-4 mb-4">
                  <h3 className="text-xl font-bold text-gray-900 flex items-center">
                    <FileText className="w-6 h-6 mr-2 text-gray-500" />
                    Document Preview
                  </h3>
                  
                  {/* Download Controls */}
                  <div className="flex items-center space-x-2 bg-gray-50 p-1.5 rounded-lg border">
                    <select 
                      value={selectedTemplate} 
                      onChange={(e) => setSelectedTemplate(e.target.value)}
                      className="bg-white border-gray-300 text-sm rounded-md py-1.5 focus:ring-indigo-500 focus:border-indigo-500"
                    >
                      <option value="modern">Modern Template</option>
                      <option value="classic">Classic Template</option>
                    </select>
                    <button 
                      onClick={handleDownload}
                      className="flex items-center px-3 py-1.5 bg-gray-800 text-white text-sm font-medium rounded-md hover:bg-gray-700 transition-colors"
                    >
                      <Download className="w-4 h-4 mr-1.5" />
                      Download PDF
                    </button>
                  </div>
                </div>

                {/* Simulated Document Formatting */}
                <div className="space-y-6 text-gray-800 text-sm leading-relaxed">
                  <section>
                    <h4 className="font-bold text-gray-900 border-b border-gray-200 uppercase tracking-wider mb-2">Summary</h4>
                    <p>{currentResume.summary}</p>
                  </section>

                  <section>
                    <h4 className="font-bold text-gray-900 border-b border-gray-200 uppercase tracking-wider mb-2 mt-6">Experience</h4>
                    <div className="space-y-4">
                      {(currentResume.work_experience || []).map((exp, i) => (
                        <div key={i}>
                          <div className="flex justify-between font-bold">
                            <span>{exp.role}</span>
                            <span className="text-gray-600 font-normal">{exp.dates}</span>
                          </div>
                          <div className="text-indigo-600 font-medium mb-1">{exp.company}</div>
                          <ul className="list-disc pl-5 space-y-1">
                            {(exp.bullet_points || []).map((bullet, j) => (
                              <li key={j}>{bullet}</li>
                            ))}
                          </ul>
                        </div>
                      ))}
                    </div>
                  </section>

                  <section>
                    <h4 className="font-bold text-gray-900 border-b border-gray-200 uppercase tracking-wider mb-2 mt-6">Education</h4>
                    {(currentResume.education || []).map((edu, i) => (
                      <div key={i} className="mb-2">
                        <div className="flex justify-between font-bold">
                          <span>{edu.degree}</span>
                          <span className="text-gray-600 font-normal">{edu.year}</span>
                        </div>
                        <div>{edu.institution}</div>
                      </div>
                    ))}
                  </section>

                  <section>
                    <h4 className="font-bold text-gray-900 border-b border-gray-200 uppercase tracking-wider mb-2 mt-6">Skills</h4>
                    <p>{Array.isArray(currentResume.skills) ? currentResume.skills.join(', ') : currentResume.skills}</p>
                  </section>
                </div>
              </div>

              {/* Refinement Chat */}
              <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden flex flex-col">
                <div className="bg-gray-50 border-b px-4 py-3 font-semibold text-gray-700 flex items-center">
                  <Sparkles className="w-4 h-4 mr-2 text-indigo-500" />
                  Refine with AI
                </div>
                
                {chatMessages.length > 0 && (
                  <div className="p-4 max-h-48 overflow-y-auto space-y-3 bg-gray-50 border-b">
                    {chatMessages.map((msg, idx) => (
                      <div key={idx} className={`text-sm ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
                        <span className={`inline-block px-3 py-2 rounded-lg ${
                          msg.role === 'user' ? 'bg-indigo-600 text-white' : 
                          msg.role === 'system' ? 'bg-gray-200 text-gray-600 text-xs italic' :
                          'bg-white border text-gray-800 shadow-sm'
                        }`}>
                          {msg.content}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
                
                <div className="p-3 bg-white flex items-center">
                  <input
                    type="text"
                    className="flex-1 border-0 focus:ring-0 text-sm px-3 py-2 bg-gray-100 rounded-lg mr-3"
                    placeholder="E.g., Make the summary more impactful..."
                    value={feedback}
                    onChange={(e) => setFeedback(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleRefine()}
                    disabled={isRefining}
                  />
                  <button 
                    onClick={handleRefine}
                    disabled={isRefining || !feedback.trim()}
                    className="p-2.5 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50 transition-colors"
                  >
                    {isRefining ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                  </button>
                </div>
              </div>
            </>
          ) : (
            <div className="h-full bg-gray-50 border-2 border-dashed border-gray-200 rounded-xl flex items-center justify-center p-12 text-center">
              <div>
                <FileText className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900">No Preview Available</h3>
                <p className="mt-1 text-sm text-gray-500">Paste a job description and click generate to see your tailored resume here.</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Simple Briefcase icon fallback since it wasn't requested in the import explicitly but is used above.
const Briefcase = ({className}) => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={className}><rect width="20" height="14" x="2" y="7" rx="2" ry="2"/><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/></svg>
);

export default Tailor;
