import { useState, useEffect } from 'react';
import axios from 'axios';
import TestResultCard from '../components/TestResultCard';

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

  useEffect(() => {
    fetchEmailTemplates();
  }, []);

  const fetchEmailTemplates = async () => {
    try {
      setLoading(true);
      // In a real implementation, this would call your backend API
      // const response = await axios.get('/api/v1/emails');
      // setTemplates(response.data);
      
      // Mock data for demonstration
      setTemplates([
        {
          id: 'template-1',
          name: 'Welcome Email',
          created_at: '2023-01-01T12:00:00Z',
          status: 'pass'
        },
        {
          id: 'template-2',
          name: 'Promotional Email',
          created_at: '2023-01-02T14:30:00Z',
          status: 'fail'
        },
        {
          id: 'template-3',
          name: 'Newsletter',
          created_at: '2023-01-03T09:15:00Z',
          status: 'needs_review'
        }
      ]);
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
              <button
                onClick={fetchEmailTemplates}
                className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
              >
                Refresh
              </button>
            </div>
            
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