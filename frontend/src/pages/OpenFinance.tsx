import React from 'react';
import { OFBIntegration } from '../components/OpenFinanceBrasil';

const OpenFinancePage: React.FC = () => {
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
          
          <OFBIntegration />
        </div>
      </div>
    </div>
  );
};

export default OpenFinancePage;
