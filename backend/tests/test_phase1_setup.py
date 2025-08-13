"""
Test Phase 1 setup and Open Finance Brasil standards.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, init_db
from app.core.open_finance_standards import (
    get_category_hierarchy,
    get_open_finance_compliance_info,
    PRIMARY_CATEGORIES,
    SECONDARY_CATEGORIES,
    DETAILED_CATEGORIES
)
from app.core.database_seeder import seed_database, verify_seeding


class TestPhase1Setup:
    """Test Phase 1 setup and configuration."""
    
    def test_open_finance_standards_structure(self):
        """Test Open Finance Brasil standards structure."""
        # Test primary categories
        assert len(PRIMARY_CATEGORIES) == 4
        assert "RECEITAS" in PRIMARY_CATEGORIES
        assert "DESPESAS" in PRIMARY_CATEGORIES
        assert "TRANSFERENCIAS" in PRIMARY_CATEGORIES
        assert "INVESTIMENTOS" in PRIMARY_CATEGORIES
        
        # Test secondary categories
        assert "ALIMENTACAO" in SECONDARY_CATEGORIES["DESPESAS"]
        assert "TRANSPORTE" in SECONDARY_CATEGORIES["DESPESAS"]
        assert "MORADIA" in SECONDARY_CATEGORIES["DESPESAS"]
        
        # Test detailed categories
        assert "RESTAURANTES" in DETAILED_CATEGORIES["ALIMENTACAO"]
        assert "SUPERMERCADO" in DETAILED_CATEGORIES["ALIMENTACAO"]
        assert "COMBUSTIVEL" in DETAILED_CATEGORIES["TRANSPORTE"]
        
        print("✅ Open Finance Brasil standards structure verified")
    
    def test_category_hierarchy_function(self):
        """Test category hierarchy function."""
        hierarchy = get_category_hierarchy()
        
        assert "primary" in hierarchy
        assert "secondary" in hierarchy
        assert "detailed" in hierarchy
        
        assert len(hierarchy["primary"]) == 4
        assert len(hierarchy["secondary"]["DESPESAS"]) == 9
        
        print("✅ Category hierarchy function verified")
    
    def test_compliance_info(self):
        """Test Open Finance Brasil compliance information."""
        compliance = get_open_finance_compliance_info()
        
        assert compliance["country"] == "BR"
        assert compliance["currency"] == "BRL"
        assert compliance["category_levels"] == 3
        assert compliance["compliance_status"] == "FULLY_COMPLIANT"
        
        print("✅ Compliance information verified")
    
    def test_database_models_import(self):
        """Test that database models can be imported."""
        try:
            from app.models.transaction import Transaction
            from app.models.category import Category
            from app.models.budget import Budget
            from app.models.categorization_rule import CategorizationRule
            
            assert Transaction is not None
            assert Category is not None
            assert Budget is not None
            assert CategorizationRule is not None
            
            print("✅ Database models import verified")
        except ImportError as e:
            pytest.fail(f"Failed to import database models: {e}")
    
    def test_configuration_import(self):
        """Test that configuration can be imported."""
        try:
            from app.config import settings
            
            assert settings.app_name == "CashFlow Monitor"
            assert settings.default_currency == "BRL"
            assert settings.default_country == "BR"
            
            print("✅ Configuration import verified")
        except ImportError as e:
            pytest.fail(f"Failed to import configuration: {e}")


class TestDatabaseSetup:
    """Test database setup and initialization."""
    
    @pytest.fixture(scope="class")
    def test_engine(self):
        """Create test database engine."""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(bind=engine)
        return engine
    
    @pytest.fixture(scope="class")
    def test_session(self, test_engine):
        """Create test database session."""
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
        session = SessionLocal()
        yield session
        session.close()
    
    def test_database_initialization(self, test_engine):
        """Test database initialization."""
        # This should not raise an exception
        init_db()
        print("✅ Database initialization verified")
    
    def test_database_seeding(self, test_session):
        """Test database seeding with Open Finance Brasil categories."""
        try:
            seed_database(test_session)
            print("✅ Database seeding completed")
            
            # Verify seeding
            is_valid = verify_seeding(test_session)
            assert is_valid, "Database seeding verification failed"
            print("✅ Database seeding verification passed")
            
        except Exception as e:
            pytest.fail(f"Database seeding failed: {e}")


if __name__ == "__main__":
    # Run basic tests without pytest
    print("🧪 Running Phase 1 setup tests...")
    
    # Test Open Finance Brasil standards
    test_setup = TestPhase1Setup()
    test_setup.test_open_finance_standards_structure()
    test_setup.test_category_hierarchy_function()
    test_setup.test_compliance_info()
    test_setup.test_database_models_import()
    test_setup.test_configuration_import()
    
    print("\n🎉 All Phase 1 setup tests passed!")
    print("✅ Open Finance Brasil standards implemented")
    print("✅ Database models created")
    print("✅ Configuration system working")
    print("✅ Project structure established")
