import React from 'react';
import { NavLink, useLocation } from 'react-router-dom';
import { 
  HomeIcon, 
  CreditCardIcon, 
  FolderIcon, 
  ChartPieIcon, 
  ArrowUpTrayIcon, 
  Cog6ToothIcon,
  BanknotesIcon
} from '@heroicons/react/24/outline';

const Sidebar: React.FC = () => {
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/', icon: HomeIcon },
    { name: 'Transactions', href: '/transactions', icon: CreditCardIcon },
    { name: 'Categories', href: '/categories', icon: FolderIcon },
    { name: 'Budgets', href: '/budgets', icon: BanknotesIcon },
    { name: 'Analytics', href: '/analytics', icon: ChartPieIcon },
    { name: 'Import/Export', href: '/import-export', icon: ArrowUpTrayIcon },
    { name: 'Settings', href: '/settings', icon: Cog6ToothIcon },
  ];

  return (
    <div className="w-64 bg-white shadow-lg border-r border-gray-200">
      <div className="flex items-center justify-center h-16 px-4 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-lg">C</span>
          </div>
          <span className="text-xl font-bold text-gray-900">CashFlow</span>
        </div>
      </div>
      
      <nav className="mt-8 px-4">
        <ul className="space-y-2">
          {navigation.map((item) => {
            const isActive = location.pathname === item.href;
            return (
              <li key={item.name}>
                <NavLink
                  to={item.href}
                  className={`flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors duration-200 ${
                    isActive
                      ? 'bg-primary-50 text-primary-700 border-r-2 border-primary-600'
                      : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                  }`}
                >
                  <item.icon className="w-5 h-5 mr-3" />
                  {item.name}
                </NavLink>
              </li>
            );
          })}
        </ul>
      </nav>

      <div className="absolute bottom-0 w-64 p-4 border-t border-gray-200">
        <div className="text-xs text-gray-500 text-center">
          <p>CashFlow 2.0</p>
          <p>Open Finance Brasil Compliant</p>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
