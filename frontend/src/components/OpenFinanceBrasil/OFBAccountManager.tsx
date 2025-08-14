import React, { useState, useEffect } from 'react';
import { 
  BanknotesIcon, 
  ArrowPathIcon,
  ClockIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
  PlusIcon,
  TrashIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline';

interface OFBAccount {
  account_id: string;
  type: string;
  subtype: string;
  currency: string;
  brand_name: string;
  company_cnpj: string;
  number: string;
  check_digit: string;
  agency_number: string;
  agency_check_digit: string;
  status: string;
}

interface OFBAccountBalance {
  available_amount: string;
  available_amount_currency: string;
  blocked_amount: string;
  blocked_amount_currency: string;
  automatically_invested_amount: string;
  automatically_invested_amount_currency: string;
  last_updated: string;
}

interface OFBTransaction {
  transaction_id: string;
  booking_date: string;
  amount: string;
  currency: string;
  credit_debit_type: string;
  transaction_name: string;
  reference_number?: string;
  type?: string;
  transaction_category?: string;
}

interface OFBImportResult {
  status: string;
  imported_count: number;
  skipped_count: number;
  total_processed: number;
  errors: string[];
  account_id: string;
  date_range: {
    from?: string;
    to?: string;
  };
}

const OFBAccountManager: React.FC = () => {
  const [accounts, setAccounts] = useState<OFBAccount[]>([]);
  const [selectedAccount, setSelectedAccount] = useState<OFBAccount | null>(null);
  const [accountBalance, setAccountBalance] = useState<OFBAccountBalance | null>(null);
  const [transactions, setTransactions] = useState<OFBTransaction[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [importResult, setImportResult] = useState<OFBImportResult | null>(null);
  const [showImportForm, setShowImportForm] = useState(false);
  const [importForm, setImportForm] = useState({
    consent_id: '',
    access_token: '',
    from_date: '',
    to_date: '',
    auto_categorize: true
  });

  // Mock data for development
  useEffect(() => {
    // Simulate loading accounts
    setLoading(true);
    setTimeout(() => {
      const mockAccounts: OFBAccount[] = [
        {
          account_id: "account_001",
          type: "CACC",
          subtype: "CURRENT_ACCOUNT",
          currency: "BRL",
          brand_name: "Banco do Brasil",
          company_cnpj: "00000000000191",
          number: "12345-6",
          check_digit: "7",
          agency_number: "1234",
          agency_check_digit: "5",
          status: "ACTIVE"
        },
        {
          account_id: "account_002",
          type: "SVGS",
          subtype: "SAVINGS_ACCOUNT",
          currency: "BRL",
          brand_name: "Banco do Brasil",
          company_cnpj: "00000000000191",
          number: "98765-4",
          check_digit: "3",
          agency_number: "1234",
          agency_check_digit: "5",
          status: "ACTIVE"
        }
      ];
      setAccounts(mockAccounts);
      setLoading(false);
    }, 1000);
  }, []);

  const handleAccountSelect = async (account: OFBAccount) => {
    setSelectedAccount(account);
    setLoading(true);
    setError(null);

    try {
      // In production, this would call the actual API
      // For now, use mock data
      const mockBalance: OFBAccountBalance = {
        available_amount: "1250.75",
        available_amount_currency: "BRL",
        blocked_amount: "0.00",
        blocked_amount_currency: "BRL",
        automatically_invested_amount: "500.00",
        automatically_invested_amount_currency: "BRL",
        last_updated: new Date().toISOString()
      };

      const mockTransactions: OFBTransaction[] = [
        {
          transaction_id: "txn_001",
          booking_date: "2024-01-15",
          amount: "150.50",
          currency: "BRL",
          credit_debit_type: "DEBITO",
          transaction_name: "RESTAURANTE ABC",
          reference_number: "REF123456",
          type: "PURCHASE",
          transaction_category: "ALIMENTACAO"
        },
        {
          transaction_id: "txn_002",
          booking_date: "2024-01-14",
          amount: "2500.00",
          currency: "BRL",
          credit_debit_type: "CREDITO",
          transaction_name: "SALARIO",
          reference_number: "REF789012",
          type: "CREDIT",
          transaction_category: "RECEITA"
        }
      ];

      setAccountBalance(mockBalance);
      setTransactions(mockTransactions);
    } catch (err) {
      setError('Failed to load account details');
    } finally {
      setLoading(false);
    }
  };

  const handleImportTransactions = async () => {
    if (!selectedAccount || !importForm.consent_id || !importForm.access_token) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // In production, this would call the actual API
      // For now, simulate import
      await new Promise(resolve => setTimeout(resolve, 2000));

      const mockImportResult: OFBImportResult = {
        status: "completed",
        imported_count: 15,
        skipped_count: 3,
        total_processed: 18,
        errors: [],
        account_id: selectedAccount.account_id,
        date_range: {
          from: importForm.from_date || undefined,
          to: importForm.to_date || undefined
        }
      };

      setImportResult(mockImportResult);
      setShowImportForm(false);
    } catch (err) {
      setError('Failed to import transactions');
    } finally {
      setLoading(false);
    }
  };

  const getAccountTypeLabel = (type: string) => {
    const typeLabels: { [key: string]: string } = {
      'CACC': 'Current Account',
      'SVGS': 'Savings Account',
      'CRDT': 'Credit Account',
      'LOAN': 'Loan Account'
    };
    return typeLabels[type] || type;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return 'text-green-600 bg-green-100';
      case 'INACTIVE':
        return 'text-red-600 bg-red-100';
      case 'SUSPENDED':
        return 'text-yellow-600 bg-yellow-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading && accounts.length === 0) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center space-x-3 mb-6">
          <BanknotesIcon className="h-8 w-8 text-blue-600" />
          <h1 className="text-2xl font-bold text-gray-900">
            Open Finance Brasil Account Manager
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

        {/* Account List */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Connected Accounts</h2>
            <div className="space-y-3">
              {accounts.map((account) => (
                <div
                  key={account.account_id}
                  className={`p-4 border rounded-lg cursor-pointer transition-colors ${
                    selectedAccount?.account_id === account.account_id
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                  onClick={() => handleAccountSelect(account)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium text-gray-900">{account.brand_name}</h3>
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(account.status)}`}>
                      {account.status}
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-1">
                    {getAccountTypeLabel(account.type)} - {account.number}
                  </p>
                  <p className="text-sm text-gray-500">
                    Agency: {account.agency_number} | Currency: {account.currency}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Account Details */}
          <div className="lg:col-span-2">
            {selectedAccount ? (
              <div>
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-gray-900">
                    {selectedAccount.brand_name} - {selectedAccount.number}
                  </h2>
                  <button
                    onClick={() => setShowImportForm(true)}
                    className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition-colors"
                  >
                    <PlusIcon className="h-4 w-4" />
                    <span>Import Transactions</span>
                  </button>
                </div>

                {/* Account Balance */}
                {accountBalance && (
                  <div className="bg-gray-50 rounded-lg p-4 mb-6">
                    <h3 className="font-medium text-gray-900 mb-3">Account Balance</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div>
                        <p className="text-sm text-gray-600">Available Balance</p>
                        <p className="text-lg font-semibold text-green-600">
                          R$ {parseFloat(accountBalance.available_amount).toFixed(2)}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Blocked Amount</p>
                        <p className="text-lg font-semibold text-yellow-600">
                          R$ {parseFloat(accountBalance.blocked_amount).toFixed(2)}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Invested Amount</p>
                        <p className="text-lg font-semibold text-blue-600">
                          R$ {parseFloat(accountBalance.automatically_invested_amount).toFixed(2)}
                        </p>
                      </div>
                    </div>
                    <p className="text-xs text-gray-500 mt-2">
                      Last updated: {new Date(accountBalance.last_updated).toLocaleString()}
                    </p>
                  </div>
                )}

                {/* Recent Transactions */}
                {transactions.length > 0 && (
                  <div>
                    <h3 className="font-medium text-gray-900 mb-3">Recent Transactions</h3>
                    <div className="space-y-2">
                      {transactions.map((transaction) => (
                        <div key={transaction.transaction_id} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                          <div className="flex-1">
                            <p className="font-medium text-gray-900">{transaction.transaction_name}</p>
                            <p className="text-sm text-gray-600">
                              {new Date(transaction.booking_date).toLocaleDateString()} • {transaction.transaction_category}
                            </p>
                          </div>
                          <div className="text-right">
                            <p className={`font-semibold ${
                              transaction.credit_debit_type === 'CREDITO' ? 'text-green-600' : 'text-red-600'
                            }`}>
                              {transaction.credit_debit_type === 'CREDITO' ? '+' : '-'} R$ {parseFloat(transaction.amount).toFixed(2)}
                            </p>
                            <p className="text-xs text-gray-500">{transaction.type}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-12">
                <BanknotesIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">Select an Account</h3>
                <p className="text-gray-500">Choose an account from the list to view details and manage transactions.</p>
              </div>
            )}
          </div>
        </div>

        {/* Import Form Modal */}
        {showImportForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Import Transactions</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Consent ID *
                  </label>
                  <input
                    type="text"
                    value={importForm.consent_id}
                    onChange={(e) => setImportForm({...importForm, consent_id: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter consent ID"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Access Token *
                  </label>
                  <input
                    type="text"
                    value={importForm.access_token}
                    onChange={(e) => setImportForm({...importForm, access_token: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Enter access token"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      From Date
                    </label>
                    <input
                      type="date"
                      value={importForm.from_date}
                      onChange={(e) => setImportForm({...importForm, from_date: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      To Date
                    </label>
                    <input
                      type="date"
                      value={importForm.to_date}
                      onChange={(e) => setImportForm({...importForm, to_date: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="auto_categorize"
                    checked={importForm.auto_categorize}
                    onChange={(e) => setImportForm({...importForm, auto_categorize: e.target.checked})}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <label htmlFor="auto_categorize" className="ml-2 text-sm text-gray-700">
                    Auto-categorize transactions
                  </label>
                </div>
              </div>

              <div className="flex space-x-3 mt-6">
                <button
                  onClick={() => setShowImportForm(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={handleImportTransactions}
                  disabled={loading}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:bg-gray-400 transition-colors"
                >
                  {loading ? 'Importing...' : 'Import'}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Import Result */}
        {importResult && (
          <div className="mt-6 bg-green-50 border border-green-200 rounded-md p-4">
            <div className="flex">
              <CheckCircleIcon className="h-5 w-5 text-green-400" />
              <div className="ml-3">
                <h3 className="text-sm font-medium text-green-800">Import Completed</h3>
                <div className="mt-2 text-sm text-green-700">
                  <p>Successfully imported {importResult.imported_count} transactions</p>
                  <p>Skipped {importResult.skipped_count} existing transactions</p>
                  <p>Total processed: {importResult.total_processed}</p>
                  {importResult.errors.length > 0 && (
                    <p className="text-red-600 mt-2">
                      Errors: {importResult.errors.join(', ')}
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default OFBAccountManager;
