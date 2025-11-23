import { useState, useEffect, useRef } from 'react';
import { apiClient } from '../lib/api';

interface EmailTemplate {
  id: string;
  name: string;
  created_at: string;
  status: string;
  locale?: string;
  risk_score?: number;
}

export default function Home() {
  const [templates, setTemplates] = useState<EmailTemplate[]>([]);
  const [filteredTemplates, setFilteredTemplates] = useState<EmailTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<any>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchEmailTemplates();
  }, []);

  useEffect(() => {
    // Filter templates based on search term
    if (searchTerm) {
      const filtered = templates.filter(template => 
        template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (template.locale && template.locale.toLowerCase().includes(searchTerm.toLowerCase()))
      );
      setFilteredTemplates(filtered);
    } else {
      setFilteredTemplates(templates);
    }
  }, [searchTerm, templates]);

  const fetchEmailTemplates = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getEmails();
      setTemplates(response);
      setFilteredTemplates(response);
    } catch (err) {
      setError('Failed to fetch email templates');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleViewReport = (templateId: string) => {
    // Navigate to the detail page
    window.location.href = `/email/${templateId}`;
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    try {
      setUploading(true);

      // Upload file to backend
      const response = await apiClient.uploadHTML(file);

      // Set the result to display
      setUploadResult(response.report);
      
      // Refresh the template list
      fetchEmailTemplates();
      
      // Clear the file input
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (err) {
      setError('Failed to upload and analyze email');
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  const triggerFileInput = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pass': return 'bg-green-100 text-green-800';
      case 'fail': return 'bg-red-100 text-red-800';
      case 'needs_review': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 85) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-xl">Loading email templates...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-xl text-red-500">{error}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <h1 className="text-3xl font-bold text-gray-900">Email QA Dashboard</h1>
        </div>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-4">
            <a href="/" className="text-blue-600 hover:text-blue-800 font-medium">
              Dashboard
            </a>
            <a href="/admin" className="text-gray-500 hover:text-gray-700 font-medium">
              Admin Panel
            </a>
          </div>
        </div>
      </header>
      <main>
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
            {/* Search Bar */}
            <div className="mb-6">
              <div className="relative rounded-md shadow-sm">
                <input
                  type="text"
                  className="block w-full pl-3 pr-10 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                  placeholder="Enter email name or locale..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                />
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-semibold text-gray-800">Email Templates</h2>
              <div className="flex space-x-2">
                <button
                  onClick={fetchEmailTemplates}
                  className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                >
                  Refresh
                </button>
                <button
                  onClick={triggerFileInput}
                  disabled={uploading}
                  className={`bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  {uploading ? 'Uploading...' : 'Upload HTML'}
                </button>
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileUpload}
                  accept=".html,.htm"
                  className="hidden"
                />
              </div>
            </div>
            
            {uploadResult && (
              <div className="mb-6 bg-white shadow rounded-lg p-6">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-lg font-medium text-gray-900">Upload Analysis Result</h3>
                  <button 
                    onClick={() => setUploadResult(null)}
                    className="text-gray-500 hover:text-gray-700"
                  >
                    Close
                  </button>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-blue-50 p-4 rounded">
                    <h4 className="font-medium text-blue-800">Overall Status</h4>
                    <p className="text-2xl font-bold mt-2">{uploadResult.overall_status}</p>
                  </div>
                  <div className="bg-yellow-50 p-4 rounded">
                    <h4 className="font-medium text-yellow-800">Risk Score</h4>
                    <p className="text-2xl font-bold mt-2">{uploadResult.risk_score}/100</p>
                  </div>
                  <div className="bg-purple-50 p-4 rounded">
                    <h4 className="font-medium text-purple-800">Issues Found</h4>
                    <p className="text-2xl font-bold mt-2">{uploadResult.agentic_analysis?.top_issues?.length || 0}</p>
                  </div>
                </div>
                <div className="mt-4">
                  <button 
                    onClick={() => window.location.href = `/email/${uploadResult.email_id}`}
                    className="bg-indigo-600 hover:bg-indigo-700 text-white font-bold py-2 px-4 rounded"
                  >
                    View Detailed Report
                  </button>
                </div>
              </div>
            )}
            
            {/* Templates Table */}
            {filteredTemplates.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500">No email templates found</p>
              </div>
            ) : (
              <div className="bg-white shadow overflow-hidden sm:rounded-lg">
                <div className="px-4 py-5 sm:px-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900">Email Templates</h3>
                </div>
                <div className="border-t border-gray-200">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Template Name
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Locale
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Status
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          QA Score
                        </th>
                        <th scope="col" className="relative px-6 py-3">
                          <span className="sr-only">Actions</span>
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {filteredTemplates.map((template) => (
                        <tr key={template.id}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {template.name}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            {template.locale || 'N/A'}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(template.status)}`}>
                              {template.status.replace('_', ' ')}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                            <span className={getScoreColor(template.risk_score || 0)}>
                              {(template.risk_score || 0)}/100
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                            <button
                              onClick={() => handleViewReport(template.id)}
                              className="text-blue-600 hover:text-blue-900"
                            >
                              View Report
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div className="bg-gray-50 px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
                  <div className="text-sm text-gray-700">
                    Showing <span className="font-medium">{filteredTemplates.length}</span> of <span className="font-medium">{templates.length}</span> templates
                  </div>
                  <div className="text-sm text-gray-700">
                    Legend: PASS &ge; 85 | NEED REVIEW 60&ndash;85 | FAIL &lt; 60
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}