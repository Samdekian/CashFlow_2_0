import { api, PaginatedResponse } from './api';

// Budget Types
export interface Budget {
  id: string;
  name: string;
  category_id: string;
  category_name?: string;
  amount: number;
  spent: number;
  remaining: number;
  period: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly';
  start_date: string;
  end_date: string;
  status: 'active' | 'inactive' | 'completed';
  progress_percentage: number;
  alerts: string[];
  created_at: string;
  updated_at: string;
}

export interface BudgetCreate {
  name: string;
  category_id: string;
  amount: number;
  period: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly';
  start_date: string;
  end_date: string;
  status?: 'active' | 'inactive' | 'completed';
}

export interface BudgetUpdate {
  name?: string;
  category_id?: string;
  amount?: number;
  period?: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly';
  start_date?: string;
  end_date?: string;
  status?: 'active' | 'inactive' | 'completed';
}

export interface BudgetFilters {
  page?: number;
  size?: number;
  category_id?: string;
  status?: 'active' | 'inactive' | 'completed';
  period?: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly';
  start_date?: string;
  end_date?: string;
}

export interface BudgetProgress {
  budget_id: string;
  spent: number;
  remaining: number;
  progress_percentage: number;
  status: 'on_track' | 'warning' | 'exceeded';
}

export interface BudgetAlert {
  budget_id: string;
  type: 'warning' | 'danger' | 'info';
  message: string;
  created_at: string;
}

// Budget Service
export const budgetService = {
  // Get all budgets with filters
  getBudgets: async (filters: BudgetFilters = {}): Promise<PaginatedResponse<Budget>> => {
    return api.get<PaginatedResponse<Budget>>('/api/v1/budgets', filters);
  },

  // Get budget by ID
  getBudget: async (id: string): Promise<Budget> => {
    return api.get<Budget>(`/api/v1/budgets/${id}`);
  },

  // Create new budget
  createBudget: async (budget: BudgetCreate): Promise<Budget> => {
    return api.post<Budget>('/api/v1/budgets', budget);
  },

  // Update budget
  updateBudget: async (id: string, budget: BudgetUpdate): Promise<Budget> => {
    return api.put<Budget>(`/api/v1/budgets/${id}`, budget);
  },

  // Delete budget
  deleteBudget: async (id: string): Promise<void> => {
    return api.delete<void>(`/api/v1/budgets/${id}`);
  },

  // Get budget progress
  getBudgetProgress: async (id: string): Promise<BudgetProgress> => {
    return api.get<BudgetProgress>(`/api/v1/budgets/${id}/progress`);
  },

  // Get budget alerts
  getBudgetAlerts: async (id: string): Promise<BudgetAlert[]> => {
    return api.get<BudgetAlert[]>(`/api/v1/budgets/${id}/alerts`);
  },

  // Activate budget
  activateBudget: async (id: string): Promise<Budget> => {
    return api.patch<Budget>(`/api/v1/budgets/${id}/activate`);
  },

  // Deactivate budget
  deactivateBudget: async (id: string): Promise<Budget> => {
    return api.patch<Budget>(`/api/v1/budgets/${id}/deactivate`);
  },

  // Get budgets by category
  getBudgetsByCategory: async (categoryId: string): Promise<Budget[]> => {
    return api.get<Budget[]>(`/api/v1/budgets/category/${categoryId}`);
  },

  // Get budgets overview
  getBudgetsOverview: async (): Promise<{
    total_budgets: number;
    active_budgets: number;
    total_amount: number;
    total_spent: number;
    total_remaining: number;
  }> => {
    return api.get('/api/v1/budgets/overview');
  },

  // Bulk create budgets
  bulkCreateBudgets: async (budgets: BudgetCreate[]): Promise<Budget[]> => {
    return api.post<Budget[]>('/api/v1/budgets/bulk', { budgets });
  },

  // Bulk delete budgets
  bulkDeleteBudgets: async (ids: string[]): Promise<void> {
    return api.delete<void>('/api/v1/budgets/bulk');
  },
};
