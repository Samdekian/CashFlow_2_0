"""
Database seeder for Open Finance Brasil categories and initial data.
"""
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import text

from ..models import Category, CategorizationRule
from ..core.open_finance_standards import (
    PRIMARY_CATEGORIES,
    SECONDARY_CATEGORIES,
    DETAILED_CATEGORIES,
    get_category_hierarchy
)


def seed_categories(db: Session) -> None:
    """Seed the database with Open Finance Brasil categories."""
    print("🌱 Seeding Open Finance Brasil categories...")
    
    # Clear existing categories
    db.execute(text("DELETE FROM categorization_rules"))
    db.execute(text("DELETE FROM categories"))
    db.commit()
    
    # Create primary categories (Level 1)
    primary_categories = {}
    for code, info in PRIMARY_CATEGORIES.items():
        category = Category(
            name=info.name,
            name_en=info.name_en,
            description=info.description,
            level=1,
            parent_id=None,
            open_finance_code=info.open_finance_code,
            color=info.color,
            icon=info.icon,
            is_system=True,
            sort_order=len(primary_categories)
        )
        db.add(category)
        db.flush()  # Get the ID
        primary_categories[code] = category
    
    # Create secondary categories (Level 2)
    secondary_categories = {}
    for primary_code, secondary_dict in SECONDARY_CATEGORIES.items():
        if primary_code in primary_categories:
            parent = primary_categories[primary_code]
            for code, info in secondary_dict.items():
                category = Category(
                    name=info.name,
                    name_en=info.name_en,
                    description=info.description,
                    level=2,
                    parent_id=parent.id,
                    open_finance_code=info.open_finance_code,
                    color=info.color,
                    icon=info.icon,
                    is_system=True,
                    sort_order=len(secondary_categories)
                )
                db.add(category)
                db.flush()
                secondary_categories[code] = category
    
    # Create detailed categories (Level 3)
    for secondary_code, detailed_dict in DETAILED_CATEGORIES.items():
        if secondary_code in secondary_categories:
            parent = secondary_categories[secondary_code]
            for code, info in detailed_dict.items():
                category = Category(
                    name=info.name,
                    name_en=info.name_en,
                    description=info.description,
                    level=3,
                    parent_id=parent.id,
                    open_finance_code=info.open_finance_code,
                    color=info.color,
                    icon=info.icon,
                    is_system=True,
                    sort_order=0
                )
                db.add(category)
    
    # Commit all categories
    db.commit()
    print(f"✅ Created {len(primary_categories)} primary categories")
    print(f"✅ Created {len(secondary_categories)} secondary categories")
    print(f"✅ Created {sum(len(cats) for cats in DETAILED_CATEGORIES.values())} detailed categories")


def seed_categorization_rules(db: Session) -> None:
    """Seed the database with basic categorization rules."""
    print("🔧 Seeding categorization rules...")
    
    # Get categories for rule creation
    categories = db.query(Category).all()
    category_map = {cat.name: cat for cat in categories}
    
    # Basic categorization rules
    rules = [
        # Food & Dining
        {
            "name": "Restaurant Keywords",
            "description": "Auto-categorize restaurant transactions",
            "category": "Alimentação",
            "rule_type": "KEYWORD",
            "rule_value": "restaurante,restaurant,lanchonete,padaria,pizzaria",
            "confidence_score": 0.85
        },
        {
            "name": "Supermarket Keywords",
            "description": "Auto-categorize supermarket transactions",
            "category": "Supermercado",
            "rule_type": "KEYWORD",
            "rule_value": "supermercado,supermarket,hipermercado,atacado",
            "confidence_score": 0.90
        },
        {
            "name": "Food Delivery",
            "description": "Auto-categorize food delivery transactions",
            "category": "Delivery",
            "rule_type": "KEYWORD",
            "rule_value": "ifood,rappi,uber eats,delivery,entrega",
            "confidence_score": 0.88
        },
        
        # Transportation
        {
            "name": "Fuel Keywords",
            "description": "Auto-categorize fuel transactions",
            "category": "Combustível",
            "rule_type": "KEYWORD",
            "rule_value": "posto,gasolina,combustivel,petrobras,shell",
            "confidence_score": 0.92
        },
        {
            "name": "Ride Sharing",
            "description": "Auto-categorize ride sharing transactions",
            "category": "Uber/99",
            "rule_type": "KEYWORD",
            "rule_value": "uber,99,99pop,ride sharing",
            "confidence_score": 0.95
        },
        {
            "name": "Public Transport",
            "description": "Auto-categorize public transport transactions",
            "category": "Ônibus/Metrô",
            "rule_type": "KEYWORD",
            "rule_value": "metro,onibus,bus,transporte publico",
            "confidence_score": 0.87
        },
        
        # Housing
        {
            "name": "Rent Keywords",
            "description": "Auto-categorize rent transactions",
            "category": "Aluguel",
            "rule_type": "KEYWORD",
            "rule_value": "aluguel,rent,imobiliaria,imovel",
            "confidence_score": 0.90
        },
        {
            "name": "Condominium",
            "description": "Auto-categorize condominium transactions",
            "category": "Condomínio",
            "rule_type": "KEYWORD",
            "rule_value": "condominio,condo,administracao",
            "confidence_score": 0.88
        },
        {
            "name": "Electricity",
            "description": "Auto-categorize electricity transactions",
            "category": "Energia",
            "rule_type": "KEYWORD",
            "rule_value": "energia,eletrica,light,enel,energisa",
            "confidence_score": 0.93
        },
        {
            "name": "Water",
            "description": "Auto-categorize water transactions",
            "category": "Água",
            "rule_type": "KEYWORD",
            "rule_value": "agua,water,sabesp,caesb",
            "confidence_score": 0.91
        },
        
        # Income
        {
            "name": "Salary Keywords",
            "description": "Auto-categorize salary transactions",
            "category": "Salário",
            "rule_type": "KEYWORD",
            "rule_value": "salario,salary,remuneracao,ordenado",
            "confidence_score": 0.95
        },
        {
            "name": "Freelance Keywords",
            "description": "Auto-categorize freelance transactions",
            "category": "Freelance",
            "rule_type": "KEYWORD",
            "rule_value": "freelance,consultoria,projeto,servico",
            "confidence_score": 0.85
        }
    ]
    
    # Create rules
    for rule_data in rules:
        category_name = rule_data["category"]
        if category_name in category_map:
            rule = CategorizationRule(
                name=rule_data["name"],
                description=rule_data["description"],
                category_id=category_map[category_name].id,
                rule_type=rule_data["rule_type"],
                rule_value=rule_data["rule_value"],
                confidence_score=rule_data["confidence_score"],
                is_system=True,
                priority=0
            )
            db.add(rule)
    
    db.commit()
    print(f"✅ Created {len(rules)} categorization rules")


def seed_database(db: Session) -> None:
    """Seed the entire database with initial data."""
    print("🚀 Starting database seeding...")
    
    try:
        # Seed categories first
        seed_categories(db)
        
        # Seed categorization rules
        seed_categorization_rules(db)
        
        print("🎉 Database seeding completed successfully!")
        
    except Exception as e:
        print(f"❌ Database seeding failed: {e}")
        db.rollback()
        raise


def verify_seeding(db: Session) -> bool:
    """Verify that the database was seeded correctly."""
    try:
        # Check category counts
        primary_count = db.query(Category).filter(Category.level == 1).count()
        secondary_count = db.query(Category).filter(Category.level == 2).count()
        detailed_count = db.query(Category).filter(Category.level == 3).count()
        rules_count = db.query(CategorizationRule).count()
        
        print(f"📊 Database verification:")
        print(f"   Primary categories: {primary_count}")
        print(f"   Secondary categories: {secondary_count}")
        print(f"   Detailed categories: {detailed_count}")
        print(f"   Categorization rules: {rules_count}")
        
        # Expected counts based on our standards
        expected_primary = len(PRIMARY_CATEGORIES)
        expected_secondary = sum(len(cats) for cats in SECONDARY_CATEGORIES.values())
        expected_detailed = sum(len(cats) for cats in DETAILED_CATEGORIES.values())
        
        if (primary_count == expected_primary and 
            secondary_count == expected_secondary and 
            detailed_count == expected_detailed and
            rules_count > 0):
            print("✅ Database seeding verification passed!")
            return True
        else:
            print("❌ Database seeding verification failed!")
            return False
            
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False
