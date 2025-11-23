import { useState, useEffect } from 'react';
import { apiClient, Rule } from '../../lib/api';

export default function AdminPanel() {
  const [rules, setRules] = useState<Rule[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [editingRule, setEditingRule] = useState<Rule | null>(null);
  const [scoringFormula, setScoringFormula] = useState<string>(
    'Total Score = Σ( deterministic_weight * deterministic_score ) + Σ( agentic_weight * agent_agentic_score )'
  );

  useEffect(() => {
    fetchRules();
  }, []);

  const fetchRules = async () => {
    try {
      setLoading(true);
      const fetchedRules = await apiClient.getRules();
      setRules(fetchedRules);
    } catch (err) {
      setError('Failed to fetch rules');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleEditRule = (rule: Rule) => {
    setEditingRule(rule);
  };

  const handleSaveRule = async () => {
    if (editingRule) {
      try {
        const updatedRule = await apiClient.updateRule(editingRule.id, editingRule);
        setRules(rules.map(rule => rule.id === editingRule.id ? updatedRule : rule));
        setEditingRule(null);
      } catch (err) {
        setError('Failed to update rule');
        console.error(err);
      }
    }
  };

  const handleCancelEdit = () => {
    setEditingRule(null);
  };

  const handleWeightChange = (id: string, weight: number) => {
    setRules(rules.map(rule => rule.id === id ? { ...rule, weight } : rule));
  };

  const handlePriorityChange = (id: string, priority: 'High' | 'Medium' | 'Low') => {
    setRules(rules.map(rule => rule.id === id ? { ...rule, priority } : rule));
  };

  const handleOverrideChange = (id: string, override: boolean) => {
    setRules(rules.map(rule => rule.id === id ? { ...rule, override_enabled: override } : rule));
  };

  const handleSaveScoringModel = async () => {
    try {
      await apiClient.updateScoringModel(scoringFormula);
      alert('Scoring model updated successfully!');
    } catch (err) {
      setError('Failed to update scoring model');
      console.error(err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-xl">Loading rules...</div>
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
          <h1 className="text-3xl font-bold text-gray-900">ADMIN PANEL – QA RULE SET</h1>
        </div>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-4">
            <a href="/" className="text-gray-500 hover:text-gray-700 font-medium">
              Dashboard
            </a>
            <a href="/admin" className="text-blue-600 hover:text-blue-800 font-medium">
              Admin Panel
            </a>
          </div>
        </div>
      </header>
      
      <main>
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          {/* Rule Management Table */}
          <div className="bg-white shadow overflow-hidden sm:rounded-lg mb-6">
            <div className="px-4 py-5 sm:px-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900">Rule Management</h3>
            </div>
            <div className="border-t border-gray-200">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Rule Name
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Weight
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Priority
                    </th>
                    <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Override
                    </th>
                    <th scope="col" className="relative px-6 py-3">
                      <span className="sr-only">Actions</span>
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {rules.map((rule) => (
                    <tr key={rule.id}>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        {rule.name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <div className="flex items-center">
                          <span className="mr-2">{rule.weight}%</span>
                          <input
                            type="range"
                            min="0"
                            max="100"
                            value={rule.weight}
                            onChange={(e) => handleWeightChange(rule.id, parseInt(e.target.value))}
                            className="w-24"
                          />
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <select
                          value={rule.priority}
                          onChange={(e) => handlePriorityChange(rule.id, e.target.value as 'High' | 'Medium' | 'Low')}
                          className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                        >
                          <option value="High">High</option>
                          <option value="Medium">Medium</option>
                          <option value="Low">Low</option>
                        </select>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        <label className="inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={rule.override_enabled}
                            onChange={(e) => handleOverrideChange(rule.id, e.target.checked)}
                            className="rounded border-gray-300 text-blue-600 shadow-sm focus:border-blue-300 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                          />
                          <span className="ml-2">ON</span>
                        </label>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <button
                          onClick={() => handleEditRule(rule)}
                          className="text-blue-600 hover:text-blue-900"
                        >
                          Edit
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Rule Editor Panel */}
          {editingRule && (
            <div className="bg-white shadow overflow-hidden sm:rounded-lg mb-6">
              <div className="px-4 py-5 sm:px-6">
                <h3 className="text-lg leading-6 font-medium text-gray-900">Edit Rule: {editingRule.name}</h3>
              </div>
              <div className="border-t border-gray-200">
                <div className="px-4 py-5 sm:p-6">
                  <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                    <div className="sm:col-span-6">
                      <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                        Description
                      </label>
                      <div className="mt-1">
                        <input
                          type="text"
                          id="description"
                          value={editingRule.description}
                          onChange={(e) => setEditingRule({...editingRule, description: e.target.value})}
                          className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                        />
                      </div>
                    </div>

                    <div className="sm:col-span-3">
                      <label htmlFor="weight" className="block text-sm font-medium text-gray-700">
                        Weight: {editingRule.weight}%
                      </label>
                      <div className="mt-1">
                        <input
                          type="range"
                          id="weight"
                          min="0"
                          max="100"
                          value={editingRule.weight}
                          onChange={(e) => setEditingRule({...editingRule, weight: parseInt(e.target.value)})}
                          className="w-full"
                        />
                      </div>
                    </div>

                    <div className="sm:col-span-3">
                      <label htmlFor="priority" className="block text-sm font-medium text-gray-700">
                        Priority
                      </label>
                      <div className="mt-1">
                        <select
                          id="priority"
                          value={editingRule.priority}
                          onChange={(e) => setEditingRule({...editingRule, priority: e.target.value as 'High' | 'Medium' | 'Low'})}
                          className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                        >
                          <option value="High">High</option>
                          <option value="Medium">Medium</option>
                          <option value="Low">Low</option>
                        </select>
                      </div>
                    </div>

                    <div className="sm:col-span-6">
                      <label className="block text-sm font-medium text-gray-700">
                        Business Override
                      </label>
                      <div className="mt-1">
                        <div className="flex items-start">
                          <div className="flex items-center h-5">
                            <input
                              id="business-override"
                              name="business-override"
                              type="checkbox"
                              checked={editingRule.override_enabled}
                              onChange={(e) => setEditingRule({...editingRule, override_enabled: e.target.checked})}
                              className="focus:ring-blue-500 h-4 w-4 text-blue-600 border-gray-300 rounded"
                            />
                          </div>
                          <div className="ml-3 text-sm">
                            <label htmlFor="business-override" className="font-medium text-gray-700">
                              Allow decorative images with empty ALT
                            </label>
                            <p className="text-gray-500">
                              <input
                                type="text"
                                value={editingRule.business_override_text}
                                onChange={(e) => setEditingRule({...editingRule, business_override_text: e.target.value})}
                                className="mt-1 shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                                placeholder="Business override description"
                              />
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div className="sm:col-span-6">
                      <label htmlFor="error-message" className="block text-sm font-medium text-gray-700">
                        Error Messaging
                      </label>
                      <div className="mt-1">
                        <input
                          type="text"
                          id="error-message"
                          value={editingRule.error_message}
                          onChange={(e) => setEditingRule({...editingRule, error_message: e.target.value})}
                          className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                        />
                      </div>
                    </div>
                  </div>
                </div>
                <div className="px-4 py-3 bg-gray-50 text-right sm:px-6">
                  <button
                    onClick={handleCancelEdit}
                    className="inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleSaveRule}
                    className="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    Save
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Final Admin Setting: Scoring Formula */}
          <div className="bg-white shadow overflow-hidden sm:rounded-lg">
            <div className="px-4 py-5 sm:px-6">
              <h3 className="text-lg leading-6 font-medium text-gray-900">FINAL SCORING MODEL</h3>
            </div>
            <div className="border-t border-gray-200">
              <div className="px-4 py-5 sm:p-6">
                <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
                  <div className="sm:col-span-6">
                    <label htmlFor="scoring-formula" className="block text-sm font-medium text-gray-700">
                      Weighted formula (editable):
                    </label>
                    <div className="mt-1">
                      <textarea
                        id="scoring-formula"
                        rows={4}
                        value={scoringFormula}
                        onChange={(e) => setScoringFormula(e.target.value)}
                        className="shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                      />
                    </div>
                  </div>
                </div>
              </div>
              <div className="px-4 py-3 bg-gray-50 text-right sm:px-6">
                <button
                  onClick={handleSaveScoringModel}
                  className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Update Scoring Model
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}