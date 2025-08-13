// Integration Configuration
export const INTEGRATION_CONFIG = {
  // API Configuration
  API: {
    BASE_URL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
    TIMEOUT: 30000,
    RETRY_ATTEMPTS: 3,
    RETRY_DELAY: 1000,
  },

  // Feature Flags
  FEATURES: {
    REAL_TIME_UPDATES: true,
    OFFLINE_SUPPORT: false,
    ADVANCED_ANALYTICS: true,
    IMPORT_EXPORT: true,
    BUDGET_ALERTS: true,
    OPEN_FINANCE_COMPLIANCE: true,
  },

  // Open Finance Brasil Compliance
  OPEN_FINANCE: {
    STANDARDS_VERSION: '1.0.0',
    SUPPORTED_CATEGORIES: [
      'FOOD_AND_DINING',
      'TRANSPORTATION',
      'ENTERTAINMENT',
      'SHOPPING',
      'HEALTHCARE',
      'EDUCATION',
      'TRAVEL',
      'UTILITIES',
      'INSURANCE',
      'INVESTMENTS',
      'INCOME',
      'OTHER',
    ],
    REQUIRED_FIELDS: [
      'description',
      'amount',
      'category_id',
      'type',
      'date',
      'status',
    ],
    VALIDATION_RULES: {
      amount: {
        min: 0.01,
        max: 999999.99,
        precision: 2,
      },
      description: {
        min_length: 1,
        max_length: 255,
      },
      date: {
        format: 'YYYY-MM-DD',
        min_date: '2020-01-01',
        max_date: '2030-12-31',
      },
    },
  },

  // Error Handling
  ERROR_HANDLING: {
    SHOW_USER_FRIENDLY_MESSAGES: true,
    LOG_ERRORS_TO_CONSOLE: process.env.NODE_ENV === 'development',
    RETRY_ON_NETWORK_ERROR: true,
    MAX_RETRY_ATTEMPTS: 3,
  },

  // Performance
  PERFORMANCE: {
    DEBOUNCE_DELAY: 300,
    CACHE_TTL: 5 * 60 * 1000, // 5 minutes
    LAZY_LOAD_THRESHOLD: 100,
    VIRTUAL_SCROLL_THRESHOLD: 1000,
  },

  // Testing
  TESTING: {
    MOCK_API_RESPONSES: process.env.NODE_ENV === 'test',
    API_RESPONSE_DELAY: 100,
    ENABLE_LOGGING: process.env.NODE_ENV === 'development',
  },
};

// Integration Status
export interface IntegrationStatus {
  backend: {
    connected: boolean;
    health: 'healthy' | 'degraded' | 'unhealthy';
    last_check: string;
    response_time: number;
  };
  database: {
    connected: boolean;
    tables: string[];
    last_backup: string;
  };
  services: {
    transactions: boolean;
    categories: boolean;
    budgets: boolean;
    analytics: boolean;
    import_export: boolean;
  };
}

// Default Integration Status
export const DEFAULT_INTEGRATION_STATUS: IntegrationStatus = {
  backend: {
    connected: false,
    health: 'unhealthy',
    last_check: new Date().toISOString(),
    response_time: 0,
  },
  database: {
    connected: false,
    tables: [],
    last_backup: new Date().toISOString(),
  },
  services: {
    transactions: false,
    categories: false,
    budgets: false,
    analytics: false,
    import_export: false,
  },
};

// Integration Utilities
export const IntegrationUtils = {
  // Check if all services are healthy
  isSystemHealthy: (status: IntegrationStatus): boolean => {
    return (
      status.backend.connected &&
      status.backend.health === 'healthy' &&
      status.database.connected &&
      Object.values(status.services).every(service => service)
    );
  },

  // Get system health score (0-100)
  getHealthScore: (status: IntegrationStatus): number => {
    let score = 0;
    
    if (status.backend.connected) score += 20;
    if (status.backend.health === 'healthy') score += 20;
    if (status.database.connected) score += 20;
    
    const serviceScore = Object.values(status.services).filter(Boolean).length * 10;
    score += Math.min(serviceScore, 40);
    
    return score;
  },

  // Format health status for display
  formatHealthStatus: (status: IntegrationStatus): string => {
    const score = IntegrationUtils.getHealthScore(status);
    
    if (score >= 90) return 'Excellent';
    if (score >= 75) return 'Good';
    if (score >= 50) return 'Fair';
    if (score >= 25) return 'Poor';
    return 'Critical';
  },
};
