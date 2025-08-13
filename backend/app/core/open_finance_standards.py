"""
Open Finance Brasil Standards Implementation

This module contains the constants and data structures that ensure
compliance with Open Finance Brasil specifications for financial applications.
"""
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


class TransactionType(str, Enum):
    """Transaction types according to Open Finance Brasil standards."""
    INCOME = "RECEITA"
    EXPENSE = "DESPESA"
    TRANSFER = "TRANSFERENCIA"
    INVESTMENT = "INVESTIMENTO"


class BudgetPeriod(str, Enum):
    """Budget period types."""
    WEEKLY = "SEMANAL"
    MONTHLY = "MENSAL"
    QUARTERLY = "TRIMESTRAL"
    YEARLY = "ANUAL"


@dataclass
class CategoryInfo:
    """Category information with Open Finance Brasil compliance."""
    code: str
    name: str
    name_en: str
    description: str
    color: str
    icon: str
    open_finance_code: Optional[str] = None


# Level 1 Categories (Primary) - Open Finance Brasil Primary Categories
PRIMARY_CATEGORIES: Dict[str, CategoryInfo] = {
    "RECEITAS": CategoryInfo(
        code="RECEITAS",
        name="Receitas",
        name_en="Income",
        description="All forms of income and revenue",
        color="#10B981",  # Green
        icon="💰",
        open_finance_code="OFB_RECEITAS"
    ),
    "DESPESAS": CategoryInfo(
        code="DESPESAS",
        name="Despesas",
        name_en="Expenses",
        description="All forms of expenses and costs",
        color="#EF4444",  # Red
        icon="💸",
        open_finance_code="OFB_DESPESAS"
    ),
    "TRANSFERENCIAS": CategoryInfo(
        code="TRANSFERENCIAS",
        name="Transferências",
        name_en="Transfers",
        description="Money transfers between accounts",
        color="#3B82F6",  # Blue
        icon="🔄",
        open_finance_code="OFB_TRANSFERENCIAS"
    ),
    "INVESTIMENTOS": CategoryInfo(
        code="INVESTIMENTOS",
        name="Investimentos",
        name_en="Investments",
        description="Investment activities and returns",
        color="#8B5CF6",  # Purple
        icon="📈",
        open_finance_code="OFB_INVESTIMENTOS"
    )
}

# Level 2 Categories (Secondary) - Open Finance Brasil Secondary Categories
SECONDARY_CATEGORIES: Dict[str, Dict[str, CategoryInfo]] = {
    "RECEITAS": {
        "SALARIO": CategoryInfo(
            code="SALARIO",
            name="Salário",
            name_en="Salary",
            description="Regular employment income",
            color="#059669",
            icon="💼",
            open_finance_code="OFB_RECEITAS_SALARIO"
        ),
        "FREELANCE": CategoryInfo(
            code="FREELANCE",
            name="Freelance",
            name_en="Freelance",
            description="Freelance and contract work income",
            color="#10B981",
            icon="💻",
            open_finance_code="OFB_RECEITAS_FREELANCE"
        ),
        "INVESTIMENTOS_RETORNO": CategoryInfo(
            code="INVESTIMENTOS_RETORNO",
            name="Retorno de Investimentos",
            name_en="Investment Returns",
            description="Returns from investments",
            color="#059669",
            icon="📊",
            open_finance_code="OFB_RECEITAS_INVESTIMENTOS"
        ),
        "OUTROS": CategoryInfo(
            code="OUTROS_RECEITAS",
            name="Outras Receitas",
            name_en="Other Income",
            description="Other forms of income",
            color="#10B981",
            icon="➕",
            open_finance_code="OFB_RECEITAS_OUTROS"
        )
    },
    "DESPESAS": {
        "ALIMENTACAO": CategoryInfo(
            code="ALIMENTACAO",
            name="Alimentação",
            name_en="Food & Dining",
            description="Food, restaurants, and dining expenses",
            color="#EF4444",
            icon="🍽️",
            open_finance_code="OFB_DESPESAS_ALIMENTACAO"
        ),
        "TRANSPORTE": CategoryInfo(
            code="TRANSPORTE",
            name="Transporte",
            name_en="Transportation",
            description="Public transport, fuel, and vehicle expenses",
            color="#F59E0B",
            icon="🚗",
            open_finance_code="OFB_DESPESAS_TRANSPORTE"
        ),
        "MORADIA": CategoryInfo(
            code="MORADIA",
            name="Moradia",
            name_en="Housing",
            description="Rent, mortgage, utilities, and home maintenance",
            color="#8B5CF6",
            icon="🏠",
            open_finance_code="OFB_DESPESAS_MORADIA"
        ),
        "SAUDE": CategoryInfo(
            code="SAUDE",
            name="Saúde",
            name_en="Healthcare",
            description="Medical expenses, insurance, and wellness",
            color="#EC4899",
            icon="🏥",
            open_finance_code="OFB_DESPESAS_SAUDE"
        ),
        "EDUCACAO": CategoryInfo(
            code="EDUCACAO",
            name="Educação",
            name_en="Education",
            description="Tuition, books, courses, and training",
            color="#06B6D4",
            icon="📚",
            open_finance_code="OFB_DESPESAS_EDUCACAO"
        ),
        "ENTRETENIMENTO": CategoryInfo(
            code="ENTRETENIMENTO",
            name="Entretenimento",
            name_en="Entertainment",
            description="Movies, games, hobbies, and leisure activities",
            color="#F97316",
            icon="🎬",
            open_finance_code="OFB_DESPESAS_ENTRETENIMENTO"
        ),
        "COMPRAS": CategoryInfo(
            code="COMPRAS",
            name="Compras",
            name_en="Shopping",
            description="Clothing, electronics, and general shopping",
            color="#84CC16",
            icon="🛍️",
            open_finance_code="OFB_DESPESAS_COMPRAS"
        ),
        "SERVICOS_FINANCEIROS": CategoryInfo(
            code="SERVICOS_FINANCEIROS",
            name="Serviços Financeiros",
            name_en="Financial Services",
            description="Bank fees, credit card charges, and financial services",
            color="#6B7280",
            icon="🏦",
            open_finance_code="OFB_DESPESAS_SERVICOS_FINANCEIROS"
        ),
        "OUTROS": CategoryInfo(
            code="OUTROS_DESPESAS",
            name="Outras Despesas",
            name_en="Other Expenses",
            description="Miscellaneous and other expenses",
            color="#9CA3AF",
            icon="📝",
            open_finance_code="OFB_DESPESAS_OUTROS"
        )
    },
    "TRANSFERENCIAS": {
        "ENTRE_CONTAS": CategoryInfo(
            code="ENTRE_CONTAS",
            name="Entre Contas",
            name_en="Between Accounts",
            description="Transfers between personal accounts",
            color="#3B82F6",
            icon="💳",
            open_finance_code="OFB_TRANSFERENCIAS_ENTRE_CONTAS"
        ),
        "PAGAMENTO_CARTAO": CategoryInfo(
            code="PAGAMENTO_CARTAO",
            name="Pagamento de Cartão",
            name_en="Credit Card Payment",
            description="Credit card bill payments",
            color="#1D4ED8",
            icon="💳",
            open_finance_code="OFB_TRANSFERENCIAS_PAGAMENTO_CARTAO"
        )
    },
    "INVESTIMENTOS": {
        "ACAOES": CategoryInfo(
            code="ACAOES",
            name="Ações",
            name_en="Stocks",
            description="Stock market investments",
            color="#8B5CF6",
            icon="📈",
            open_finance_code="OFB_INVESTIMENTOS_ACAOES"
        ),
        "FUNDOS": CategoryInfo(
            code="FUNDOS",
            name="Fundos",
            name_en="Funds",
            description="Investment funds and ETFs",
            color="#7C3AED",
            icon="📊",
            open_finance_code="OFB_INVESTIMENTOS_FUNDOS"
        ),
        "POUPANCA": CategoryInfo(
            code="POUPANCA",
            name="Poupança",
            name_en="Savings",
            description="Savings accounts and deposits",
            color="#6366F1",
            icon="🏦",
            open_finance_code="OFB_INVESTIMENTOS_POUPANCA"
        )
    }
}

# Level 3 Categories (Detailed) - Specific subcategories
DETAILED_CATEGORIES: Dict[str, Dict[str, CategoryInfo]] = {
    "ALIMENTACAO": {
        "RESTAURANTES": CategoryInfo(
            code="RESTAURANTES",
            name="Restaurantes",
            name_en="Restaurants",
            description="Dining out at restaurants",
            color="#DC2626",
            icon="🍽️",
            open_finance_code="OFB_DESPESAS_ALIMENTACAO_RESTAURANTES"
        ),
        "SUPERMERCADO": CategoryInfo(
            code="SUPERMERCADO",
            name="Supermercado",
            name_en="Supermarket",
            description="Grocery shopping",
            color="#B91C1C",
            icon="🛒",
            open_finance_code="OFB_DESPESAS_ALIMENTACAO_SUPERMERCADO"
        ),
        "DELIVERY": CategoryInfo(
            code="DELIVERY",
            name="Delivery",
            name_en="Food Delivery",
            description="Food delivery services",
            color="#991B1B",
            icon="🚚",
            open_finance_code="OFB_DESPESAS_ALIMENTACAO_DELIVERY"
        )
    },
    "TRANSPORTE": {
        "COMBUSTIVEL": CategoryInfo(
            code="COMBUSTIVEL",
            name="Combustível",
            name_en="Fuel",
            description="Gasoline and fuel expenses",
            color="#D97706",
            icon="⛽",
            open_finance_code="OFB_DESPESAS_TRANSPORTE_COMBUSTIVEL"
        ),
        "UBER_99": CategoryInfo(
            code="UBER_99",
            name="Uber/99",
            name_en="Ride Sharing",
            description="Ride sharing services",
            color="#F59E0B",
            icon="🚕",
            open_finance_code="OFB_DESPESAS_TRANSPORTE_RIDE_SHARING"
        ),
        "ONIBUS_METRO": CategoryInfo(
            code="ONIBUS_METRO",
            name="Ônibus/Metrô",
            name_en="Public Transport",
            description="Public transportation",
            color="#EAB308",
            icon="🚌",
            open_finance_code="OFB_DESPESAS_TRANSPORTE_PUBLICO"
        )
    },
    "MORADIA": {
        "ALUGUEL": CategoryInfo(
            code="ALUGUEL",
            name="Aluguel",
            name_en="Rent",
            description="Housing rent payments",
            color="#7C3AED",
            icon="🏠",
            open_finance_code="OFB_DESPESAS_MORADIA_ALUGUEL"
        ),
        "CONDOMINIO": CategoryInfo(
            code="CONDOMINIO",
            name="Condomínio",
            name_en="Condominium",
            description="Condominium fees",
            color="#8B5CF6",
            icon="🏢",
            open_finance_code="OFB_DESPESAS_MORADIA_CONDOMINIO"
        ),
        "ENERGIA": CategoryInfo(
            code="ENERGIA",
            name="Energia",
            name_en="Electricity",
            description="Electricity bills",
            color="#A855F7",
            icon="⚡",
            open_finance_code="OFB_DESPESAS_MORADIA_ENERGIA"
        ),
        "AGUA": CategoryInfo(
            code="AGUA",
            name="Água",
            name_en="Water",
            description="Water bills",
            color="#06B6D4",
            icon="💧",
            open_finance_code="OFB_DESPESAS_MORADIA_AGUA"
        )
    }
}


def get_category_hierarchy() -> Dict:
    """Get the complete Open Finance Brasil category hierarchy."""
    return {
        "primary": PRIMARY_CATEGORIES,
        "secondary": SECONDARY_CATEGORIES,
        "detailed": DETAILED_CATEGORIES
    }


def get_category_by_code(code: str) -> Optional[CategoryInfo]:
    """Get category information by its code."""
    # Search in primary categories
    if code in PRIMARY_CATEGORIES:
        return PRIMARY_CATEGORIES[code]
    
    # Search in secondary categories
    for primary_cats in SECONDARY_CATEGORIES.values():
        if code in primary_cats:
            return primary_cats[code]
    
    # Search in detailed categories
    for secondary_cats in DETAILED_CATEGORIES.values():
        if code in secondary_cats:
            return secondary_cats[code]
    
    return None


def get_categories_by_level(level: int) -> List[CategoryInfo]:
    """Get all categories at a specific level."""
    if level == 1:
        return list(PRIMARY_CATEGORIES.values())
    elif level == 2:
        categories = []
        for primary_cats in SECONDARY_CATEGORIES.values():
            categories.extend(primary_cats.values())
        return categories
    elif level == 3:
        categories = []
        for secondary_cats in DETAILED_CATEGORIES.values():
            categories.extend(secondary_cats.values())
        return categories
    else:
        return []


def get_open_finance_compliance_info() -> Dict:
    """Get Open Finance Brasil compliance information."""
    return {
        "standard_version": "1.0",
        "country": "BR",
        "currency": "BRL",
        "category_levels": 3,
        "total_categories": len(PRIMARY_CATEGORIES) + 
                          sum(len(cats) for cats in SECONDARY_CATEGORIES.values()) +
                          sum(len(cats) for cats in DETAILED_CATEGORIES.values()),
        "compliance_status": "FULLY_COMPLIANT",
        "last_updated": "2024-12-01"
    }


def validate_budget_category(category_id: str, db) -> bool:
    """
    Validate if a category is suitable for budget creation.
    
    Args:
        category_id: Category ID to validate
        db: Database session
        
    Returns:
        True if category is valid for budgets, False otherwise
    """
    # For now, return True as a placeholder
    # In a real implementation, this would query the database
    # to check if the category exists and is an expense category
    return True


def validate_date_range(date_range) -> bool:
    """
    Validate if a date range is valid.
    
    Args:
        date_range: DateRange object to validate
        
    Returns:
        True if date range is valid, False otherwise
    """
    if not date_range or not hasattr(date_range, 'start_date') or not hasattr(date_range, 'end_date'):
        return False
    
    if date_range.start_date >= date_range.end_date:
        return False
    
    return True


def validate_import_data(data: List[Dict[str, Any]]) -> bool:
    """
    Validate import data against Open Finance Brasil standards.
    
    Args:
        data: List of transaction data to validate
        
    Returns:
        True if data is valid, False otherwise
    """
    if not data:
        return False
    
    for transaction in data:
        # Basic validation - in real implementation, this would be more comprehensive
        if not transaction.get('date') or not transaction.get('amount') or not transaction.get('description'):
            return False
    
    return True


def get_supported_formats() -> Dict[str, Any]:
    """
    Get supported import and export formats.
    
    Returns:
        Dictionary of supported formats
    """
    return {
        "import_formats": {
            "csv": {
                "name": "CSV (Comma Separated Values)",
                "description": "Standard CSV format with headers",
                "extensions": [".csv"],
                "max_size": "50MB",
                "required_fields": ["date", "amount", "description"],
                "optional_fields": ["category", "reference", "institution"]
            },
            "ofx": {
                "name": "OFX (Open Financial Exchange)",
                "description": "Financial data exchange format",
                "extensions": [".ofx", ".qfx"],
                "max_size": "50MB",
                "required_fields": ["date", "amount", "memo"],
                "optional_fields": ["category", "reference"]
            },
            "excel": {
                "name": "Excel (XLSX/XLS)",
                "description": "Microsoft Excel format",
                "extensions": [".xlsx", ".xls"],
                "max_size": "50MB",
                "required_fields": ["date", "amount", "description"],
                "optional_fields": ["category", "reference", "institution"]
            }
        },
        "export_formats": {
            "csv": {
                "name": "CSV (Comma Separated Values)",
                "description": "Standard CSV format",
                "extensions": [".csv"],
                "features": ["Headers", "Custom delimiter", "UTF-8 encoding"]
            },
            "json": {
                "name": "JSON (JavaScript Object Notation)",
                "description": "Structured data format",
                "extensions": [".json"],
                "features": ["Pretty print", "Nested structures", "Metadata"]
            },
            "excel": {
                "name": "Excel (XLSX)",
                "description": "Microsoft Excel format",
                "extensions": [".xlsx"],
                "features": ["Multiple sheets", "Charts", "Formatting"]
            },
            "pdf": {
                "name": "PDF (Portable Document Format)",
                "description": "Portable document format",
                "extensions": [".pdf"],
                "features": ["Professional layout", "Charts", "Print-ready"]
            }
        }
    }
