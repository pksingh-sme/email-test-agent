import { useRouter } from 'next/router';
import { useState, useEffect } from 'react';
import axios from 'axios';
import HtmlPreview from '../../components/HtmlPreview';

interface EmailDetails {
  id: string;
  html_content: string;
  metadata: {
    subject: string;
    preheader: string;
    template_name: string;
    locale: string;
    created_at: string;
  };
}

interface TestResult {
  test_name: string;
  status: 'pass' | 'fail';
  details: string;
}

interface AgentAnalysis {
  overall_status: string;
  risk_score: number;
  risk_level: string;
  compliance_analysis: {
    issues: Array<{ rule: string; description: string; severity: string }>;
  };
  tone_analysis: {
    issues: Array<{ rule: string; description: string; severity: string }>;
  };
  accessibility_analysis: {
    issues: Array<{ rule: string; description: string; severity: string }>;
  };
  deterministic_results: TestResult[];
  fix_suggestions: Array<{ type: string; issue: string; description: string; suggestion: string; priority: string }>;
}

export default function EmailDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [emailDetails, setEmailDetails] = useState<EmailDetails | null>(null);
  const [analysis, setAnalysis] = useState<AgentAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [runningQA, setRunningQA] = useState(false);

  useEffect(() => {
    if (id) {
      fetchEmailDetails();
    }
  }, [id]);

  const fetchEmailDetails = async () => {
    try {
      setLoading(true);
      // In a real implementation, this would call your backend API
      // const response = await axios.get(`/api/v1/emails/${id}`);
      // setEmailDetails(response.data);
      
      // Mock data for demonstration
      setEmailDetails({
        id: id as string,
        html_content: '<html><body><h1>Welcome to Our Service</h1><p>Thank you for joining us. We\'re excited to have you on board!</p><img src="https://example.com/logo.png" alt="Company Logo"></body></html>',
        metadata: {
          subject: 'Welcome to Our Service',
          preheader: 'Thank you for joining us',
          template_name: 'Welcome Email',
          locale: 'en-US',
          created_at: '2023-01-01T12:00:00Z'
        }
      });
      
      // Also fetch analysis if available
      fetchAnalysis();
    } catch (err) {
      setError('Failed to fetch email details');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  const fetchAnalysis = async () => {
    try {
      // In a real implementation, this would call your backend API
      // const response = await axios.post(`/api/v1/emails/${id}/qa`);
      // setAnalysis(response.data.report);
      
      // Mock data for demonstration
      setAnalysis({
        overall_status: 'needs_review',
        risk_score: 65,
        risk_level: 'medium',
        compliance_analysis: {
          issues: [
            { rule: 'font_compliance', description: 'Font does not match brand guidelines', severity: 'medium' },
            { rule: 'cta_color_compliance', description: 'CTA button color does not match brand guidelines', severity: 'medium' }
          ]
        },
        tone_analysis: {
          issues: [
            { rule: 'clarity', description: 'Text contains excessive passive voice constructions', severity: 'low' }
          ]
        },
        accessibility_analysis: {
          issues: [
            { rule: 'alt_text_quality', description: 'Image has non-descriptive ALT text: \'Company Logo\'', severity: 'medium' }
          ]
        },
        deterministic_results: [
          { test_name: 'alt_text', status: 'fail', details: 'Image missing descriptive ALT text' },
          { test_name: 'subject_line', status: 'pass', details: 'Subject line present' },
          { test_name: 'preheader', status: 'pass', details: 'Preheader present' }
        ],
        fix_suggestions: [
          { type: 'accessibility', issue: 'alt_text_quality', description: 'Image has non-descriptive ALT text', suggestion: 'Improve ALT text descriptiveness: Company Logo', priority: 'medium' },
          { type: 'compliance', issue: 'font_compliance', description: 'Font does not match brand guidelines', suggestion: 'Update font family to brand standard: Arial', priority: 'medium' }
        ]
      });
    } catch (err) {
      console.error('Failed to fetch analysis', err);
    }
  };

  const runQA = async () => {
    if (!id) return;
    
    try {
      setRunningQA(true);
      // In a real implementation, this would call your backend API
      // const response = await axios.post(`/api/v1/emails/${id}/qa`, { email_id: id });
      // setAnalysis(response.data.report);
      
      // Mock delay for demonstration
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Use existing mock data
      fetchAnalysis();
    } catch (err) {
      setError('Failed to run QA analysis');
      console.error(err);
    } finally {
      setRunningQA(false);
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

  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'low': return 'bg-green-100 text-green-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'high': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-xl">Loading email details...</div>
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

  if (!emailDetails) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-xl">Email not found</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <h1 className="text-3xl font-bold text-gray-900">Email QA Report</h1>
            <button
              onClick={() => router.push('/')}
              className="bg-gray-500 hover:bg-gray-700 text-white font-bold py-2 px-4 rounded"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </header>
      
      <main>
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          {/* Email Metadata */}
          <div className="bg-white shadow overflow-hidden sm:rounded-lg mb-6">
            <div className="px-4 py-5 sm:px-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900">Email Information</h3>
            </div>
            <div className="border-t border-gray-200">
              <dl>
                <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                  <dt className="text-sm font-medium text-gray-500">Template Name</dt>
                  <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{emailDetails.metadata.template_name}</dd>
                </div>
                <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                  <dt className="text-sm font-medium text-gray-500">Subject</dt>
                  <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{emailDetails.metadata.subject}</dd>
                </div>
                <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                  <dt className="text-sm font-medium text-gray-500">Preheader</dt>
                  <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{emailDetails.metadata.preheader}</dd>
                </div>
                <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                  <dt className="text-sm font-medium text-gray-500">Locale</dt>
                  <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{emailDetails.metadata.locale}</dd>
                </div>
              </dl>
            </div>
          </div>

          {/* QA Status and Actions */}
          <div className="bg-white shadow overflow-hidden sm:rounded-lg mb-6">
            <div className="px-4 py-5 sm:px-6 flex justify-between items-center">
              <div>
                <h3 className="text-lg leading-6 font-medium text-gray-900">QA Status</h3>
                {analysis && (
                  <div className="mt-2 flex items-center">
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(analysis.overall_status)}`}>
                      {analysis.overall_status.replace('_', ' ')}
                    </span>
                    <span className="ml-4 inline-flex items-center px-3 py-1 rounded-full text-sm font-medium">
                      Risk Score: {analysis.risk_score}/100
                    </span>
                    <span className={`ml-4 inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getRiskLevelColor(analysis.risk_level)}`}>
                      {analysis.risk_level} risk
                    </span>
                  </div>
                )}
              </div>
              <button
                onClick={runQA}
                disabled={runningQA}
                className={`inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
                  runningQA ? 'bg-blue-400' : 'bg-blue-600 hover:bg-blue-700'
                } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500`}
              >
                {runningQA ? 'Running QA...' : 'Run QA Again'}
              </button>
            </div>
          </div>

          {/* Email Preview */}
          <div className="bg-white shadow overflow-hidden sm:rounded-lg mb-6">
            <div className="px-4 py-5 sm:px-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900">Email Preview</h3>
            </div>
            <div className="border-t border-gray-200">
              <div className="p-4">
                <HtmlPreview htmlContent={emailDetails.html_content} />
              </div>
            </div>
          </div>

          {/* Analysis Results */}
          {analysis && (
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              {/* Deterministic Tests */}
              <div className="bg-white shadow overflow-hidden sm:rounded-lg">
                <div className="px-4 py-5 sm:px-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900">Deterministic Tests</h3>
                </div>
                <div className="border-t border-gray-200">
                  <ul className="divide-y divide-gray-200">
                    {analysis.deterministic_results.map((test, index) => (
                      <li key={index} className="px-4 py-4 sm:px-6">
                        <div className="flex items-center justify-between">
                          <div className="text-sm font-medium text-gray-900">{test.test_name.replace('_', ' ')}</div>
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${test.status === 'pass' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                            {test.status}
                          </span>
                        </div>
                        <div className="mt-2 text-sm text-gray-500">
                          {test.details}
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>

              {/* Fix Suggestions */}
              <div className="bg-white shadow overflow-hidden sm:rounded-lg">
                <div className="px-4 py-5 sm:px-6">
                  <h3 className="text-lg leading-6 font-medium text-gray-900">Fix Suggestions</h3>
                </div>
                <div className="border-t border-gray-200">
                  <ul className="divide-y divide-gray-200">
                    {analysis.fix_suggestions.map((fix, index) => (
                      <li key={index} className="px-4 py-4 sm:px-6">
                        <div className="flex items-center justify-between">
                          <div className="text-sm font-medium text-gray-900">{fix.issue.replace('_', ' ')}</div>
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                            fix.priority === 'high' ? 'bg-red-100 text-red-800' :
                            fix.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-green-100 text-green-800'
                          }`}>
                            {fix.priority}
                          </span>
                        </div>
                        <div className="mt-2 text-sm text-gray-500">
                          {fix.suggestion}
                        </div>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}