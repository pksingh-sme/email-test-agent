import { useRouter } from 'next/router';
import { useState, useEffect } from 'react';
import { apiClient } from '../../lib/api';

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

interface DeterministicTest {
  test_name: string;
  status: 'pass' | 'fail';
  details: string;
}

interface Issue {
  rule: string;
  description: string;
  severity: string;
}

interface FixSuggestion {
  type: string;
  issue: string;
  description: string;
  suggestion: string;
  priority: string;
}

interface ScoreBreakdown {
  deterministic: {
    score: number;
    max: number;
    raw_score: number;
    raw_max: number;
  };
  compliance: {
    score: number;
    max: number;
    raw_score: number;
    raw_max: number;
  };
  tone: {
    score: number;
    max: number;
    raw_score: number;
    raw_max: number;
  };
  accessibility: {
    score: number;
    max: number;
    raw_score: number;
    raw_max: number;
  };
}

interface AgentAnalysis {
  overall_status: string;
  risk_score: number;
  risk_level: string;
  deterministic_results: DeterministicTest[];
  compliance_analysis: {
    issues: Issue[];
  };
  tone_analysis: {
    issues: Issue[];
  };
  accessibility_analysis: {
    issues: Issue[];
  };
  fix_suggestions: FixSuggestion[];
  top_issues: Array<{
    type: string;
    test_name: string;
    details: string;
    severity: string;
  }>;
  score_breakdown: ScoreBreakdown;
}

export default function EmailDetail() {
  const router = useRouter();
  const { id } = router.query;
  const [emailDetails, setEmailDetails] = useState<EmailDetails | null>(null);
  const [analysis, setAnalysis] = useState<AgentAnalysis | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [runningQA, setRunningQA] = useState(false);
  const [activeTab, setActiveTab] = useState('deterministic');

  useEffect(() => {
    if (id) {
      fetchEmailDetails();
    }
  }, [id]);

  const fetchEmailDetails = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getEmailDetails(id as string);
      setEmailDetails(response);
      
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
      if (id) {
        const response = await apiClient.getReport(id as string);
        if (response.report_data) {
          setAnalysis(response.report_data);
        } else if (response.status !== 'not_found') {
          // If we have data but no report_data, use what we have
          setAnalysis(response);
        }
      }
    } catch (err) {
      console.error('Failed to fetch analysis', err);
    }
  };

  const runQA = async () => {
    if (!id) return;
    
    try {
      setRunningQA(true);
      const response = await apiClient.runQA(id as string);
      // The response contains { report: {...} }, so we need to extract the report
      const reportData = response.report;
      if (reportData) {
        setAnalysis(reportData);
      }
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

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800';
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-100 text-red-800';
      case 'medium': return 'bg-yellow-100 text-yellow-800';
      case 'low': return 'bg-green-100 text-green-800';
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
                  <dt className="text-sm font-medium text-gray-500">Email Name</dt>
                  <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{emailDetails.metadata.template_name}</dd>
                </div>
                <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                  <dt className="text-sm font-medium text-gray-500">Locale</dt>
                  <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">{emailDetails.metadata.locale}</dd>
                </div>
                <div className="bg-gray-50 px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                  <dt className="text-sm font-medium text-gray-500">Last Checked</dt>
                  <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                    {emailDetails.metadata.created_at 
                      ? new Date(emailDetails.metadata.created_at).toLocaleString() 
                      : 'N/A'}
                  </dd>
                </div>
                <div className="bg-white px-4 py-5 sm:grid sm:grid-cols-3 sm:gap-4 sm:px-6">
                  <dt className="text-sm font-medium text-gray-500">Overall Result</dt>
                  <dd className="mt-1 text-sm text-gray-900 sm:mt-0 sm:col-span-2">
                    {analysis && (
                      <div className="flex items-center">
                        <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(analysis.overall_status || 'needs_review')}`}>
                          {analysis.overall_status === 'fail' ? '✖ FAIL' : analysis.overall_status === 'pass' ? '✔ PASS' : '⚠ NEEDS REVIEW'}
                        </span>
                        <span className="ml-4 inline-flex items-center px-3 py-1 rounded-full text-sm font-medium">
                          QA Score: <span className={getScoreColor(analysis.risk_score || 0)}>{(analysis.risk_score || 0)}/100</span>
                        </span>
                      </div>
                    )}
                  </dd>
                </div>
              </dl>
            </div>
          </div>

          {/* QA Actions */}
          <div className="bg-white shadow overflow-hidden sm:rounded-lg mb-6">
            <div className="px-4 py-5 sm:px-6">
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

          {/* Main Content - Email Preview and QA Summary */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            {/* Left: Email Preview */}
            <div className="bg-white shadow overflow-hidden sm:rounded-lg">
              <div className="px-4 py-5 sm:px-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900">EMAIL PREVIEW (Rendered HTML)</h3>
              </div>
              <div className="border-t border-gray-200">
                <div className="p-4">
                  <iframe 
                    srcDoc={emailDetails.html_content}
                    className="w-full h-96 border border-gray-300 rounded"
                    title="Email Preview"
                  />
                </div>
              </div>
            </div>

            {/* Right: QA Summary Panel */}
            <div className="bg-white shadow overflow-hidden sm:rounded-lg">
              <div className="px-4 py-5 sm:px-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900">TOP ISSUES (Prioritized by Agent)</h3>
              </div>
              <div className="border-t border-gray-200">
                <div className="p-4">
                  {analysis?.top_issues && analysis.top_issues.length > 0 ? (
                    <ul className="divide-y divide-gray-200">
                      {analysis.top_issues.slice(0, 5).map((issue, index) => (
                        <li key={index} className="py-3">
                          <div className="flex items-start">
                            <span className="flex-shrink-0 w-6 h-6 rounded-full bg-gray-200 flex items-center justify-center text-xs font-medium text-gray-700 mr-3">
                              {index + 1}
                            </span>
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-gray-900 truncate">
                                {issue.test_name.replace('_', ' ')}
                              </p>
                              <p className="text-sm text-gray-500 truncate">
                                {issue.details}
                              </p>
                            </div>
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeverityColor(issue.severity)}`}>
                              {issue.severity}
                            </span>
                          </div>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-gray-500 text-sm">No issues found</p>
                  )}
                </div>
              </div>

              <div className="px-4 py-5 sm:px-6 border-t border-gray-200">
                <h3 className="text-lg leading-6 font-medium text-gray-900">FIX SUGGESTIONS</h3>
              </div>
              <div className="border-t border-gray-200">
                <div className="p-4">
                  {analysis?.fix_suggestions && analysis.fix_suggestions.length > 0 ? (
                    <ul className="space-y-3">
                      {analysis.fix_suggestions.slice(0, 4).map((fix, index) => (
                        <li key={index} className="text-sm">
                          <div className="flex items-start">
                            <span className="flex-shrink-0 w-5 h-5 rounded-full bg-blue-100 flex items-center justify-center text-xs font-medium text-blue-800 mr-2 mt-0.5">
                              •
                            </span>
                            <div className="flex-1 min-w-0">
                              <p className="text-gray-700">{fix.suggestion}</p>
                            </div>
                          </div>
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-gray-500 text-sm">No fix suggestions available</p>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* Test Results Tabs */}
          {analysis && (
            <div className="bg-white shadow overflow-hidden sm:rounded-lg">
              <div className="border-b border-gray-200">
                <nav className="-mb-px flex space-x-8 px-6" aria-label="Tabs">
                  <button
                    onClick={() => setActiveTab('deterministic')}
                    className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${
                      activeTab === 'deterministic'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    1. Deterministic Results
                  </button>
                  <button
                    onClick={() => setActiveTab('brand')}
                    className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${
                      activeTab === 'brand'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    2. Brand Compliance
                  </button>
                  <button
                    onClick={() => setActiveTab('copy')}
                    className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${
                      activeTab === 'copy'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    3. Copy & Tone
                  </button>
                  <button
                    onClick={() => setActiveTab('accessibility')}
                    className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${
                      activeTab === 'accessibility'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    4. Accessibility
                  </button>
                  <button
                    onClick={() => setActiveTab('final')}
                    className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${
                      activeTab === 'final'
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    5. Final Decision Engine Output
                  </button>
                </nav>
              </div>

              <div className="p-6">
                {/* Deterministic Results Tab */}
                {activeTab === 'deterministic' && (
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Deterministic Results</h3>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <ul className="space-y-3">
                        {analysis.deterministic_results?.map((test: DeterministicTest, index: number) => (
                          <li key={index} className="flex items-center justify-between">
                            <span className="text-sm text-gray-700">
                              {test.test_name.replace('_', ' ')}: {test.details}
                            </span>
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              test.status === 'pass' 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {test.status === 'pass' ? '✔' : '✖'} {test.status}
                            </span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                {/* Brand Compliance Tab */}
                {activeTab === 'brand' && (
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Brand Compliance</h3>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <ul className="space-y-3">
                        {analysis.compliance_analysis?.issues?.map((issue: Issue, index: number) => (
                          <li key={index} className="flex items-center justify-between">
                            <span className="text-sm text-gray-700">
                              {issue.description}
                            </span>
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeverityColor(issue.severity)}`}>
                              {issue.severity}
                            </span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                {/* Copy & Tone Tab */}
                {activeTab === 'copy' && (
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Copy & Tone</h3>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <ul className="space-y-3">
                        {analysis.tone_analysis?.issues?.map((issue: Issue, index: number) => (
                          <li key={index} className="flex items-center justify-between">
                            <span className="text-sm text-gray-700">
                              {issue.description}
                            </span>
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeverityColor(issue.severity)}`}>
                              {issue.severity}
                            </span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                {/* Accessibility Tab */}
                {activeTab === 'accessibility' && (
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Accessibility</h3>
                    <div className="bg-gray-50 rounded-lg p-4">
                      <ul className="space-y-3">
                        {analysis.accessibility_analysis?.issues?.map((issue: Issue, index: number) => (
                          <li key={index} className="flex items-center justify-between">
                            <span className="text-sm text-gray-700">
                              {issue.description}
                            </span>
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSeverityColor(issue.severity)}`}>
                              {issue.severity}
                            </span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}

                {/* Final Decision Engine Output Tab */}
                {activeTab === 'final' && (
                  <div>
                    <h3 className="text-lg font-medium text-gray-900 mb-4">Final Decision Engine Output</h3>
                    <div className="bg-gray-50 rounded-lg p-6">
                      <div className="mb-6">
                        <h4 className="text-md font-medium text-gray-900 mb-3">WEIGHTED RULE SUMMARY</h4>
                        <div className="space-y-3">
                          <div className="flex justify-between items-center py-2 border-b border-gray-200">
                            <span className="text-sm text-gray-700">Deterministic Checks (40%)</span>
                            <span className="text-sm font-medium">
                              Score: {analysis.score_breakdown?.deterministic?.score || 0}/{analysis.score_breakdown?.deterministic?.max || 40}
                            </span>
                          </div>
                          <div className="flex justify-between items-center py-2 border-b border-gray-200">
                            <span className="text-sm text-gray-700">Brand Compliance (25%)</span>
                            <span className="text-sm font-medium">
                              Score: {analysis.score_breakdown?.compliance?.score || 0}/{analysis.score_breakdown?.compliance?.max || 25}
                            </span>
                          </div>
                          <div className="flex justify-between items-center py-2 border-b border-gray-200">
                            <span className="text-sm text-gray-700">Copy & Tone (15%)</span>
                            <span className="text-sm font-medium">
                              Score: {analysis.score_breakdown?.tone?.score || 0}/{analysis.score_breakdown?.tone?.max || 15}
                            </span>
                          </div>
                          <div className="flex justify-between items-center py-2 border-b border-gray-200">
                            <span className="text-sm text-gray-700">Accessibility (20%)</span>
                            <span className="text-sm font-medium">
                              Score: {analysis.score_breakdown?.accessibility?.score || 0}/{analysis.score_breakdown?.accessibility?.max || 20}
                            </span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="pt-4 border-t border-gray-200">
                        <div className="flex justify-between items-center">
                          <span className="text-lg font-bold text-gray-900">FINAL SCORE</span>
                          <span className="text-2xl font-bold">
                            <span className={getScoreColor(analysis.risk_score || 0)}>{analysis.risk_score || 0}/100</span>
                          </span>
                        </div>
                        <div className="mt-3 flex items-center">
                          <span className="text-lg font-bold text-gray-900">STATUS:</span>
                          <span className={`ml-2 inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(analysis.overall_status || 'needs_review')}`}>
                            {analysis.overall_status === 'fail' ? '❌ FAIL' : analysis.overall_status === 'pass' ? '✅ PASS' : '⚠ NEEDS REVIEW'}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}