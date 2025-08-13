import React, { useState } from 'react';
import { 
  ArrowUpTrayIcon,
  ArrowDownTrayIcon,
  DocumentTextIcon,
  EyeIcon,
  TrashIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from '@heroicons/react/24/outline';

const ImportExport: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'import' | 'export'>('import');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Import & Export</h1>
          <p className="text-gray-600">Import financial data and export reports in multiple formats.</p>
        </div>
      </div>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            <button
              onClick={() => setActiveTab('import')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'import'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <ArrowUpTrayIcon className="w-5 h-5 inline mr-2" />
              Import Data
            </button>
            <button
              onClick={() => setActiveTab('export')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'export'
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              <ArrowDownTrayIcon className="w-5 h-5 inline mr-2" />
              Export Data
            </button>
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'import' ? (
            <div className="space-y-6">
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                <div className="flex flex-col items-center">
                  <ArrowUpTrayIcon className="w-12 h-12 text-gray-400 mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Upload Financial Data</h3>
                  <p className="text-gray-600 mb-4">
                    Drag and drop files here, or click to select files
                  </p>
                  
                  <div className="flex items-center space-x-4">
                    <input
                      type="file"
                      accept=".csv,.ofx,.xlsx,.xls"
                      onChange={handleFileSelect}
                      className="hidden"
                      id="file-upload"
                    />
                    <label
                      htmlFor="file-upload"
                      className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 cursor-pointer"
                    >
                      Select Files
                    </label>
                  </div>
                  
                  {selectedFile && (
                    <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                      <p className="text-sm text-blue-800">
                        Selected: <strong>{selectedFile.name}</strong> ({(selectedFile.size / 1024).toFixed(1)} KB)
                      </p>
                    </div>
                  )}
                </div>
              </div>

              <div className="bg-gray-50 rounded-lg p-4">
                <h4 className="text-sm font-medium text-gray-900 mb-2">Supported Import Formats</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <DocumentTextIcon className="w-4 h-4" />
                    <span>CSV</span>
                    <span className="text-gray-400">(.csv)</span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <DocumentTextIcon className="w-4 h-4" />
                    <span>OFX</span>
                    <span className="text-gray-400">(.ofx)</span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm text-gray-600">
                    <DocumentTextIcon className="w-4 h-4" />
                    <span>Excel</span>
                    <span className="text-gray-400">(.xlsx, .xls)</span>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div className="space-y-6">
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Export Configuration</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Export Format</label>
                    <div className="grid grid-cols-2 gap-3">
                      <label className="flex items-center">
                        <input type="radio" name="exportFormat" value="csv" defaultChecked className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300" />
                        <span className="ml-2 text-sm text-gray-700">CSV</span>
                      </label>
                      <label className="flex items-center">
                        <input type="radio" name="exportFormat" value="excel" className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300" />
                        <span className="ml-2 text-sm text-gray-700">Excel</span>
                      </label>
                      <label className="flex items-center">
                        <input type="radio" name="exportFormat" value="pdf" className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300" />
                        <span className="ml-2 text-sm text-gray-700">PDF</span>
                      </label>
                      <label className="flex items-center">
                        <input type="radio" name="exportFormat" value="json" className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300" />
                        <span className="ml-2 text-sm text-gray-700">JSON</span>
                      </label>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Date Range</label>
                    <select className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500">
                      <option value="lastmonth">Last Month</option>
                      <option value="last3months">Last 3 Months</option>
                      <option value="last6months">Last 6 Months</option>
                      <option value="lastyear">Last Year</option>
                      <option value="thisyear">This Year</option>
                      <option value="custom">Custom Range</option>
                    </select>
                  </div>
                </div>

                <div className="mt-6">
                  <button className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
                    <ArrowDownTrayIcon className="w-4 h-4 mr-2" />
                    Generate Export
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ImportExport;
