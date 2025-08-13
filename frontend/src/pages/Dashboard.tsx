import React from 'react';
import { 
  ArrowUpIcon, 
  ArrowDownIcon, 
  BanknotesIcon, 
  CreditCardIcon, 
  ChartBarIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';
import { Line, Doughnut } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const Dashboard: React.FC = () => {
  // Mock data - in real app, this would come from API
  const spendingData = {
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

  const categoryData = {
    labels: ['Food & Dining', 'Transportation', 'Entertainment', 'Shopping', 'Bills'],
    datasets: [
      {
        data: [35, 25, 20, 15, 5],
        backgroundColor: [
          '#3B82F6',
          '#10B981',
          '#F59E0B',
          '#EF4444',
          '#8B5CF6',
        ],
        borderWidth: 2,
        borderColor: '#fff',
      },
    ],
  };

  const overviewCards = [
    {
      title: 'Total Balance',
      value: 'R$ 12,450.00',
      change: '+8.5%',
      changeType: 'positive',
      icon: BanknotesIcon,
      color: 'bg-primary-500',
    },
    {
      title: 'Monthly Income',
      value: 'R$ 5,800.00',
      change: '+12.3%',
      changeType: 'positive',
      icon: ArrowUpIcon,
      color: 'bg-success-500',
    },
    {
      title: 'Monthly Expenses',
      value: 'R$ 3,800.00',
      change: '-5.2%',
      changeType: 'negative',
      icon: ArrowDownIcon,
      color: 'bg-danger-500',
    },
    {
      title: 'Savings Rate',
      value: '34.5%',
      change: '+2.1%',
      changeType: 'positive',
      icon: ChartBarIcon,
      color: 'bg-warning-500',
    },
  ];

  const recentTransactions = [
    { id: 1, description: 'Grocery Shopping', amount: -120.50, category: 'Food & Dining', date: '2024-01-15' },
    { id: 2, description: 'Salary Deposit', amount: 5800.00, category: 'Income', date: '2024-01-14' },
    { id: 3, description: 'Gas Station', amount: -85.00, category: 'Transportation', date: '2024-01-13' },
    { id: 4, description: 'Netflix Subscription', amount: -39.90, category: 'Entertainment', date: '2024-01-12' },
  ];

  const budgetAlerts = [
    { category: 'Food & Dining', spent: 'R$ 1,200', limit: 'R$ 1,500', percentage: 80, status: 'warning' },
    { category: 'Entertainment', spent: 'R$ 450', limit: 'R$ 400', percentage: 112, status: 'danger' },
    { category: 'Shopping', spent: 'R$ 300', limit: 'R$ 500', percentage: 60, status: 'success' },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600">Welcome back! Here's your financial overview.</p>
        </div>
        <div className="flex items-center space-x-3">
          <select className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500">
            <option>Last 6 Months</option>
            <option>Last 3 Months</option>
            <option>Last Year</option>
          </select>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {overviewCards.map((card) => (
          <div key={card.title} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{card.title}</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{card.value}</p>
                <div className="flex items-center mt-2">
                  {card.changeType === 'positive' ? (
                    <ArrowUpIcon className="w-4 h-4 text-success-500 mr-1" />
                  ) : (
                    <ArrowDownIcon className="w-4 h-4 text-danger-500 mr-1" />
                  )}
                  <span className={`text-sm font-medium ${
                    card.changeType === 'positive' ? 'text-success-600' : 'text-danger-600'
                  }`}>
                    {card.change}
                  </span>
                  <span className="text-sm text-gray-500 ml-1">vs last month</span>
                </div>
              </div>
              <div className={`p-3 rounded-lg ${card.color}`}>
                <card.icon className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Cash Flow Chart */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Cash Flow Overview</h3>
          <div className="h-64">
            <Line 
              data={spendingData}
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
              data={categoryData}
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

      {/* Bottom Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Transactions */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Recent Transactions</h3>
            <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
              View All
            </button>
          </div>
          <div className="space-y-3">
            {recentTransactions.map((transaction) => (
              <div key={transaction.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="w-2 h-2 bg-gray-400 rounded-full"></div>
                  <div>
                    <p className="font-medium text-gray-900">{transaction.description}</p>
                    <p className="text-sm text-gray-500">{transaction.category} • {transaction.date}</p>
                  </div>
                </div>
                <span className={`font-semibold ${
                  transaction.amount > 0 ? 'text-success-600' : 'text-danger-600'
                }`}>
                  {transaction.amount > 0 ? '+' : ''}{transaction.amount}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Budget Alerts */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Budget Alerts</h3>
            <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
              View All
            </button>
          </div>
          <div className="space-y-3">
            {budgetAlerts.map((alert) => (
              <div key={alert.category} className="p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-gray-900">{alert.category}</span>
                  <span className={`text-sm font-medium ${
                    alert.status === 'danger' ? 'text-danger-600' : 
                    alert.status === 'warning' ? 'text-warning-600' : 'text-success-600'
                  }`}>
                    {alert.percentage}%
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm text-gray-600">
                  <span>Spent: {alert.spent}</span>
                  <span>Limit: {alert.limit}</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div 
                    className={`h-2 rounded-full ${
                      alert.status === 'danger' ? 'bg-danger-500' : 
                      alert.status === 'warning' ? 'bg-warning-500' : 'bg-success-500'
                    }`}
                    style={{ width: `${Math.min(alert.percentage, 100)}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
