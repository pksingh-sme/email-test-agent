import React from 'react';

interface EmailTemplate {
  id: string;
  name: string;
  created_at: string;
  status: string;
}

interface TestResultCardProps {
  template: EmailTemplate;
  onViewReport: (templateId: string) => void;
}

const TestResultCard: React.FC<TestResultCardProps> = ({ template, onViewReport }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pass': return 'bg-green-100 text-green-800';
      case 'fail': return 'bg-red-100 text-red-800';
      case 'needs_review': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (dateString: string) => {
    const options: Intl.DateTimeFormatOptions = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  return (
    <div className="bg-white overflow-hidden shadow rounded-lg">
      <div className="px-4 py-5 sm:p-6">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-gray-900">{template.name}</h3>
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(template.status)}`}>
            {template.status.replace('_', ' ')}
          </span>
        </div>
        <div className="mt-2 text-sm text-gray-500">
          <p>Created: {formatDate(template.created_at)}</p>
        </div>
        <div className="mt-4">
          <button
            onClick={() => onViewReport(template.id)}
            className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            View Report
          </button>
        </div>
      </div>
    </div>
  );
};

export default TestResultCard;