import { useState, useEffect, useRef } from 'react';
import TestResultCard from '../components/TestResultCard';
import { apiClient } from '../lib/api';

interface EmailTemplate {
  id: string;
  name: string;
  created_at: string;
  status: string;
}

export default function Home() {
  const [templates, setTemplates] = useState<EmailTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<any>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchEmailTemplates();
  }, []);

  const fetchEmailTemplates = async () => {
    try {
      setLoading(true);
      // In a real implementation, this would call your backend API
      const response = await apiClient.getEmails();
      setTemplates(response);
      
      // Mock data for demonstration
      // setTemplates([
      //   {
      //     id: 'template-1',
      //     name: 'Welcome Email',
      //     created_at: '2023-01-01T12:00:00Z',
      //     status: 'pass'
      //   },
      //   {
      //     id: 'template-2',
      //     name: 'Promotional Email',
      //     created_at: '2023-01-02T14:30:00Z',
      //     status: 'fail'
      //   },
      //   {
      //     id: 'template-3',
      //     name: 'Newsletter',
      //     created_at: '2023-01-03T09:15:00Z',
      //     status: 'needs_review'
      //   }
      // ]);
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
      </header>
      <main>
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          <div className="px-4 py-6 sm:px-0">
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
            
            {templates.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-gray-500">No email templates found</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {templates.map((template) => (
                  <TestResultCard
                    key={template.id}
                    template={template}
                    onViewReport={handleViewReport}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}