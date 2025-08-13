# CashFlow Monitor - Personal Finance Management Application

A comprehensive personal cashflow monitoring application with **Open Finance Brasil** integration, designed for local-only operation with maximum privacy and control.

## 🚀 Features

- **Smart Transaction Categorization**: AI-powered categorization using Open Finance Brasil standards
- **Complete Financial Overview**: Dashboard with spending patterns and insights
- **Budget Management**: Create and track budgets with real-time alerts
- **Data Import/Export**: Support for CSV, OFX, and QIF file formats
- **Local-Only Operation**: No cloud dependencies, complete data privacy
- **Open Finance Brasil Compliance**: Full adherence to Brazilian financial standards

## 🏗️ Architecture

- **Backend**: Python 3.11+ with FastAPI
- **Frontend**: React 18 with TypeScript and Tailwind CSS
- **Database**: SQLite for local storage
- **AI/ML**: Scikit-learn for transaction categorization
- **Standards**: Open Finance Brasil v1.0 compliance

## 📋 Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- npm or yarn package manager

## 🛠️ Installation & Setup

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Install Poetry** (if not already installed):
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

3. **Install dependencies**:
   ```bash
   poetry install
   ```

4. **Activate virtual environment**:
   ```bash
   poetry shell
   ```

5. **Run the application**:
   ```bash
   poetry run dev
   ```

The backend will be available at `http://127.0.0.1:8000`

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start development server**:
   ```bash
   npm start
   ```

The frontend will be available at `http://localhost:3000`

## 🗂️ Project Structure

```
CashFlow_2_0/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── api/               # API endpoints
│   │   ├── core/              # Core functionality
│   │   ├── models/            # Database models
│   │   ├── schemas/           # Pydantic schemas
│   │   └── services/          # Business logic
│   ├── tests/                 # Test suite
│   └── pyproject.toml         # Poetry configuration
├── frontend/                   # React TypeScript frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── services/          # API services
│   │   ├── types/             # TypeScript types
│   │   └── utils/             # Utility functions
│   └── package.json           # npm configuration
├── docs/                       # Documentation
├── ADR_CashFlow_App.md        # Architecture Decision Record
├── PDR_CashFlow_App.md        # Product Definition Record
└── MVP_Roadmap.md             # Development roadmap
```

## 🔧 Development

### Backend Development

- **API Documentation**: Available at `/docs` when running in debug mode
- **Database Migrations**: Using Alembic for schema management
- **Testing**: pytest with coverage requirements (80%+)
- **Code Quality**: Black, Flake8, and MyPy for code standards

### Frontend Development

- **Component Library**: Reusable React components with TypeScript
- **State Management**: React Query for server state
- **Styling**: Tailwind CSS with custom design system
- **Testing**: Jest and React Testing Library

## 📊 Open Finance Brasil Compliance

This application fully complies with Open Finance Brasil standards:

- **Transaction Categories**: 3-level hierarchy (Primary → Secondary → Detailed)
- **Currency Standards**: BRL formatting and validation
- **Data Models**: Aligned with Brazilian financial specifications
- **API Design**: RESTful patterns following Open Finance Brasil guidelines

## 🧪 Testing

### Backend Tests
```bash
cd backend
poetry run pytest
poetry run pytest --cov=app --cov-report=html
```

### Frontend Tests
```bash
cd frontend
npm test
npm run build
```

## 📦 Building for Production

### Backend Build
```bash
cd backend
poetry build
poetry run pyinstaller --onefile app/main.py
```

### Frontend Build
```bash
cd frontend
npm run build
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Check the documentation in the `docs/` directory
- Review the ADR and PDR documents
- Open an issue on the repository

## 🚀 Roadmap

See `MVP_Roadmap.md` for the complete development roadmap and timeline.

---

**Built with ❤️ for the Brazilian financial community**
# CashFlow_2_0
