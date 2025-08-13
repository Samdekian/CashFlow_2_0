import React, { useState } from 'react';
import { 
  PlusIcon, 
  FolderIcon,
  ChevronRightIcon,
  ChevronDownIcon,
  PencilIcon,
  TrashIcon,
  EyeIcon
} from '@heroicons/react/24/outline';

interface Category {
  id: string;
  name: string;
  description: string;
  level: number;
  parent_id?: string;
  children?: Category[];
  transaction_count: number;
  total_amount: number;
  is_active: boolean;
  color: string;
}

const Categories: React.FC = () => {
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());
  const [selectedCategory, setSelectedCategory] = useState<Category | null>(null);

  // Mock data - in real app, this would come from API
  const categories: Category[] = [
    {
      id: '1',
      name: 'Alimentação',
      description: 'Food and dining expenses',
      level: 1,
      transaction_count: 45,
      total_amount: -1200.50,
      is_active: true,
      color: '#3B82F6',
      children: [
        {
          id: '1.1',
          name: 'Supermercado',
          description: 'Grocery shopping',
          level: 2,
          parent_id: '1',
          transaction_count: 25,
          total_amount: -800.30,
          is_active: true,
          color: '#60A5FA',
          children: [
            {
              id: '1.1.1',
              name: 'Produtos Básicos',
              description: 'Basic household products',
              level: 3,
              parent_id: '1.1',
              transaction_count: 15,
              total_amount: -450.20,
              is_active: true,
              color: '#93C5FD',
            }
          ]
        },
        {
          id: '1.2',
          name: 'Restaurantes',
          description: 'Restaurant and dining out',
          level: 2,
          parent_id: '1',
          transaction_count: 20,
          total_amount: -400.20,
          is_active: true,
          color: '#60A5FA',
        }
      ]
    },
    {
      id: '2',
      name: 'Transporte',
      description: 'Transportation expenses',
      level: 1,
      transaction_count: 18,
      total_amount: -450.00,
      is_active: true,
      color: '#10B981',
      children: [
        {
          id: '2.1',
          name: 'Combustível',
          description: 'Fuel and gas',
          level: 2,
          parent_id: '2',
          transaction_count: 12,
          total_amount: -320.00,
          is_active: true,
          color: '#34D399',
        },
        {
          id: '2.2',
          name: 'Transporte Público',
          description: 'Public transportation',
          level: 2,
          parent_id: '2',
          transaction_count: 6,
          total_amount: -130.00,
          is_active: true,
          color: '#34D399',
        }
      ]
    },
    {
      id: '3',
      name: 'Entretenimento',
      description: 'Entertainment and leisure',
      level: 1,
      transaction_count: 12,
      total_amount: -280.00,
      is_active: true,
      color: '#F59E0B',
      children: [
        {
          id: '3.1',
          name: 'Streaming',
          description: 'Video and music streaming services',
          level: 2,
          parent_id: '3',
          transaction_count: 8,
          total_amount: -180.00,
          is_active: true,
          color: '#FBBF24',
        }
      ]
    },
    {
      id: '4',
      name: 'Receitas',
      description: 'Income and earnings',
      level: 1,
      transaction_count: 8,
      total_amount: 8500.00,
      is_active: true,
      color: '#22C55E',
      children: [
        {
          id: '4.1',
          name: 'Salário',
          description: 'Regular salary income',
          level: 2,
          parent_id: '4',
          transaction_count: 6,
          total_amount: 7200.00,
          is_active: true,
          color: '#4ADE80',
        },
        {
          id: '4.2',
          name: 'Freelance',
          description: 'Freelance and side income',
          level: 2,
          parent_id: '4',
          transaction_count: 2,
          total_amount: 1300.00,
          is_active: true,
          color: '#4ADE80',
        }
      ]
    }
  ];

  const toggleExpanded = (categoryId: string) => {
    const newExpanded = new Set(expandedCategories);
    if (newExpanded.has(categoryId)) {
      newExpanded.delete(categoryId);
    } else {
      newExpanded.add(categoryId);
    }
    setExpandedCategories(newExpanded);
  };

  const renderCategory = (category: Category, depth: number = 0) => {
    const isExpanded = expandedCategories.has(category.id);
    const hasChildren = category.children && category.children.length > 0;

    return (
      <div key={category.id}>
        <div 
          className={`flex items-center justify-between p-3 hover:bg-gray-50 cursor-pointer border-l-4 ${
            category.level === 1 ? 'bg-white' : 'bg-gray-50'
          }`}
          style={{ borderLeftColor: category.color }}
        >
          <div className="flex items-center space-x-3" style={{ marginLeft: `${depth * 20}px` }}>
            {hasChildren && (
              <button
                onClick={() => toggleExpanded(category.id)}
                className="p-1 hover:bg-gray-200 rounded"
              >
                {isExpanded ? (
                  <ChevronDownIcon className="w-4 h-4 text-gray-500" />
                ) : (
                  <ChevronRightIcon className="w-4 h-4 text-gray-500" />
                )}
              </button>
            )}
            {!hasChildren && <div className="w-6" />}
            
            <FolderIcon className="w-5 h-5 text-gray-400" />
            <div>
              <h4 className="font-medium text-gray-900">{category.name}</h4>
              <p className="text-sm text-gray-500">{category.description}</p>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-sm font-medium text-gray-900">
                {category.transaction_count} transactions
              </p>
              <p className={`text-sm font-semibold ${
                category.total_amount >= 0 ? 'text-success-600' : 'text-danger-600'
              }`}>
                {category.total_amount >= 0 ? '+' : ''}R$ {Math.abs(category.total_amount).toFixed(2)}
              </p>
            </div>
            
            <div className="flex items-center space-x-2">
              <button 
                onClick={() => setSelectedCategory(category)}
                className="p-1 text-gray-400 hover:text-primary-600 transition-colors"
              >
                <EyeIcon className="w-4 h-4" />
              </button>
              <button className="p-1 text-gray-400 hover:text-warning-600 transition-colors">
                <PencilIcon className="w-4 h-4" />
              </button>
              <button className="p-1 text-gray-400 hover:text-danger-600 transition-colors">
                <TrashIcon className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>

        {hasChildren && isExpanded && (
          <div className="border-l border-gray-200 ml-6">
            {category.children!.map(child => renderCategory(child, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Categories</h1>
          <p className="text-gray-600">Manage your transaction categories with Open Finance Brasil compliance.</p>
        </div>
        <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-colors duration-200">
          <PlusIcon className="w-4 h-4 mr-2" />
          New Category
        </button>
      </div>

      {/* Open Finance Brasil Compliance Info */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
        <div className="flex items-start space-x-3">
          <div className="flex-shrink-0">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">OF</span>
            </div>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-blue-900">Open Finance Brasil Compliant</h3>
            <p className="text-blue-700 mt-1">
              This category structure follows the official Open Finance Brasil standards with 3-level hierarchy:
              <br />
              <strong>Level 1:</strong> Main categories (Alimentação, Transporte, etc.)
              <br />
              <strong>Level 2:</strong> Sub-categories (Supermercado, Restaurantes, etc.)
              <br />
              <strong>Level 3:</strong> Specific categories (Produtos Básicos, etc.)
            </p>
          </div>
        </div>
      </div>

      {/* Categories Tree */}
      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">
            Category Hierarchy ({categories.length} main categories)
          </h3>
        </div>
        
        <div className="divide-y divide-gray-200">
          {categories.map(category => renderCategory(category))}
        </div>
      </div>

      {/* Category Details Modal */}
      {selectedCategory && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">Category Details</h3>
                <button
                  onClick={() => setSelectedCategory(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ✕
                </button>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Name</label>
                  <p className="mt-1 text-sm text-gray-900">{selectedCategory.name}</p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700">Description</label>
                  <p className="mt-1 text-sm text-gray-900">{selectedCategory.description}</p>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Level</label>
                    <p className="mt-1 text-sm text-gray-900">{selectedCategory.level}</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Status</label>
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      selectedCategory.is_active 
                        ? 'bg-success-100 text-success-800' 
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {selectedCategory.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Transactions</label>
                    <p className="mt-1 text-sm text-gray-900">{selectedCategory.transaction_count}</p>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Total Amount</label>
                    <p className={`mt-1 text-sm font-semibold ${
                      selectedCategory.total_amount >= 0 ? 'text-success-600' : 'text-danger-600'
                    }`}>
                      {selectedCategory.total_amount >= 0 ? '+' : ''}R$ {Math.abs(selectedCategory.total_amount).toFixed(2)}
                    </p>
                  </div>
                </div>
                
                {selectedCategory.children && selectedCategory.children.length > 0 && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700">Sub-categories</label>
                    <div className="mt-1 space-y-1">
                      {selectedCategory.children.map(child => (
                        <div key={child.id} className="flex items-center justify-between text-sm">
                          <span className="text-gray-900">{child.name}</span>
                          <span className="text-gray-500">{child.transaction_count} transactions</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
              
              <div className="flex items-center justify-end space-x-3 mt-6">
                <button
                  onClick={() => setSelectedCategory(null)}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                  Close
                </button>
                <button className="px-4 py-2 text-sm font-medium text-white bg-primary-600 border border-transparent rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
                  Edit Category
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Categories;
