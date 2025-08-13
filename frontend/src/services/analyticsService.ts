import { api } from './api';

// Analytics Types
export interface SpendingSummary {
  total_income: number;
  total_expenses: number;
  net_savings: number;
  savings_rate: number;
  period: string;
}

export interface CategoryBreakdown {
  category_id: string;
  category_name: string;
  amount: number;
  percentage: number;
  transaction_count: number;
}

export interface SpendingTrend {
  date: string;
  income: number;
  expenses: number;
  net: number;
}

export interface MonthlyComparison {
  month: string;
  current_year: number;
  previous_year: number;
  change_percentage: number;
}

export interface CashFlowAnalysis {
  period: string;
  opening_balance: number;
  closing_balance: number;
  net_cash_flow: number;
  cash_in: number;
  cash_out: number;
}

export interface BudgetAnalysis {
  budget_id: string;
  budget_name: string;
  planned: number;
  actual: number;
  variance: number;
  variance_percentage: number;
  status: 'on_track' | 'warning' | 'exceeded';
}

export interface SpendingPattern {
  day_of_week: string;
  average_amount: number;
  transaction_count: number;
}

export interface FinancialHealth {
  savings_rate: number;
  debt_ratio: number;
  emergency_fund_ratio: number;
  investment_rate: number;
  budget_adherence: number;
  overall_score: number;
}

export interface AnalyticsFilters {
  start_date?: string;
  end_date?: string;
  category_id?: string;
  period?: 'daily' | 'weekly' | 'monthly' | 'quarterly' | 'yearly';
}

// Analytics Service
export const analyticsService = {
  // Get spending summary
  getSpendingSummary: async (filters: AnalyticsFilters = {}): Promise<SpendingSummary> => {
    return api.get<SpendingSummary>('/api/v1/analytics/spending-summary', filters);
  },

  // Get category breakdown
  getCategoryBreakdown: async (filters: AnalyticsFilters = {}): Promise<CategoryBreakdown[]> => {
    return api.get<CategoryBreakdown[]>('/api/v1/analytics/category-breakdown', filters);
  },

  // Get spending trends
  getSpendingTrends: async (filters: AnalyticsFilters = {}): Promise<SpendingTrend[]> => {
    return api.get<SpendingTrend[]>('/api/v1/analytics/spending-trends', filters);
  },

  // Get monthly comparison
  getMonthlyComparison: async (filters: AnalyticsFilters = {}): Promise<MonthlyComparison[]> => {
    return api.get<MonthlyComparison[]>('/api/v1/analytics/monthly-comparison', filters);
  },

  // Get cash flow analysis
  getCashFlowAnalysis: async (filters: AnalyticsFilters = {}): Promise<CashFlowAnalysis> => {
    return api.get<CashFlowAnalysis>('/api/v1/analytics/cash-flow', filters);
  },

  // Get budget analysis
  getBudgetAnalysis: async (filters: AnalyticsFilters = {}): Promise<BudgetAnalysis[]> => {
    return api.get<BudgetAnalysis[]>('/api/v1/analytics/budget-analysis', filters);
  },

  // Get spending patterns
  getSpendingPatterns: async (filters: AnalyticsFilters = {}): Promise<SpendingPattern[]> => {
    return api.get<SpendingPattern[]>('/api/v1/analytics/spending-patterns', filters);
  },

  // Get financial health
  getFinancialHealth: async (filters: AnalyticsFilters = {}): Promise<FinancialHealth> => {
    return api.get<FinancialHealth>('/api/v1/analytics/financial-health', filters);
  },

  // Get category analysis
  getCategoryAnalysis: async (categoryId: string, filters: AnalyticsFilters = {}): Promise<{
    category: CategoryBreakdown;
    trends: SpendingTrend[];
    patterns: SpendingPattern[];
  }> => {
    return api.get(`/api/v1/analytics/categories/${categoryId}`, filters);
  },

  // Export analytics report
  exportAnalyticsReport: async (format: 'csv' | 'json' | 'excel', filters: AnalyticsFilters = {}) => {
    return api.get(`/api/v1/analytics/export/${format}`, filters);
  },

  // Get insights and recommendations
  getInsightsAndRecommendations: async (filters: AnalyticsFilters = {}): Promise<{
    insights: string[];
    recommendations: string[];
    risk_level: 'low' | 'medium' | 'high';
  }> => {
    return api.get('/api/v1/analytics/insights', filters);
  },

  // Get performance benchmarks
  getPerformanceBenchmarks: async (filters: AnalyticsFilters = {}): Promise<{
    personal_best: SpendingSummary;
    monthly_average: SpendingSummary;
    industry_benchmark: SpendingSummary;
  }> => {
    return api.get('/api/v1/analytics/benchmarks', filters);
  },
};
