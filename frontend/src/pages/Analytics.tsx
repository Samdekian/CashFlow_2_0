import React, { useState } from 'react';
import { 
  ChartBarIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  CalendarIcon,
  FunnelIcon,
  ArrowDownTrayIcon
} from '@heroicons/react/24/outline';
import { Line, Bar, Doughnut, Radar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  RadialLinearScale,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  RadialLinearScale
);

const Analytics: React.FC = () => {
  const [dateRange, setDateRange] = useState('6months');
  const [selectedMetric, setSelectedMetric] = useState('spending');

  // Mock data - in real app, this would come from API
  const spendingTrends = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: 'Income',
        data: [5000, 5200, 4800, 5500, 5300, 5800],
        borderColor: 'rgb(34, 197, 94)',
        backgroundColor: 'rgba(34, 197, 94, 0.1)',
        tension: 0.4,
      },
      {
        label: 'Expenses',
        data: [3200, 3400, 3100, 3600, 3300, 3800],
        borderColor: 'rgb(239, 68, 68)',
        backgroundColor: 'rgba(239, 68, 68, 0.1)',
        tension: 0.4,
      },
    ],
  };

  const categoryBreakdown = {
    labels: ['Food & Dining', 'Transportation', 'Entertainment', 'Shopping', 'Bills', 'Healthcare'],
    datasets: [
      {
        data: [35, 25, 20, 15, 3, 2],
        backgroundColor: [
          '#3B82F6',
          '#10B981',
          '#F59E0B',
          '#EF4444',
          '#8B5CF6',
          '#06B6D4',
        ],
        borderWidth: 2,
        borderColor: '#fff',
      },
    ],
  };

  const monthlyComparison = {
    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    datasets: [
      {
        label: '2024',
        data: [3200, 3400, 3100, 3600, 3300, 3800],
        backgroundColor: 'rgba(59, 130, 246, 0.8)',
      },
      {
        label: '2023',
        data: [3000, 3200, 2900, 3400, 3100, 3600],
        backgroundColor: 'rgba(156, 163, 175, 0.8)',
      },
    ],
  };

  const spendingPatterns = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    datasets: [
      {
        label: 'Average Daily Spending',
        data: [120, 95, 110, 85, 150, 200, 180],
        backgroundColor: 'rgba(139, 92, 246, 0.8)',
        borderColor: 'rgb(139, 92, 246)',
        borderWidth: 2,
      },
    ],
  };

  const financialHealth = {
    labels: ['Savings Rate', 'Debt Ratio', 'Emergency Fund', 'Investment Rate', 'Budget Adherence'],
    datasets: [
      {
        label: 'Current Score',
        data: [85, 70, 90, 60, 75],
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        borderColor: 'rgb(59, 130, 246)',
        borderWidth: 2,
        pointBackgroundColor: 'rgb(59, 130, 246)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgb(59, 130, 246)',
      },
      {
        label: 'Target Score',
        data: [90, 80, 95, 80, 85],
        backgroundColor: 'rgba(34, 197, 94, 0.2)',
        borderColor: 'rgb(34, 197, 94)',
        borderWidth: 2,
        pointBackgroundColor: 'rgb(34, 197, 94)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgb(34, 197, 94)',
      },
    ],
  };

  const insights = [
    {
      type: 'positive',
      title: 'Savings Rate Improved',
      description: 'Your savings rate increased by 5% this month compared to last month.',
      icon: ArrowTrendingUpIcon,
    },
    {
      type: 'warning',
      title: 'Entertainment Spending High',
      description: 'Entertainment spending is 12% above your monthly average.',
      icon: ArrowTrendingDownIcon,
    },
    {
      type: 'positive',
      title: 'Transportation Costs Down',
      description: 'Transportation costs decreased by 8% due to reduced fuel consumption.',
      icon: ArrowTrendingUpIcon,
    },
    {
      type: 'info',
      title: 'Budget Compliance',
      description: 'You\'re on track with 4 out of 5 budget categories this month.',
      icon: ChartBarIcon,
    },
  ];

  const getInsightColor = (type: string) => {
    switch (type) {
      case 'positive': return 'text-success-600 bg-success-50 border-success-200';
      case 'warning': return 'text-warning-600 bg-warning-50 border-warning-200';
      case 'negative': return 'text-danger-600 bg-danger-50 border-danger-200';
      default: return 'text-primary-600 bg-primary-50 border-primary-200';
    }
  };

  const getInsightIconColor = (type: string) => {
    switch (type) {
      case 'positive': return 'text-success-600';
      case 'warning': return 'text-warning-600';
      case 'negative': return 'text-danger-600';
      default: return 'text-primary-600';
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
          <p className="text-gray-600">Comprehensive financial analysis and insights to help you make better decisions.</p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
            <ArrowDownTrayIcon className="w-4 h-4 mr-2" />
            Export Report
          </button>
        </div>
      </div>

      {/* Filters and Controls */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Analysis Parameters</h3>
          <button className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
            <FunnelIcon className="w-4 h-4 mr-2" />
            Advanced Filters
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Date Range</label>
            <select 
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="1month">Last Month</option>
              <option value="3months">Last 3 Months</option>
              <option value="6months">Last 6 Months</option>
              <option value="1year">Last Year</option>
              <option value="custom">Custom Range</option>
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Primary Metric</label>
            <select 
              value={selectedMetric}
              onChange={(e) => setSelectedMetric(e.target.value)}
              className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
            >
              <option value="spending">Spending Analysis</option>
              <option value="income">Income Analysis</option>
              <option value="savings">Savings Analysis</option>
              <option value="budget">Budget Analysis</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Category Level</label>
            <select className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500">
              <option value="1">Level 1 (Main)</option>
              <option value="2">Level 2 (Sub)</option>
              <option value="3">Level 3 (Specific)</option>
            </select>
          </div>
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-3 bg-success-100 rounded-lg">
              <ArrowTrendingUpIcon className="w-6 h-6 text-success-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Income</p>
              <p className="text-2xl font-bold text-gray-900">R$ 31,600</p>
              <p className="text-sm text-success-600">+12.3% vs last period</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-3 bg-danger-100 rounded-lg">
              <ArrowTrendingDownIcon className="w-6 h-6 text-danger-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Total Expenses</p>
              <p className="text-2xl font-bold text-gray-900">R$ 20,400</p>
              <p className="text-sm text-danger-600">+5.2% vs last period</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-3 bg-primary-100 rounded-lg">
              <ChartBarIcon className="w-6 h-6 text-primary-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Net Savings</p>
              <p className="text-2xl font-bold text-gray-900">R$ 11,200</p>
              <p className="text-sm text-primary-600">35.4% of income</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center">
            <div className="p-3 bg-warning-100 rounded-lg">
              <CalendarIcon className="w-6 h-6 text-warning-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Avg Daily Spend</p>
              <p className="text-2xl font-bold text-gray-900">R$ 113</p>
              <p className="text-sm text-warning-600">Within budget</p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Cash Flow Trends */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Cash Flow Trends</h3>
          <div className="h-64">
            <Line 
              data={spendingTrends}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'top' as const,
                  },
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    ticks: {
                      callback: function(value) {
                        return 'R$ ' + value;
                      }
                    }
                  }
                }
              }}
            />
          </div>
        </div>

        {/* Category Breakdown */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Spending by Category</h3>
          <div className="h-64">
            <Doughnut 
              data={categoryBreakdown}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'bottom' as const,
                  },
                }
              }}
            />
          </div>
        </div>
      </div>

      {/* Additional Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Monthly Comparison */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Monthly Comparison</h3>
          <div className="h-64">
            <Bar 
              data={monthlyComparison}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'top' as const,
                  },
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    ticks: {
                      callback: function(value) {
                        return 'R$ ' + value;
                      }
                    }
                  }
                }
              }}
            />
          </div>
        </div>

        {/* Weekly Spending Patterns */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Weekly Spending Patterns</h3>
          <div className="h-64">
            <Bar 
              data={spendingPatterns}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    position: 'top' as const,
                  },
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    ticks: {
                      callback: function(value) {
                        return 'R$ ' + value;
                      }
                    }
                  }
                }
              }}
            />
          </div>
        </div>
      </div>

      {/* Financial Health Radar Chart */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Financial Health Assessment</h3>
        <div className="h-80">
          <Radar 
            data={financialHealth}
            options={{
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                legend: {
                  position: 'top' as const,
                },
              },
              scales: {
                r: {
                  beginAtZero: true,
                  max: 100,
                  ticks: {
                    stepSize: 20,
                  },
                },
              },
            }}
          />
        </div>
      </div>

      {/* Insights and Recommendations */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Insights & Recommendations</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {insights.map((insight, index) => (
            <div key={index} className={`p-4 rounded-lg border ${getInsightColor(insight.type)}`}>
              <div className="flex items-start space-x-3">
                <div className={`p-2 rounded-lg ${getInsightIconColor(insight.type)} bg-white`}>
                  <insight.icon className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="font-medium text-gray-900">{insight.title}</h4>
                  <p className="text-sm text-gray-600 mt-1">{insight.description}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Export Options */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Export & Share</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
            <ArrowDownTrayIcon className="w-4 h-4 mr-2" />
            Export as PDF
          </button>
          <button className="flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
            <ArrowDownTrayIcon className="w-4 h-4 mr-2" />
            Export as Excel
          </button>
          <button className="flex items-center justify-center px-4 py-3 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
            <ArrowDownTrayIcon className="w-4 h-4 mr-2" />
            Export as JSON
          </button>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
