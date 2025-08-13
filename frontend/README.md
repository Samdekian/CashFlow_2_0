# CashFlow 2.0 Frontend

A modern, responsive React application for personal financial management with Open Finance Brasil compliance.

## 🚀 Features

### Core Functionality
- **Dashboard**: Comprehensive financial overview with charts and insights
- **Transactions**: Full CRUD operations with advanced filtering and search
- **Categories**: Hierarchical category management (3-level Open Finance Brasil compliance)
- **Budgets**: Budget creation, tracking, and alerts
- **Analytics**: Advanced financial analysis with multiple chart types
- **Import/Export**: Support for CSV, OFX, Excel, and JSON formats
- **Settings**: User preferences and compliance management

### Technical Features
- **React 19** with TypeScript for type safety
- **Tailwind CSS** for modern, responsive design
- **React Router** for client-side routing
- **React Query** for efficient data fetching and caching
- **Chart.js** with React Chart.js 2 for data visualization
- **Heroicons** for consistent iconography
- **Responsive Design** with mobile-first approach

## 🛠️ Tech Stack

- **Frontend Framework**: React 19.1.1
- **Language**: TypeScript 4.9.5
- **Styling**: Tailwind CSS 4.1.11
- **Routing**: React Router DOM
- **State Management**: React Query (TanStack Query)
- **Charts**: Chart.js 4.5.0 + React Chart.js 2
- **Icons**: Heroicons
- **Build Tool**: Create React App 5.0.1

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CashFlow_2_0/frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm start
   ```

4. **Open your browser**
   Navigate to [http://localhost:3000](http://localhost:3000)

## 🏗️ Project Structure

```
src/
├── components/          # Reusable UI components
│   └── layout/         # Layout components (Header, Sidebar, Layout)
├── pages/              # Page components
│   ├── Dashboard.tsx   # Main dashboard with charts
│   ├── Transactions.tsx # Transaction management
│   ├── Categories.tsx  # Category hierarchy management
│   ├── Budgets.tsx     # Budget tracking and alerts
│   ├── Analytics.tsx   # Financial analysis and insights
│   ├── ImportExport.tsx # Data import/export functionality
│   └── Settings.tsx    # User preferences and settings
├── App.tsx             # Main application component
├── App.css             # Custom styles and animations
├── index.tsx           # Application entry point
└── App.test.tsx        # Component tests
```

## 🎨 Design System

### Color Palette
- **Primary**: Blue (#3B82F6) - Main actions and links
- **Success**: Green (#22C55E) - Positive actions and status
- **Warning**: Yellow (#F59E0B) - Caution and alerts
- **Danger**: Red (#EF4444) - Errors and destructive actions
- **Neutral**: Gray scale for text and backgrounds

### Typography
- **Font Family**: Inter (system fallbacks)
- **Headings**: Bold weights for hierarchy
- **Body Text**: Regular weight for readability

### Components
- **Cards**: Rounded corners with subtle shadows
- **Buttons**: Consistent sizing and hover effects
- **Forms**: Clean inputs with focus states
- **Tables**: Responsive data tables with sorting

## 📱 Responsive Design

The application is built with a mobile-first approach:

- **Mobile**: Stacked layouts, collapsible navigation
- **Tablet**: Side-by-side layouts, expanded navigation
- **Desktop**: Full sidebar, multi-column layouts

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the root directory:

```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENVIRONMENT=development
```

### Tailwind Configuration
Custom colors, spacing, and animations are defined in `tailwind.config.js`.

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
npm test

# Run tests in watch mode
npm test -- --watch

# Generate coverage report
npm test -- --coverage
```

### Test Structure
- **Unit Tests**: Individual component testing
- **Integration Tests**: Component interaction testing
- **Mock Components**: Isolated testing without external dependencies

## 🚀 Build & Deployment

### Development Build
```bash
npm run build
```

### Production Build
```bash
npm run build
npm run eject  # Only if you need custom webpack config
```

### Deployment
The build output is in the `build/` directory and can be deployed to:
- **Vercel**: Zero-config deployment
- **Netlify**: Drag and drop deployment
- **AWS S3**: Static website hosting
- **GitHub Pages**: Free hosting for open source

## 📊 Performance

### Optimization Features
- **Code Splitting**: Route-based code splitting
- **Lazy Loading**: Components loaded on demand
- **Image Optimization**: Optimized assets and icons
- **Bundle Analysis**: Webpack bundle analyzer

### Performance Metrics
- **First Contentful Paint**: < 1.5s
- **Largest Contentful Paint**: < 2.5s
- **Cumulative Layout Shift**: < 0.1
- **First Input Delay**: < 100ms

## 🔒 Security

### Security Features
- **Input Validation**: Client-side form validation
- **XSS Protection**: React's built-in XSS protection
- **HTTPS Only**: Secure communication in production
- **Content Security Policy**: CSP headers for security

## 🌐 Internationalization

### Supported Languages
- **Portuguese (Brazil)**: Primary language
- **English**: Secondary language
- **Spanish**: Future support

### Localization Features
- **Currency**: Brazilian Real (R$) support
- **Date Formats**: Brazilian date format (DD/MM/YYYY)
- **Number Formats**: Brazilian number formatting

## 📈 Open Finance Brasil Compliance

### Compliance Features
- **Category Hierarchy**: 3-level category structure
- **Data Standards**: Open Finance Brasil data models
- **Security**: Industry-standard encryption
- **Audit Trail**: Complete transaction history

### Compliance Levels
- ✅ **Level 1**: Main categories (Alimentação, Transporte, etc.)
- ✅ **Level 2**: Sub-categories (Supermercado, Restaurantes, etc.)
- ✅ **Level 3**: Specific categories (Produtos Básicos, etc.)

## 🤝 Contributing

### Development Workflow
1. Create a feature branch
2. Make your changes
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

### Code Standards
- **TypeScript**: Strict type checking enabled
- **ESLint**: Code quality and consistency
- **Prettier**: Code formatting
- **Conventional Commits**: Standardized commit messages

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

## 🆘 Support

### Getting Help
- **Documentation**: Check this README and inline code comments
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Discussions**: Join community discussions on GitHub

### Common Issues
- **Build Errors**: Clear node_modules and reinstall dependencies
- **TypeScript Errors**: Ensure all types are properly defined
- **Styling Issues**: Check Tailwind CSS classes and custom CSS

## 🔮 Roadmap

### Upcoming Features
- **Real-time Updates**: WebSocket integration for live data
- **Mobile App**: React Native companion app
- **Advanced Analytics**: Machine learning insights
- **Multi-currency**: Support for multiple currencies
- **API Integration**: Direct bank API connections

### Future Enhancements
- **Dark Mode**: Theme switching capability
- **Offline Support**: Progressive Web App features
- **Voice Commands**: Speech-to-text for transactions
- **AI Assistant**: Intelligent financial recommendations

---

**Built with ❤️ for the Brazilian financial community**
