import React, { useState } from 'react';
import { 
  PlusIcon, 
  FunnelIcon, 
  MagnifyingGlassIcon,
  EyeIcon,
  PencilIcon,
  TrashIcon
} from '@heroicons/react/24/outline';
import { useReactTable, getCoreRowModel, getFilteredRowModel, getSortedRowModel, getPaginationRowModel } from '@tanstack/react-table';
import type { ColumnDef } from '@tanstack/react-table';

interface Transaction {
  id: string;
  description: string;
  amount: number;
  category: string;
  type: 'income' | 'expense';
  date: string;
  status: 'completed' | 'pending' | 'cancelled';
}

const Transactions: React.FC = () => {
  const [showFilters, setShowFilters] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  // Mock data - in real app, this would come from API
  const transactions: Transaction[] = [
    { id: '1', description: 'Grocery Shopping', amount: -120.50, category: 'Food & Dining', type: 'expense', date: '2024-01-15', status: 'completed' },
    { id: '2', description: 'Salary Deposit', amount: 5800.00, category: 'Income', type: 'income', date: '2024-01-14', status: 'completed' },
    { id: '3', description: 'Gas Station', amount: -85.00, category: 'Transportation', type: 'expense', date: '2024-01-13', status: 'completed' },
    { id: '4', description: 'Netflix Subscription', amount: -39.90, category: 'Entertainment', type: 'expense', date: '2024-01-12', status: 'completed' },
    { id: '5', description: 'Freelance Work', amount: 1500.00, category: 'Income', type: 'income', date: '2024-01-11', status: 'completed' },
    { id: '6', description: 'Restaurant', amount: -75.00, category: 'Food & Dining', type: 'expense', date: '2024-01-10', status: 'completed' },
  ];

  const columns: ColumnDef<Transaction>[] = [
    {
      accessorKey: 'date',
      header: 'Date',
      cell: ({ getValue }) => {
        const date = new Date(getValue() as string);
        return date.toLocaleDateString('pt-BR');
      },
    },
    {
      accessorKey: 'description',
      header: 'Description',
      cell: ({ getValue }) => <span className="font-medium">{getValue() as string}</span>,
    },
    {
      accessorKey: 'category',
      header: 'Category',
      cell: ({ getValue }) => (
        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
          {getValue() as string}
        </span>
      ),
    },
    {
      accessorKey: 'amount',
      header: 'Amount',
      cell: ({ getValue }) => {
        const amount = getValue() as number;
        return (
          <span className={`font-semibold ${
            amount >= 0 ? 'text-success-600' : 'text-danger-600'
          }`}>
            {amount >= 0 ? '+' : ''}R$ {Math.abs(amount).toFixed(2)}
          </span>
        );
      },
    },
    {
      accessorKey: 'type',
      header: 'Type',
      cell: ({ getValue }) => {
        const type = getValue() as string;
        return (
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
            type === 'income' 
              ? 'bg-success-100 text-success-800' 
              : 'bg-danger-100 text-danger-800'
          }`}>
            {type === 'income' ? 'Income' : 'Expense'}
          </span>
        );
      },
    },
    {
      accessorKey: 'status',
      header: 'Status',
      cell: ({ getValue }) => {
        const status = getValue() as string;
        const statusConfig = {
          completed: { bg: 'bg-success-100', text: 'text-success-800', label: 'Completed' },
          pending: { bg: 'bg-warning-100', text: 'text-warning-800', label: 'Pending' },
          cancelled: { bg: 'bg-gray-100', text: 'text-gray-800', label: 'Cancelled' },
        };
        const config = statusConfig[status as keyof typeof statusConfig];
        return (
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${config.bg} ${config.text}`}>
            {config.label}
          </span>
        );
      },
    },
    {
      id: 'actions',
      header: 'Actions',
      cell: ({ row }) => (
        <div className="flex items-center space-x-2">
          <button className="p-1 text-gray-400 hover:text-primary-600 transition-colors">
            <EyeIcon className="w-4 h-4" />
          </button>
          <button className="p-1 text-gray-400 hover:text-warning-600 transition-colors">
            <PencilIcon className="w-4 h-4" />
          </button>
          <button className="p-1 text-gray-400 hover:text-danger-600 transition-colors">
            <TrashIcon className="w-4 h-4" />
          </button>
        </div>
      ),
    },
  ];

  const table = useReactTable({
    data: transactions,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
  });

  const { rows } = table.getFilteredRowModel();

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Transactions</h1>
          <p className="text-gray-600">Manage and track all your financial transactions.</p>
        </div>
        <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-200">
          <PlusIcon className="w-4 h-4 mr-2" />
          New Transaction
        </button>
      </div>

      {/* Filters and Search */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-gray-900">Filters & Search</h3>
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="inline-flex items-center px-3 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            <FunnelIcon className="w-4 h-4 mr-2" />
            {showFilters ? 'Hide Filters' : 'Show Filters'}
          </button>
        </div>

        {/* Search */}
        <div className="relative mb-4">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
          </div>
          <input
            type="text"
            placeholder="Search transactions by description or category..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
          />
        </div>

        {/* Advanced Filters */}
        {showFilters && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pt-4 border-t border-gray-200">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
              <select className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500">
                <option value="">All Types</option>
                <option value="income">Income</option>
                <option value="expense">Expense</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
              <select className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500">
                <option value="">All Categories</option>
                <option value="food">Food & Dining</option>
                <option value="transportation">Transportation</option>
                <option value="entertainment">Entertainment</option>
                <option value="income">Income</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
              <select className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500">
                <option value="">All Statuses</option>
                <option value="completed">Completed</option>
                <option value="pending">Pending</option>
                <option value="cancelled">Cancelled</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Date Range</label>
              <select className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500">
                <option value="">All Time</option>
                <option value="today">Today</option>
                <option value="week">This Week</option>
                <option value="month">This Month</option>
                <option value="quarter">This Quarter</option>
                <option value="year">This Year</option>
              </select>
            </div>
          </div>
        )}
      </div>

      {/* Transactions Table */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            Transactions ({rows.length})
          </h3>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              {table.getHeaderGroups().map(headerGroup => (
                <tr key={headerGroup.id}>
                  {headerGroup.headers.map(header => (
                    <th
                      key={header.id}
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                    >
                      {header.isPlaceholder ? null : header.column.columnDef.header}
                    </th>
                  ))}
                </tr>
              ))}
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {rows.map(row => (
                <tr key={row.id} className="hover:bg-gray-50">
                  {row.getVisibleCells().map(cell => (
                    <td key={cell.id} className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {cell.column.columnDef.cell ? 
                        cell.column.columnDef.cell({ getValue: () => cell.getValue(), row }) : 
                        cell.getValue() as string
                      }
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="px-6 py-3 border-t border-gray-200">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-700">
              Showing <span className="font-medium">1</span> to <span className="font-medium">{rows.length}</span> of{' '}
              <span className="font-medium">{rows.length}</span> results
            </div>
            <div className="flex items-center space-x-2">
              <button className="px-3 py-1 text-sm text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">
                Previous
              </button>
              <span className="px-3 py-1 text-sm text-gray-700 bg-white border border-gray-300 rounded-md">
                Page 1 of 1
              </span>
              <button className="px-3 py-1 text-sm text-gray-500 bg-white border border-gray-300 rounded-md hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed">
                Next
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Transactions;
