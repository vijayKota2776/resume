import React, { useState } from 'react';
import { Upload, Save, User, Loader2, CheckCircle, Plus, Trash2 } from 'lucide-react';
import api from '../utils/api';
import { useNavigate } from 'react-router-dom';

const Profile = () => {
  const [isUploading, setIsUploading] = useState(false);
  const [isParsingText, setIsParsingText] = useState(false);
  const [rawText, setRawText] = useState('');
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    name: '',
    contact: '',
    summary: '',
    work_experience: [],
    education: [],
    skills: ''
  });

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const data = new FormData();
    data.append('file', file);

    setIsUploading(true);
    setError('');
    setMessage('');
    
    try {
      const res = await api.post('/api/parse-resume', data, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      const parsed = res.data.data;
      setFormData({
        name: parsed.name || parsed.full_name || '',
        contact: parsed.contact || parsed.email || '',
        summary: parsed.summary || '',
        work_experience: parsed.work_experience || [],
        education: parsed.education || [],
        skills: Array.isArray(parsed.skills) ? parsed.skills.join(', ') : (parsed.skills || '')
      });
      setMessage('Resume parsed successfully! Please review the fields below and save.');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to parse resume file');
    } finally {
      setIsUploading(false);
    }
  };

  const handleTextParse = async () => {
    if (!rawText.trim()) return;
    setIsParsingText(true);
    setError('');
    setMessage('');
    try {
      const res = await api.post('/api/parse-resume-text', { text: rawText });
      const parsed = res.data.data;
      setFormData({
        name: parsed.name || parsed.full_name || '',
        contact: parsed.contact || parsed.email || '',
        summary: parsed.summary || '',
        work_experience: parsed.work_experience || [],
        education: parsed.education || [],
        skills: Array.isArray(parsed.skills) ? parsed.skills.join(', ') : (parsed.skills || '')
      });
      setMessage('Text parsed successfully! Please review the fields below and save.');
      setRawText('');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to parse text');
    } finally {
      setIsParsingText(false);
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    setError('');
    setMessage('');

    try {
      const payload = {
        parsed_data: {
          ...formData,
          skills: formData.skills.split(',').map(s => s.trim()).filter(s => s)
        }
      };
      await api.post('/profile/manual', payload);
      setMessage('Profile saved successfully!');
      setTimeout(() => navigate('/tailor'), 1500);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save profile');
    } finally {
      setIsSaving(false);
    }
  };

  const addExperience = () => {
    setFormData({
      ...formData,
      work_experience: [...formData.work_experience, { role: '', company: '', dates: '', bullet_points: [''] }]
    });
  };

  const removeExperience = (index) => {
    const newExp = [...formData.work_experience];
    newExp.splice(index, 1);
    setFormData({ ...formData, work_experience: newExp });
  };

  const updateExperience = (index, field, value) => {
    const newExp = [...formData.work_experience];
    newExp[index][field] = value;
    setFormData({ ...formData, work_experience: newExp });
  };

  const updateBullet = (expIndex, bulletIndex, value) => {
    const newExp = [...formData.work_experience];
    newExp[expIndex].bullet_points[bulletIndex] = value;
    setFormData({ ...formData, work_experience: newExp });
  };

  const addBullet = (expIndex) => {
    const newExp = [...formData.work_experience];
    if (!newExp[expIndex].bullet_points) newExp[expIndex].bullet_points = [];
    newExp[expIndex].bullet_points.push('');
    setFormData({ ...formData, work_experience: newExp });
  };

  const addEducation = () => {
    setFormData({
      ...formData,
      education: [...formData.education, { degree: '', institution: '', year: '' }]
    });
  };

  const removeEducation = (index) => {
    const newEdu = [...formData.education];
    newEdu.splice(index, 1);
    setFormData({ ...formData, education: newEdu });
  };

  const updateEducation = (index, field, value) => {
    const newEdu = [...formData.education];
    newEdu[index][field] = value;
    setFormData({ ...formData, education: newEdu });
  };

  return (
    <div className="max-w-4xl mx-auto pb-20">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-3xl font-bold text-gray-900">My Profile</h2>
          <p className="text-gray-500 mt-1">Upload your existing resume or fill out the details manually.</p>
        </div>
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
        >
          {isSaving ? <Loader2 className="w-5 h-5 animate-spin mr-2" /> : <Save className="w-5 h-5 mr-2" />}
          Save Profile
        </button>
      </div>

      {error && <div className="mb-4 p-4 bg-red-50 text-red-700 rounded-lg border border-red-100">{error}</div>}
      {message && <div className="mb-4 p-4 bg-green-50 text-green-700 rounded-lg border border-green-100 flex items-center"><CheckCircle className="w-5 h-5 mr-2"/>{message}</div>}

      <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 mb-8 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-800">Auto-fill with AI</h3>
            <p className="text-sm text-gray-500">Upload your PDF or DOCX resume to automatically extract your information.</p>
          </div>
          <label className={`flex items-center px-4 py-2 border border-gray-300 rounded-lg shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 cursor-pointer ${isUploading ? 'opacity-50 pointer-events-none' : ''}`}>
            {isUploading ? <Loader2 className="w-5 h-5 animate-spin mr-2" /> : <Upload className="w-5 h-5 mr-2 text-indigo-500" />}
            {isUploading ? 'Parsing...' : 'Upload File'}
            <input type="file" className="hidden" accept=".pdf,.docx,.txt" onChange={handleFileUpload} />
          </label>
        </div>
        
        <div className="border-t border-gray-100 pt-4">
          <p className="text-sm text-gray-500 mb-2">Or paste your resume details as plain text:</p>
          <div className="flex flex-col sm:flex-row gap-3">
            <textarea
              className="flex-1 p-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 resize-none h-24 text-sm"
              placeholder="Paste your LinkedIn export or plain text resume here..."
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
            />
            <button
              onClick={handleTextParse}
              disabled={isParsingText || !rawText.trim()}
              className="px-4 py-2 bg-gray-800 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50 text-sm font-medium h-fit whitespace-nowrap flex items-center"
            >
              {isParsingText ? <Loader2 className="w-4 h-4 animate-spin mr-2" /> : null}
              {isParsingText ? 'Parsing Text...' : 'Parse Text'}
            </button>
          </div>
        </div>
      </div>

      <div className="space-y-6">
        {/* Basic Info */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center">
            <User className="w-5 h-5 mr-2 text-indigo-500"/> Personal Information
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
              <input type="text" className="w-full p-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Contact Info (Email/Phone)</label>
              <input type="text" className="w-full p-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500" value={formData.contact} onChange={e => setFormData({...formData, contact: e.target.value})} />
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">Professional Summary</label>
              <textarea className="w-full p-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 min-h-[100px]" value={formData.summary} onChange={e => setFormData({...formData, summary: e.target.value})} />
            </div>
          </div>
        </div>

        {/* Experience */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-800">Work Experience</h3>
            <button onClick={addExperience} className="text-indigo-600 hover:text-indigo-800 text-sm font-medium flex items-center">
              <Plus className="w-4 h-4 mr-1" /> Add Job
            </button>
          </div>
          <div className="space-y-6">
            {formData.work_experience.map((exp, index) => (
              <div key={index} className="p-4 border border-gray-200 rounded-lg relative">
                <button onClick={() => removeExperience(index)} className="absolute top-4 right-4 text-gray-400 hover:text-red-500"><Trash2 className="w-4 h-4" /></button>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4 pr-8">
                  <div>
                    <label className="block text-xs font-medium text-gray-500 mb-1">Role/Title</label>
                    <input type="text" className="w-full p-2 border border-gray-300 rounded-md text-sm" value={exp.role || ''} onChange={e => updateExperience(index, 'role', e.target.value)} />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-500 mb-1">Company</label>
                    <input type="text" className="w-full p-2 border border-gray-300 rounded-md text-sm" value={exp.company || ''} onChange={e => updateExperience(index, 'company', e.target.value)} />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-500 mb-1">Dates</label>
                    <input type="text" className="w-full p-2 border border-gray-300 rounded-md text-sm" value={exp.dates || ''} onChange={e => updateExperience(index, 'dates', e.target.value)} />
                  </div>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-2">Bullet Points</label>
                  <div className="space-y-2">
                    {(exp.bullet_points || []).map((bullet, bIndex) => (
                      <div key={bIndex} className="flex items-start">
                        <span className="text-gray-400 mr-2 mt-2">•</span>
                        <textarea className="flex-1 p-2 border border-gray-300 rounded-md text-sm min-h-[40px] resize-none" value={bullet} onChange={e => updateBullet(index, bIndex, e.target.value)} />
                      </div>
                    ))}
                  </div>
                  <button onClick={() => addBullet(index)} className="mt-2 text-indigo-600 hover:text-indigo-800 text-xs font-medium flex items-center">
                    <Plus className="w-3 h-3 mr-1" /> Add Bullet Point
                  </button>
                </div>
              </div>
            ))}
            {formData.work_experience.length === 0 && <p className="text-sm text-gray-500 italic">No work experience added yet.</p>}
          </div>
        </div>

        {/* Education */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-semibold text-gray-800">Education</h3>
            <button onClick={addEducation} className="text-indigo-600 hover:text-indigo-800 text-sm font-medium flex items-center">
              <Plus className="w-4 h-4 mr-1" /> Add Education
            </button>
          </div>
          <div className="space-y-4">
            {formData.education.map((edu, index) => (
              <div key={index} className="flex gap-4 items-start relative p-4 border border-gray-200 rounded-lg">
                <div className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-4 pr-6">
                  <div>
                    <label className="block text-xs font-medium text-gray-500 mb-1">Degree</label>
                    <input type="text" className="w-full p-2 border border-gray-300 rounded-md text-sm" value={edu.degree || ''} onChange={e => updateEducation(index, 'degree', e.target.value)} />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-500 mb-1">Institution</label>
                    <input type="text" className="w-full p-2 border border-gray-300 rounded-md text-sm" value={edu.institution || ''} onChange={e => updateEducation(index, 'institution', e.target.value)} />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-gray-500 mb-1">Year</label>
                    <input type="text" className="w-full p-2 border border-gray-300 rounded-md text-sm" value={edu.year || ''} onChange={e => updateEducation(index, 'year', e.target.value)} />
                  </div>
                </div>
                <button onClick={() => removeEducation(index)} className="absolute top-4 right-4 text-gray-400 hover:text-red-500"><Trash2 className="w-4 h-4" /></button>
              </div>
            ))}
            {formData.education.length === 0 && <p className="text-sm text-gray-500 italic">No education added yet.</p>}
          </div>
        </div>

        {/* Skills */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Skills</h3>
          <p className="text-xs text-gray-500 mb-2">Enter your skills separated by commas (e.g., Python, React, Data Analysis).</p>
          <textarea 
            className="w-full p-2 border border-gray-300 rounded-md focus:ring-indigo-500 focus:border-indigo-500 min-h-[80px]" 
            value={formData.skills} 
            onChange={e => setFormData({...formData, skills: e.target.value})} 
          />
        </div>

      </div>
    </div>
  );
};

export default Profile;
