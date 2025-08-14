"""
Test Open Finance Brasil Phase 3: Account Information Integration
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import date, datetime

from app.services.ofb_account_service import OFBAccountService
from app.services.ofb_sync_service import OFBSyncService


class TestOFBAccountService:
    """Test OFB Account Service"""
    
    def test_account_service_creation(self):
        """Test account service creation"""
        db = Mock()
        account_service = OFBAccountService(db)
        
        assert account_service.db == db
        assert account_service.categorization_service is not None
        assert account_service.ofb_integration is None
    
    @pytest.mark.asyncio
    async def test_discover_accounts(self):
        """Test account discovery"""
        db = Mock()
        account_service = OFBAccountService(db)
        
        # Mock OFB integration
        account_service.ofb_integration = Mock()
        account_service.ofb_integration.validate_access = AsyncMock(return_value=True)
        
        # Test account discovery
        accounts = await account_service.discover_accounts("consent_123", "token_456")
        
        assert len(accounts) == 2
        assert accounts[0]["accountId"] == "account_001"
        assert accounts[0]["brandName"] == "Banco do Brasil"
        assert accounts[1]["type"] == "SVGS"
    
    @pytest.mark.asyncio
    async def test_get_account_balances(self):
        """Test balance retrieval"""
        db = Mock()
        account_service = OFBAccountService(db)
        
        # Mock OFB integration
        account_service.ofb_integration = Mock()
        account_service.ofb_integration.validate_access = AsyncMock(return_value=True)
        
        # Test balance retrieval
        balance = await account_service.get_account_balances("account_001", "consent_123", "token_456")
        
        assert balance["availableAmount"] == "1250.75"
        assert balance["availableAmountCurrency"] == "BRL"
        assert balance["blockedAmount"] == "0.00"
    
    @pytest.mark.asyncio
    async def test_get_account_transactions(self):
        """Test transaction retrieval"""
        db = Mock()
        account_service = OFBAccountService(db)
        
        # Mock OFB integration
        account_service.ofb_integration = Mock()
        account_service.ofb_integration.validate_access = AsyncMock(return_value=True)
        
        # Test transaction retrieval with specific date range
        from_date = date(2024, 1, 10)
        to_date = date(2024, 1, 20)
        
        transactions_data = await account_service.get_account_transactions(
            "account_001", "consent_123", "token_456",
            from_date=from_date, to_date=to_date
        )
        
        assert "transactions" in transactions_data
        assert "pagination" in transactions_data
        assert "dateRange" in transactions_data
        
        transactions = transactions_data["transactions"]
        assert len(transactions) == 3
        assert transactions[0]["transactionName"] == "RESTAURANTE ABC"
        assert transactions[1]["creditDebitType"] == "CREDITO"
    
    @pytest.mark.asyncio
    async def test_import_transactions(self):
        """Test transaction import"""
        db = Mock()
        account_service = OFBAccountService(db)
        
        # Mock database query
        db.query.return_value.filter.return_value.first.return_value = None
        db.add = Mock()
        db.commit = Mock()
        
        # Mock OFB integration
        account_service.ofb_integration = Mock()
        account_service.ofb_integration.validate_access = AsyncMock(return_value=True)
        
        # Mock categorization service
        account_service.categorization_service.suggest_category = AsyncMock(return_value=Mock(id="12345678-1234-1234-1234-123456789abc"))
        
        # Test transaction import with specific date range
        from_date = date(2024, 1, 10)
        to_date = date(2024, 1, 20)
        
        import_result = await account_service.import_transactions(
            "account_001", "consent_123", "token_456",
            from_date=from_date, to_date=to_date
        )
        
        assert import_result["status"] == "completed"
        assert import_result["imported_count"] > 0
        assert import_result["account_id"] == "account_001"
    
    def test_transaction_type_mapping(self):
        """Test transaction type mapping"""
        db = Mock()
        account_service = OFBAccountService(db)
        
        assert account_service._map_transaction_type("PURCHASE") == "DESPESA"
        assert account_service._map_transaction_type("CREDIT") == "RECEITA"
        assert account_service._map_transaction_type("TRANSFER") == "TRANSFERENCIA"
        assert account_service._map_transaction_type("INVESTMENT") == "INVESTIMENTO"
        assert account_service._map_transaction_type("UNKNOWN") == "OUTROS"
    
    def test_tag_extraction(self):
        """Test tag extraction from transactions"""
        db = Mock()
        account_service = OFBAccountService(db)
        
        transaction = {
            "type": "PURCHASE",
            "transactionCategory": "ALIMENTACAO"
        }
        
        tags = account_service._extract_tags(transaction)
        assert "PURCHASE" in tags
        assert "ALIMENTACAO" in tags
        assert len(tags) == 2


class TestOFBSyncService:
    """Test OFB Sync Service"""
    
    def test_sync_service_creation(self):
        """Test sync service creation"""
        db = Mock()
        sync_service = OFBSyncService(db)
        
        assert sync_service.db == db
        assert sync_service.account_service is not None
        assert sync_service.sync_jobs == {}
    
    @pytest.mark.asyncio
    async def test_schedule_account_sync(self):
        """Test account sync scheduling"""
        db = Mock()
        sync_service = OFBSyncService(db)
        
        # Test scheduling
        result = await sync_service.schedule_account_sync(
            "account_001", "consent_123", "token_456", "daily", "06:00"
        )
        
        assert result["status"] == "scheduled"
        assert result["account_id"] == "account_001"
        assert result["sync_frequency"] == "daily"
        assert "account_001" in sync_service.sync_jobs
    
    def test_next_sync_calculation(self):
        """Test next sync time calculation"""
        db = Mock()
        sync_service = OFBSyncService(db)
        
        # Test daily frequency
        next_sync = sync_service._calculate_next_sync("daily", "06:00")
        assert next_sync is not None
        
        # Test weekly frequency
        next_sync = sync_service._calculate_next_sync("weekly", "06:00")
        assert next_sync is not None
        
        # Test monthly frequency
        next_sync = sync_service._calculate_next_sync("monthly", "06:00")
        assert next_sync is not None
    
    @pytest.mark.asyncio
    async def test_get_sync_status(self):
        """Test sync status retrieval"""
        db = Mock()
        sync_service = OFBSyncService(db)
        
        # Add a sync job
        await sync_service.schedule_account_sync(
            "account_001", "consent_123", "token_456", "daily", "06:00"
        )
        
        # Test getting status for specific account
        status = await sync_service.get_sync_status("account_001")
        assert status["account_id"] == "account_001"
        assert "sync_status" in status
        
        # Test getting status for all accounts
        all_status = await sync_service.get_sync_status()
        assert all_status["total_jobs"] == 1
        assert all_status["enabled_jobs"] == 1
    
    @pytest.mark.asyncio
    async def test_update_sync_config(self):
        """Test sync configuration update"""
        db = Mock()
        sync_service = OFBSyncService(db)
        
        # Add a sync job
        await sync_service.schedule_account_sync(
            "account_001", "consent_123", "token_456", "daily", "06:00"
        )
        
        # Test updating frequency
        result = await sync_service.update_sync_config(
            "account_001", sync_frequency="weekly"
        )
        
        assert result["status"] == "updated"
        assert result["sync_config"]["sync_frequency"] == "weekly"
    
    @pytest.mark.asyncio
    async def test_remove_sync_job(self):
        """Test sync job removal"""
        db = Mock()
        sync_service = OFBSyncService(db)
        
        # Add a sync job
        await sync_service.schedule_account_sync(
            "account_001", "consent_123", "token_456", "daily", "06:00"
        )
        
        # Test removal
        result = await sync_service.remove_sync_job("account_001")
        
        assert result["status"] == "removed"
        assert result["account_id"] == "account_001"
        assert "account_001" not in sync_service.sync_jobs


# Integration tests
@pytest.mark.asyncio
async def test_ofb_phase3_integration():
    """Test complete Phase 3 integration"""
    
    # Test account service
    db = Mock()
    account_service = OFBAccountService(db)
    
    # Mock OFB integration
    account_service.ofb_integration = Mock()
    account_service.ofb_integration.validate_access = AsyncMock(return_value=True)
    
    # Test complete flow
    accounts = await account_service.discover_accounts("consent_123", "token_456")
    assert len(accounts) > 0
    
    account_id = accounts[0]["accountId"]
    balance = await account_service.get_account_balances(account_id, "consent_123", "token_456")
    assert balance is not None
    
    transactions = await account_service.get_account_transactions(account_id, "consent_123", "token_456")
    assert transactions is not None
    
    # Test sync service
    sync_service = OFBSyncService(db)
    await sync_service.schedule_account_sync(account_id, "consent_123", "token_456", "daily", "06:00")
    
    status = await sync_service.get_sync_status(account_id)
    assert status is not None
    
    print("✅ Phase 3 integration test completed successfully")
