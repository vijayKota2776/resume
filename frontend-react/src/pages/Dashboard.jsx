import React from 'react';
import { useNavigate } from 'react-router-dom';
import { LayoutTemplate, FileText, CheckCircle } from 'lucide-react';

const Dashboard = () => {
  const navigate = useNavigate();

  const handleSelectTemplate = (templateName) => {
    // In the future, this could save the preference to user profile.
    // For now, navigate to tailor page where they can generate a resume.
    navigate('/tailor', { state: { selectedTemplate: templateName } });
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-20">
      <div>
        <h2 className="text-3xl font-bold text-gray-900 mb-2">My Dashboard</h2>
        <p className="text-gray-500">Track your applications and select your preferred resume style.</p>
      </div>
      
      {/* Quick Stats (Mocked until Firebase Migration) */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center">
          <div className="p-3 rounded-lg bg-indigo-50 text-indigo-600 mr-4">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Tailored Resumes</p>
            <p className="text-2xl font-bold text-gray-900">0</p>
          </div>
        </div>
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex items-center">
          <div className="p-3 rounded-lg bg-green-50 text-green-600 mr-4">
            <CheckCircle className="w-6 h-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-gray-500">Applications Sent</p>
            <p className="text-2xl font-bold text-gray-900">0</p>
          </div>
        </div>
      </div>

      {/* Template Gallery */}
      <div>
        <div className="flex items-center mb-6">
          <LayoutTemplate className="w-6 h-6 text-indigo-500 mr-2" />
          <h3 className="text-xl font-bold text-gray-900">Resume Template Gallery</h3>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          
          {/* Modern Template */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-shadow group">
            <div className="h-64 overflow-hidden bg-gray-50 border-b relative">
              <img 
                src="/images/modern.jpg" 
                alt="Modern Template" 
                className="w-full object-cover object-top opacity-90 group-hover:opacity-100 transition-opacity"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-gray-900/40 to-transparent flex items-end p-4">
                <span className="bg-indigo-600 text-white text-xs font-bold px-2 py-1 rounded-md uppercase tracking-wider">Most Popular</span>
              </div>
            </div>
            <div className="p-6">
              <h4 className="text-xl font-bold text-gray-900 mb-2">Modern Clean</h4>
              <p className="text-sm text-gray-500 mb-6 line-clamp-2">
                A sleek, single-column design with minimalist typography and clear section headers. Highly ATS-friendly and perfect for tech, marketing, and modern corporate roles.
              </p>
              <button 
                onClick={() => handleSelectTemplate('modern')}
                className="w-full py-2.5 bg-gray-900 text-white rounded-lg font-medium hover:bg-gray-800 transition-colors"
              >
                Use This Template
              </button>
            </div>
          </div>

          {/* Classic Template */}
          <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden hover:shadow-md transition-shadow group">
            <div className="h-64 overflow-hidden bg-gray-50 border-b relative">
              <img 
                src="/images/classic.jpg" 
                alt="Classic Template" 
                className="w-full object-cover object-top opacity-90 group-hover:opacity-100 transition-opacity"
              />
            </div>
            <div className="p-6">
              <h4 className="text-xl font-bold text-gray-900 mb-2">Classic Two-Column</h4>
              <p className="text-sm text-gray-500 mb-6 line-clamp-2">
                A traditional two-column layout that fits more information on a single page. Features serif typography and a dedicated sidebar for skills. Great for experienced professionals.
              </p>
              <button 
                onClick={() => handleSelectTemplate('classic')}
                className="w-full py-2.5 bg-gray-100 text-gray-800 border border-gray-200 rounded-lg font-medium hover:bg-gray-200 transition-colors"
              >
                Use This Template
              </button>
            </div>
          </div>

        </div>
      </div>

    </div>
  );
};

export default Dashboard;
