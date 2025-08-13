import React, { useState, useEffect } from 'react';
import { 
  BanknotesIcon, 
  ShieldCheckIcon, 
  KeyIcon, 
  CheckCircleIcon,
  ExclamationTriangleIcon 
} from '@heroicons/react/24/outline';

interface OFBStatus {
  status: string;
  initialized: boolean;
  configuration: {
    enabled: boolean;
    sandbox_mode: boolean;
    mock_mode: boolean;
    client_configured: boolean;
    certificates_exist: boolean;
  };
}

interface OFBConnection {
  authorization_url: string;
  consent_id: string;
  state: string;
  nonce: string;
  expires_at: string;
  scopes: string[];
}

const OFBIntegration: React.FC = () => {
  const [status, setStatus] = useState<OFBStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [connection, setConnection] = useState<OFBConnection | null>(null);
  const [connecting, setConnecting] = useState(false);

  useEffect(() => {
    fetchOFBStatus();
  }, []);

  const fetchOFBStatus = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/open-finance/health');
      if (response.ok) {
        const data = await response.json();
        setStatus(data);
        setError(null);
      } else {
        setError('Failed to fetch OFB status');
      }
    } catch (err) {
      setError('Error connecting to OFB service');
    } finally {
      setLoading(false);
    }
  };

  const initiateConnection = async () => {
    try {
      setConnecting(true);
      const response = await fetch('/api/v1/open-finance/connect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: '12345678901', // Mock CPF
          scopes: ['accounts', 'transactions'],
          expiration_days: 90
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setConnection(data);
        // In a real app, redirect to the authorization URL
        window.open(data.authorization_url, '_blank');
      } else {
        setError('Failed to initiate connection');
      }
    } catch (err) {
      setError('Error initiating connection');
    } finally {
      setConnecting(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy':
        return 'text-green-600';
      case 'degraded':
        return 'text-yellow-600';
      case 'unhealthy':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircleIcon className="h-6 w-6 text-green-600" />;
      case 'degraded':
        return <ExclamationTriangleIcon className="h-6 w-6 text-yellow-600" />;
      case 'unhealthy':
        return <ExclamationTriangleIcon className="h-6 w-6 text-red-600" />;
      default:
        return <ExclamationTriangleIcon className="h-6 w-6 text-gray-600" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center space-x-3 mb-6">
          <BanknotesIcon className="h-8 w-8 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900">
            Open Finance Brasil Integration
          </h1>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4 mb-6">
            <div className="flex">
              <ExclamationTriangleIcon className="h-5 w-5 text-red-400" />
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">Error</h3>
                <div className="mt-2 text-sm text-red-700">{error}</div>
              </div>
            </div>
          </div>
        )}

        {/* Status Overview */}
        {status && (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-3">
                {getStatusIcon(status.status)}
                <h3 className="text-lg font-semibold text-gray-900">Integration Status</h3>
              </div>
              <div className={`text-sm font-medium ${getStatusColor(status.status)}`}>
                {status.status.charAt(0).toUpperCase() + status.status.slice(1)}
              </div>
              <div className="text-sm text-gray-600 mt-1">
                Initialized: {status.initialized ? 'Yes' : 'No'}
              </div>
            </div>

            <div className="bg-gray-50 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-3">
                <ShieldCheckIcon className="h-5 w-5 text-blue-600" />
                <h3 className="text-lg font-semibold text-gray-900">Configuration</h3>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Enabled:</span>
                  <span className={status.configuration.enabled ? 'text-green-600' : 'text-red-600'}>
                    {status.configuration.enabled ? 'Yes' : 'No'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Sandbox Mode:</span>
                  <span className={status.configuration.sandbox_mode ? 'text-blue-600' : 'text-gray-600'}>
                    {status.configuration.sandbox_mode ? 'Yes' : 'No'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Client Configured:</span>
                  <span className={status.configuration.client_configured ? 'text-green-600' : 'text-red-600'}>
                    {status.configuration.client_configured ? 'Yes' : 'No'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Certificates:</span>
                  <span className={status.configuration.certificates_exist ? 'text-green-600' : 'text-red-600'}>
                    {status.configuration.certificates_exist ? 'Valid' : 'Missing'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Connection Section */}
        <div className="bg-blue-50 rounded-lg p-6 mb-6">
          <div className="flex items-center space-x-3 mb-4">
            <KeyIcon className="h-6 w-6 text-blue-600" />
            <h3 className="text-lg font-semibold text-gray-900">Bank Connection</h3>
          </div>
          
          <p className="text-gray-600 mb-4">
            Connect your bank account via Open Finance Brasil to automatically import transactions 
            and get real-time financial data.
          </p>

          <button
            onClick={initiateConnection}
            disabled={connecting || !status?.configuration.enabled}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-medium py-2 px-4 rounded-md transition-colors duration-200"
          >
            {connecting ? 'Connecting...' : 'Connect Bank Account'}
          </button>

          {!status?.configuration.enabled && (
            <p className="text-sm text-red-600 mt-2">
              Open Finance Brasil integration is not enabled. Please check your configuration.
            </p>
          )}
        </div>

        {/* Connection Details */}
        {connection && (
          <div className="bg-green-50 rounded-lg p-4">
            <h4 className="font-medium text-green-800 mb-2">Connection Initiated</h4>
            <div className="text-sm text-green-700 space-y-1">
              <div><strong>Consent ID:</strong> {connection.consent_id}</div>
              <div><strong>Expires:</strong> {new Date(connection.expires_at).toLocaleString()}</div>
              <div><strong>Scopes:</strong> {connection.scopes.join(', ')}</div>
            </div>
            <p className="text-sm text-green-600 mt-2">
              Please complete the authorization in the new window that opened.
            </p>
          </div>
        )}

        {/* Features */}
        <div className="mt-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Features</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <BanknotesIcon className="h-8 w-8 text-blue-600 mx-auto mb-2" />
              <h4 className="font-medium text-gray-900">Account Sync</h4>
              <p className="text-sm text-gray-600">Automatically sync bank accounts and balances</p>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <ShieldCheckIcon className="h-8 w-8 text-green-600 mx-auto mb-2" />
              <h4 className="font-medium text-gray-900">Secure</h4>
              <p className="text-sm text-gray-600">OAuth 2.0 + FAPI compliant security</p>
            </div>
            <div className="text-center p-4 bg-gray-50 rounded-lg">
              <KeyIcon className="h-8 w-8 text-purple-600 mx-auto mb-2" />
              <h4 className="font-medium text-gray-900">Consent Management</h4>
              <p className="text-sm text-gray-600">Full control over data access permissions</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OFBIntegration;
