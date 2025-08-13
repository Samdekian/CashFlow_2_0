import { api, PaginatedResponse } from './api';

// Transaction Types
export interface Transaction {
  id: string;
  description: string;
  amount: number;
  category_id: string;
  category_name?: string;
  type: 'income' | 'expense';
  date: string;
  status: 'completed' | 'pending' | 'cancelled';
  created_at: string;
  updated_at: string;
}

export interface TransactionCreate {
  description: string;
  amount: number;
  category_id: string;
  type: 'income' | 'expense';
  date: string;
  status?: 'completed' | 'pending' | 'cancelled';
}

export interface TransactionUpdate {
  description?: string;
  amount?: number;
  category_id?: string;
  type?: 'income' | 'expense';
  date?: string;
  status?: 'completed' | 'pending' | 'cancelled';
}

export interface TransactionFilters {
  page?: number;
  size?: number;
  search?: string;
  category_id?: string;
  type?: 'income' | 'expense';
  status?: 'completed' | 'pending' | 'cancelled';
  start_date?: string;
  end_date?: string;
  min_amount?: number;
  max_amount?: number;
}

// Transaction Service
export const transactionService = {
  // Get all transactions with filters
  getTransactions: async (filters: TransactionFilters = {}): Promise<PaginatedResponse<Transaction>> => {
    return api.get<PaginatedResponse<Transaction>>('/api/v1/transactions', filters);
  },

  // Get transaction by ID
  getTransaction: async (id: string): Promise<Transaction> => {
    return api.get<Transaction>(`/api/v1/transactions/${id}`);
  },

  // Create new transaction
  createTransaction: async (transaction: TransactionCreate): Promise<Transaction> => {
    return api.post<Transaction>('/api/v1/transactions', transaction);
  },

  // Update transaction
  updateTransaction: async (id: string, transaction: TransactionUpdate): Promise<Transaction> => {
    return api.put<Transaction>(`/api/v1/transactions/${id}`, transaction);
  },

  // Delete transaction
  deleteTransaction: async (id: string): Promise<void> => {
    return api.delete<void>(`/api/v1/transactions/${id}`);
  },

  // Bulk delete transactions
  bulkDeleteTransactions: async (ids: string[]): Promise<void> => {
    return api.delete<void>('/api/v1/transactions/bulk');
  },

  // Get transaction statistics
  getTransactionStats: async (filters?: TransactionFilters) => {
    return api.get('/api/v1/transactions/stats', filters);
  },

  // Export transactions
  exportTransactions: async (format: 'csv' | 'json' | 'excel', filters?: TransactionFilters) => {
    return api.get(`/api/v1/transactions/export/${format}`, filters);
  },
};
