import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from './App';

// Mock the components to avoid complex dependencies
jest.mock('./components/layout/Layout', () => {
  return function MockLayout({ children }: { children: React.ReactNode }) {
    return <div data-testid="layout">{children}</div>;
  };
});

jest.mock('./components/layout/Sidebar', () => {
  return function MockSidebar() {
    return <div data-testid="sidebar">Sidebar</div>;
  };
});

jest.mock('./components/layout/Header', () => {
  return function MockHeader() {
    return <div data-testid="header">Header</div>;
  };
});

jest.mock('./pages/Dashboard', () => {
  return function MockDashboard() {
    return <div data-testid="dashboard">Dashboard</div>;
  };
});

jest.mock('./pages/Transactions', () => {
  return function MockTransactions() {
    return <div data-testid="transactions">Transactions</div>;
  };
});

jest.mock('./pages/Categories', () => {
  return function MockCategories() {
    return <div data-testid="categories">Categories</div>;
  };
});

jest.mock('./pages/Budgets', () => {
  return function MockBudgets() {
    return <div data-testid="budgets">Budgets</div>;
  };
});

jest.mock('./pages/Analytics', () => {
  return function MockAnalytics() {
    return <div data-testid="analytics">Analytics</div>;
  };
});

jest.mock('./pages/ImportExport', () => {
  return function MockImportExport() {
    return <div data-testid="import-export">Import/Export</div>;
  };
});

jest.mock('./pages/Settings', () => {
  return function MockSettings() {
    return <div data-testid="settings">Settings</div>;
  };
});

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  );
};

describe('CashFlow App', () => {
  test('renders the main application structure', () => {
    renderWithProviders(<App />);
    
    expect(screen.getByTestId('layout')).toBeInTheDocument();
    expect(screen.getByTestId('sidebar')).toBeInTheDocument();
    expect(screen.getByTestId('header')).toBeInTheDocument();
  });

  test('renders dashboard by default', () => {
    renderWithProviders(<App />);
    
    expect(screen.getByTestId('dashboard')).toBeInTheDocument();
  });

  test('renders with proper styling classes', () => {
    renderWithProviders(<App />);
    
    const appElement = screen.getByText('Sidebar').closest('.App');
    expect(appElement).toHaveClass('bg-gray-50', 'min-h-screen');
  });
});

describe('Component Integration', () => {
  test('all layout components are rendered', () => {
    renderWithProviders(<App />);
    
    expect(screen.getByTestId('layout')).toBeInTheDocument();
    expect(screen.getByTestId('sidebar')).toBeInTheDocument();
    expect(screen.getByTestId('header')).toBeInTheDocument();
  });

  test('main content area is properly structured', () => {
    renderWithProviders(<App />);
    
    const mainElement = screen.getByTestId('dashboard').closest('main');
    expect(mainElement).toHaveClass('flex-1', 'p-6', 'overflow-auto');
  });
});

describe('Accessibility', () => {
  test('main content has proper semantic structure', () => {
    renderWithProviders(<App />);
    
    const mainElement = screen.getByTestId('dashboard').closest('main');
    expect(mainElement).toBeInTheDocument();
  });

  test('navigation elements are present', () => {
    renderWithProviders(<App />);
    
    expect(screen.getByTestId('sidebar')).toBeInTheDocument();
    expect(screen.getByTestId('header')).toBeInTheDocument();
  });
});
