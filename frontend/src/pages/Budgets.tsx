import React, { useState } from 'react';
import { 
  PlusIcon, 
  BanknotesIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon
} from '@heroicons/react/24/outline';

interface Budget {
  id: string;
  name: string;
  category: string;
  amount: number;
  spent: number;
  remaining: number;
  period: string;
  start_date: string;
  end_date: string;
  status: 'active' | 'inactive' | 'completed';
  progress_percentage: number;
  alerts: string[];
}

const Budgets: React.FC = () => {
  const [selectedBudget, setSelectedBudget] = useState<Budget | null>(null);
  const [filterStatus, setFilterStatus] = useState<string>('all');

  // Mock data - in real app, this would come from API
  const budgets: Budget[] = [
    {
      id: '1',
      name: 'Monthly Food Budget',
      category: 'Alimentação',
      amount: 1500.00,
      spent: 1200.50,
      remaining: 299.50,
      period: 'Monthly',
      start_date: '2024-01-01',
      end_date: '2024-01-31',
      status: 'active',
      progress_percentage: 80,
      alerts: ['Approaching limit', 'High spending rate']
    },
    {
      id: '2',
      name: 'Entertainment Budget',
      category: 'Entretenimento',
      amount: 400.00,
      spent: 450.00,
      remaining: -50.00,
      period: 'Monthly',
      start_date: '2024-01-01',
      end_date: '2024-01-31',
      status: 'active',
      progress_percentage: 112,
      alerts: ['Budget exceeded', 'Immediate action required']
    },
    {
      id: '3',
      name: 'Transportation Budget',
      category: 'Transporte',
      amount: 500.00,
      spent: 320.00,
      remaining: 180.00,
      period: 'Monthly',
      start_date: '2024-01-01',
      end_date: '2024-01-31',
      status: 'active',
      progress_percentage: 64,
      alerts: []
    },
    {
      id: '4',
      name: 'Shopping Budget',
      category: 'Compras',
      amount: 800.00,
      spent: 300.00,
      remaining: 500.00,
      period: 'Monthly',
      start_date: '2024-01-01',
      end_date: '2024-01-31',
      status: 'active',
      progress_percentage: 37,
      alerts: []
    },
    {
      id: '5',
      name: 'Annual Vacation Fund',
      category: 'Viagens',
      amount: 5000.00,
      spent: 0.00,
      remaining: 5000.00,
      period: 'Yearly',
      start_date: '2024-01-01',
      end_date: '2024-12-31',
      status: 'active',
      progress_percentage: 0,
      alerts: []
    }
  ];

  const filteredBudgets = filterStatus === 'all' 
    ? budgets 
    : budgets.filter(budget => budget.status === filterStatus);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-success-100 text-success-800';
      case 'inactive': return 'bg-gray-100 text-gray-800';
      case 'completed': return 'bg-primary-100 text-primary-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getProgressColor = (percentage: number) => {
    if (percentage >= 100) return 'bg-danger-500';
    if (percentage >= 80) return 'bg-warning-500';
    return 'bg-success-500';
  };

  const getAlertIcon = (budget: Budget) => {
    if (budget.progress_percentage >= 100) {
      return <XCircleIcon className="w-5 h-5 text-danger-500" />;
    } else if (budget.progress_percentage >= 80) {
      return <ExclamationTriangleIcon className="w-5 h-5 text-warning-500" />;
    } else {
      return <CheckCircleIcon className="w-5 h-5 text-success-500" />;
    }
  };

  const getAlertText = (budget: Budget) => {
    if (budget.progress_percentage >= 100) {
      return 'Budget Exceeded';
    } else if (budget.progress_percentage >= 80) {
      return 'Approaching Limit';
    } else {
      return 'On Track';
    }
  };

  const getAlertColor = (budget: Budget) => {
    if (budget.progress_percentage >= 100) {
      return 'text-danger-600 bg-danger-50';
    } else if (budget.progress_percentage >= 80) {
      return 'text-warning-600 bg-warning-50';
    } else {
      return 'text-success-600 bg-success-50';
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Budgets</h1>
          <p className="text-gray-600">Track your spending against budget limits and stay on top of your finances.</p>
        </div>
        <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-200">
          <PlusIcon className="w-4 h-4 mr-2" />
          New Budget
        </button>
      </div>

      {/* Budget Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-3 bg-primary-100 rounded-lg">
              <BanknotesIcon className="w-6 h-6 text-primary-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Budgets</p>
              <p className="text-2xl font-bold text-gray-900">{budgets.length}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-3 bg-success-100 rounded-lg">
              <CheckCircleIcon className="w-6 h-6 text-success-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">On Track</p>
              <p className="text-2xl font-bold text-gray-900">
                {budgets.filter(b => b.progress_percentage < 80).length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-3 bg-warning-100 rounded-lg">
              <ExclamationTriangleIcon className="w-6 h-6 text-warning-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Warning</p>
              <p className="text-2xl font-bold text-gray-900">
                {budgets.filter(b => b.progress_percentage >= 80 && b.progress_percentage < 100).length}
              </p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-3 bg-danger-100 rounded-lg">
              <XCircleIcon className="w-6 h-6 text-danger-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Exceeded</p>
              <p className="text-2xl font-bold text-gray-900">
                {budgets.filter(b => b.progress_percentage >= 100).length}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center space-x-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status Filter</label>
            <select 
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="all">All Statuses</option>
              <option value="active">Active</option>
              <option value="inactive">Inactive</option>
              <option value="completed">Completed</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Period</label>
            <select className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500">
              <option value="">All Periods</option>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
              <option value="quarterly">Quarterly</option>
              <option value="yearly">Yearly</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
            <select className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500">
              <option value="">All Categories</option>
              <option value="alimentacao">Alimentação</option>
              <option value="transporte">Transporte</option>
              <option value="entretenimento">Entretenimento</option>
              <option value="compras">Compras</option>
            </select>
          </div>
        </div>
      </div>

      {/* Budgets List */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            Budgets ({filteredBudgets.length})
          </h3>
        </div>
        
        <div className="divide-y divide-gray-200">
          {filteredBudgets.map((budget) => (
            <div key={budget.id} className="p-6 hover:bg-gray-50">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h4 className="text-lg font-medium text-gray-900">{budget.name}</h4>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(budget.status)}`}>
                      {budget.status}
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                    <div>
                      <p className="text-sm text-gray-500">Category</p>
                      <p className="text-sm font-medium text-gray-900">{budget.category}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Period</p>
                      <p className="text-sm font-medium text-gray-900">{budget.period}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Start Date</p>
                      <p className="text-sm font-medium text-gray-900">
                        {new Date(budget.start_date).toLocaleDateString('pt-BR')}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">End Date</p>
                      <p className="text-sm font-medium text-gray-900">
                        {new Date(budget.end_date).toLocaleDateString('pt-BR')}
                      </p>
                    </div>
                  </div>

                  {/* Progress Bar */}
                  <div className="mb-2">
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span className="text-gray-600">Progress</span>
                      <span className="font-medium text-gray-900">{budget.progress_percentage}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${getProgressColor(budget.progress_percentage)}`}
                        style={{ width: `${Math.min(budget.progress_percentage, 100)}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Amount Details */}
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <p className="text-sm text-gray-500">Budget Amount</p>
                      <p className="text-lg font-semibold text-gray-900">R$ {budget.amount.toFixed(2)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Spent</p>
                      <p className="text-lg font-semibold text-danger-600">R$ {budget.spent.toFixed(2)}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Remaining</p>
                      <p className={`text-lg font-semibold ${
                        budget.remaining >= 0 ? 'text-success-600' : 'text-danger-600'
                      }`}>
                        {budget.remaining >= 0 ? '+' : ''}R$ {budget.remaining.toFixed(2)}
                      </p>
                    </div>
                  </div>

                  {/* Alerts */}
                  {budget.alerts.length > 0 && (
                    <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <ExclamationTriangleIcon className="w-4 h-4 text-red-500" />
                        <span className="text-sm font-medium text-red-800">Alerts:</span>
                      </div>
                      <ul className="mt-1 ml-6 text-sm text-red-700">
                        {budget.alerts.map((alert, index) => (
                          <li key={index}>• {alert}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                <div className="ml-6 flex flex-col items-center space-y-3">
                  {/* Status Icon */}
                  <div className={`p-3 rounded-lg ${getAlertColor(budget)}`}>
                    {getAlertIcon(budget)}
                  </div>
                  <p className={`text-xs font-medium ${getAlertColor(budget)}`}>
                    {getAlertText(budget)}
                  </p>

                  {/* Actions */}
                  <div className="flex flex-col space-y-2">
                    <button 
                      onClick={() => setSelectedBudget(budget)}
                      className="p-2 text-gray-400 hover:text-primary-600 transition-colors"
                    >
                      <EyeIcon className="w-4 h-4" />
                    </button>
                    <button className="p-2 text-gray-400 hover:text-warning-600 transition-colors">
                      <PencilIcon className="w-4 h-4" />
                    </button>
                    <button className="p-2 text-gray-400 hover:text-danger-600 transition-colors">
                      <TrashIcon className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Budget Details Modal */}
      {selectedBudget && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Budget Details</h3>
                <button
                  onClick={() => setSelectedBudget(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Name</label>
                  <p className="mt-1 text-sm text-gray-900">{selectedBudget.name}</p>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Category</label>
                    <p className="mt-1 text-sm text-gray-900">{selectedBudget.category}</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Period</label>
                    <p className="mt-1 text-sm text-gray-900">{selectedBudget.period}</p>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Start Date</label>
                    <p className="mt-1 text-sm text-gray-900">
                      {new Date(selectedBudget.start_date).toLocaleDateString('pt-BR')}
                    </p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700">End Date</label>
                    <p className="mt-1 text-sm text-gray-900">
                      {new Date(selectedBudget.end_date).toLocaleDateString('pt-BR')}
                    </p>
                  </div>
                </div>
                
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Budget</label>
                    <p className="mt-1 text-sm font-semibold text-gray-900">R$ {selectedBudget.amount.toFixed(2)}</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Spent</label>
                    <p className="mt-1 text-sm font-semibold text-danger-600">R$ {selectedBudget.spent.toFixed(2)}</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Remaining</label>
                    <p className={`mt-1 text-sm font-semibold ${
                      selectedBudget.remaining >= 0 ? 'text-success-600' : 'text-danger-600'
                    }`}>
                      {selectedBudget.remaining >= 0 ? '+' : ''}R$ {selectedBudget.remaining.toFixed(2)}
                    </p>
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Progress</label>
                  <div className="mt-2">
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span className="text-gray-600">{selectedBudget.progress_percentage}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className={`h-2 rounded-full ${getProgressColor(selectedBudget.progress_percentage)}`}
                        style={{ width: `${Math.min(selectedBudget.progress_percentage, 100)}%` }}
                      ></div>
                    </div>
                  </div>
                </div>
                
                {selectedBudget.alerts.length > 0 && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Alerts</label>
                    <div className="mt-1 space-y-1">
                      {selectedBudget.alerts.map((alert, index) => (
                        <div key={index} className="text-sm text-red-600">• {alert}</div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              
              <div className="flex items-center justify-end space-x-3 mt-6">
                <button
                  onClick={() => setSelectedBudget(null)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                  Close
                </button>
                <button className="px-4 py-2 text-sm font-medium text-white bg-primary-600 border border-transparent rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
                  Edit Budget
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Budgets;
