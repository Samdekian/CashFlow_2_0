import React, { useState } from 'react';
import { OFBIntegration, OFBAccountManager } from '../components/OpenFinanceBrasil';

const OpenFinancePage: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'integration' | 'accounts'>('integration');

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="py-6">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">
              Open Finance Brasil
            </h1>
            <p className="mt-2 text-gray-600">
              Connect your bank accounts and manage financial data through Open Finance Brasil integration
            </p>
          </div>

          {/* Tab Navigation */}
          <div className="border-b border-gray-200 mb-6">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('integration')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'integration'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Integration Setup
              </button>
              <button
                onClick={() => setActiveTab('accounts')}
                className={`py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'accounts'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Account Management
              </button>
            </nav>
          </div>
          
          {/* Tab Content */}
          {activeTab === 'integration' && <OFBIntegration />}
          {activeTab === 'accounts' && <OFBAccountManager />}
        </div>
      </div>
    </div>
  );
};

export default OpenFinancePage;
