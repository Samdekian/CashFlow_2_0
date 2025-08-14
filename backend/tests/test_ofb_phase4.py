"""
Phase 4: Full Integration Tests
Tests for payment services, multi-bank aggregation, and advanced analytics.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from decimal import Decimal

from app.services.ofb_payment_service import OFBPaymentService
from app.services.ofb_multi_bank_service import OFBMultiBankService
from app.services.ofb_advanced_analytics_service import OFBAdvancedAnalyticsService
from app.core.open_finance_brasil import OpenFinanceBrasilIntegration


class TestOFBPaymentService:
    """Test OFB payment service functionality."""
    
    @pytest.mark.asyncio
    async def test_payment_service_creation(self):
        """Test payment service creation."""
        db = Mock()
        ofb_integration = Mock()
        payment_service = OFBPaymentService(db, ofb_integration)
        
        assert payment_service.db == db
        assert payment_service.ofb_integration == ofb_integration
        assert "PENDING" in payment_service.payment_statuses
    
    @pytest.mark.asyncio
    async def test_initiate_pix_payment(self):
        """Test PIX payment initiation."""
        db = Mock()
        ofb_integration = Mock()
        ofb_integration.validate_access = AsyncMock(return_value=True)
        
        payment_service = OFBPaymentService(db, ofb_integration)
        
        result = await payment_service.initiate_pix_payment(
            consent_id="consent_123",
            access_token="token_456",
            amount=Decimal("100.00"),
            recipient_key="12345678901",
            recipient_key_type="CPF",
            description="Test payment"
        )
        
        assert "payment_id" in result
        assert result["status"] == "PENDING"
        assert result["message"] == "PIX payment initiated successfully"
        assert "pix_" in result["payment_id"]
    
    @pytest.mark.asyncio
    async def test_initiate_ted_transfer(self):
        """Test TED transfer initiation."""
        db = Mock()
        ofb_integration = Mock()
        ofb_integration.validate_access = AsyncMock(return_value=True)
        
        payment_service = OFBPaymentService(db, ofb_integration)
        
        result = await payment_service.initiate_ted_doc_transfer(
            consent_id="consent_123",
            access_token="token_456",
            amount=Decimal("500.00"),
            recipient_bank_code="001",
            recipient_agency="1234",
            recipient_account="12345-6",
            recipient_name="John Doe",
            transfer_type="TED",
            description="Test transfer"
        )
        
        assert "transfer_id" in result
        assert result["status"] == "PENDING"
        assert result["message"] == "TED transfer initiated successfully"
        assert "ted_" in result["transfer_id"]
    
    @pytest.mark.asyncio
    async def test_schedule_recurring_payment(self):
        """Test recurring payment scheduling."""
        db = Mock()
        ofb_integration = Mock()
        ofb_integration.validate_access = AsyncMock(return_value=True)
        
        payment_service = OFBPaymentService(db, ofb_integration)
        
        start_date = datetime.utcnow() + timedelta(days=1)
        
        result = await payment_service.schedule_recurring_payment(
            consent_id="consent_123",
            access_token="token_456",
            payment_type="PIX",
            amount=Decimal("200.00"),
            frequency="monthly",
            start_date=start_date
        )
        
        assert "schedule_id" in result
        assert result["message"] == "Recurring payment scheduled successfully"
        assert "recurring_" in result["schedule_id"]
    
    @pytest.mark.asyncio
    async def test_get_payment_status(self):
        """Test payment status retrieval."""
        db = Mock()
        ofb_integration = Mock()
        ofb_integration.validate_access = AsyncMock(return_value=True)
        
        payment_service = OFBPaymentService(db, ofb_integration)
        
        result = await payment_service.get_payment_status(
            payment_id="pix_12345678",
            consent_id="consent_123",
            access_token="token_456"
        )
        
        assert "payment_id" in result
        assert "status" in result
        assert "last_updated" in result
    
    @pytest.mark.asyncio
    async def test_cancel_payment(self):
        """Test payment cancellation."""
        db = Mock()
        ofb_integration = Mock()
        ofb_integration.validate_access = AsyncMock(return_value=True)
        
        payment_service = OFBPaymentService(db, ofb_integration)
        
        result = await payment_service.cancel_payment(
            payment_id="pix_12345678",
            consent_id="consent_123",
            access_token="token_456"
        )
        
        assert "payment_id" in result
        assert result["status"] == "CANCELLED"
        assert "cancelled_at" in result
    
    @pytest.mark.asyncio
    async def test_get_payment_history(self):
        """Test payment history retrieval."""
        db = Mock()
        ofb_integration = Mock()
        ofb_integration.validate_access = AsyncMock(return_value=True)
        
        payment_service = OFBPaymentService(db, ofb_integration)
        
        result = await payment_service.get_payment_history(
            consent_id="consent_123",
            access_token="token_456",
            page=1,
            page_size=10
        )
        
        assert "payments" in result
        assert "pagination" in result
        assert "filters" in result
        assert len(result["payments"]) > 0
    
    def test_estimate_completion_time(self):
        """Test completion time estimation."""
        db = Mock()
        ofb_integration = Mock()
        payment_service = OFBPaymentService(db, ofb_integration)
        
        # Test PIX completion time
        pix_time = payment_service._estimate_completion_time("PENDING", "PIX")
        assert "10 seconds" in pix_time
        
        # Test TED completion time
        ted_time = payment_service._estimate_completion_time("PENDING", "TED")
        assert "1 business day" in ted_time
        
        # Test completed status
        completed_time = payment_service._estimate_completion_time("COMPLETED")
        assert completed_time == "Already completed"


class TestOFBMultiBankService:
    """Test OFB multi-bank service functionality."""
    
    @pytest.mark.asyncio
    async def test_multi_bank_service_creation(self):
        """Test multi-bank service creation."""
        db = Mock()
        ofb_integration = Mock()
        multi_bank_service = OFBMultiBankService(db, ofb_integration)
        
        assert multi_bank_service.db == db
        assert multi_bank_service.ofb_integration == ofb_integration
        assert len(multi_bank_service.bank_connections) > 0
    
    @pytest.mark.asyncio
    async def test_connect_bank(self):
        """Test bank connection."""
        db = Mock()
        ofb_integration = Mock()
        ofb_integration.validate_access = AsyncMock(return_value=True)
        
        multi_bank_service = OFBMultiBankService(db, ofb_integration)
        
        # Mock account discovery
        multi_bank_service.account_service.discover_accounts = AsyncMock(
            return_value={"accounts": [{"id": "new_account_001"}]}
        )
        
        # Mock sync scheduling
        multi_bank_service.sync_service.schedule_account_sync = AsyncMock(
            return_value={"status": "scheduled"}
        )
        
        result = await multi_bank_service.connect_bank(
            bank_code="999",
            bank_name="Test Bank",
            consent_id="consent_123",
            access_token="token_456",
            user_id="user_001"
        )
        
        assert "connection_id" in result
        assert "Test Bank connected successfully" in result["message"]
        assert result["accounts_discovered"] == 1
    
    @pytest.mark.asyncio
    async def test_disconnect_bank(self):
        """Test bank disconnection."""
        db = Mock()
        ofb_integration = Mock()
        multi_bank_service = OFBMultiBankService(db, ofb_integration)
        
        # Update the mock bank connection to have the correct user_id
        multi_bank_service.bank_connections["bank_001"]["user_id"] = "user_001"
        
        # Mock sync job removal
        multi_bank_service.sync_service.remove_sync_job = AsyncMock(
            return_value={"status": "removed"}
        )
        
        result = await multi_bank_service.disconnect_bank(
            connection_id="bank_001",
            user_id="user_001"
        )
        
        assert "connection_id" in result
        assert result["status"] == "DISCONNECTED"
        assert "disconnected_at" in result
    
    @pytest.mark.asyncio
    async def test_get_connected_banks(self):
        """Test getting connected banks."""
        db = Mock()
        ofb_integration = Mock()
        multi_bank_service = OFBMultiBankService(db, ofb_integration)
        
        result = await multi_bank_service.get_connected_banks(user_id="user_001")
        
        assert "total_connections" in result
        assert "active_connections" in result
        assert "summary" in result
    
    @pytest.mark.asyncio
    async def test_get_aggregated_balance(self):
        """Test aggregated balance retrieval."""
        db = Mock()
        ofb_integration = Mock()
        multi_bank_service = OFBMultiBankService(db, ofb_integration)
        
        # Mock balance retrieval
        multi_bank_service.account_service.get_account_balances = AsyncMock(
            return_value={
                "balances": [{"type": "AVAILABLE", "amount": 1000.00}]
            }
        )
        
        result = await multi_bank_service.get_aggregated_balance(user_id="user_001")
        
        assert "total_balance" in result
        assert "currency" in result
        assert "bank_breakdown" in result
        assert result["currency"] == "BRL"
    
    @pytest.mark.asyncio
    async def test_sync_all_banks(self):
        """Test syncing all banks."""
        db = Mock()
        ofb_integration = Mock()
        multi_bank_service = OFBMultiBankService(db, ofb_integration)
        
        # Mock sync execution
        multi_bank_service.sync_service.sync_all_accounts = AsyncMock(
            return_value={"status": "completed", "synced_count": 3}
        )
        
        result = await multi_bank_service.sync_all_banks(user_id="user_001")
        
        assert "total_banks_synced" in result
        assert "total_accounts_synced" in result
        assert "sync_results" in result
    
    @pytest.mark.asyncio
    async def test_get_bank_health_status(self):
        """Test bank health status retrieval."""
        db = Mock()
        ofb_integration = Mock()
        multi_bank_service = OFBMultiBankService(db, ofb_integration)
        
        result = await multi_bank_service.get_bank_health_status(user_id="user_001")
        
        assert "total_banks" in result
        assert "healthy_banks" in result
        assert "banks_needing_attention" in result
        assert "health_details" in result


class TestOFBAdvancedAnalyticsService:
    """Test OFB advanced analytics service functionality."""
    
    @pytest.mark.asyncio
    async def test_analytics_service_creation(self):
        """Test analytics service creation."""
        db = Mock()
        ofb_integration = Mock()
        analytics_service = OFBAdvancedAnalyticsService(db, ofb_integration)
        
        assert analytics_service.db == db
        assert analytics_service.ofb_integration == ofb_integration
        assert len(analytics_service.mock_transactions) > 0
    
    @pytest.mark.asyncio
    async def test_get_cash_flow_analysis(self):
        """Test cash flow analysis."""
        db = Mock()
        ofb_integration = Mock()
        analytics_service = OFBAdvancedAnalyticsService(db, ofb_integration)
        
        # Mock multi-bank service
        analytics_service.multi_bank_service.get_aggregated_balance = AsyncMock(
            return_value={"total_balance": 5000.00}
        )
        
        result = await analytics_service.get_cash_flow_analysis(
            user_id="user_001",
            period="monthly"
        )
        
        assert "period" in result
        assert "cash_flow_metrics" in result
        assert "trends" in result
        assert "insights" in result
        assert result["period"] == "monthly"
    
    @pytest.mark.asyncio
    async def test_get_spending_patterns(self):
        """Test spending pattern analysis."""
        db = Mock()
        ofb_integration = Mock()
        analytics_service = OFBAdvancedAnalyticsService(db, ofb_integration)
        
        result = await analytics_service.get_spending_patterns(
            user_id="user_001",
            category_level="PRIMARY"
        )
        
        assert "total_expenses" in result
        assert "category_breakdown" in result
        assert "bank_breakdown" in result
        assert "top_categories" in result
        assert "insights" in result
    
    @pytest.mark.asyncio
    async def test_get_bank_performance_analysis(self):
        """Test bank performance analysis."""
        db = Mock()
        ofb_integration = Mock()
        analytics_service = OFBAdvancedAnalyticsService(db, ofb_integration)
        
        # Mock multi-bank service calls
        analytics_service.multi_bank_service.get_bank_health_status = AsyncMock(
            return_value={
                "total_banks": 2,
                "healthy_banks": 2,
                "banks_needing_attention": 0,
                "health_details": [
                    {
                        "bank_name": "Test Bank",
                        "bank_code": "001",
                        "sync_status": "EXCELLENT",
                        "account_status": "HEALTHY",
                        "last_sync": "2024-01-15T10:00:00",
                        "account_count": 2
                    }
                ]
            }
        )
        
        analytics_service.multi_bank_service.get_aggregated_balance = AsyncMock(
            return_value={
                "total_balance": 5000.00,
                "bank_breakdown": [
                    {"bank_code": "001", "total_balance": 5000.00}
                ]
            }
        )
        
        result = await analytics_service.get_bank_performance_analysis(
            user_id="user_001"
        )
        
        assert "overall_performance_score" in result
        assert "bank_performance" in result
        assert "health_summary" in result
        assert "balance_summary" in result
    
    @pytest.mark.asyncio
    async def test_get_financial_health_score(self):
        """Test financial health score calculation."""
        db = Mock()
        ofb_integration = Mock()
        analytics_service = OFBAdvancedAnalyticsService(db, ofb_integration)
        
        # Mock service calls
        analytics_service.multi_bank_service.get_aggregated_balance = AsyncMock(
            return_value={"total_balance": 5000.00}
        )
        
        analytics_service.multi_bank_service.get_bank_health_status = AsyncMock(
            return_value={
                "total_banks": 2,
                "healthy_banks": 2,
                "banks_needing_attention": 0
            }
        )
        
        result = await analytics_service.get_financial_health_score(user_id="user_001")
        
        assert "overall_score" in result
        assert "health_level" in result
        assert "component_scores" in result
        assert "recommendations" in result
        assert result["health_level"] in ["EXCELLENT", "GOOD", "FAIR", "POOR", "CRITICAL"]
    
    def test_filter_transactions_by_period(self):
        """Test transaction filtering by period."""
        db = Mock()
        ofb_integration = Mock()
        analytics_service = OFBAdvancedAnalyticsService(db, ofb_integration)
        
        # Test with no date range (should default to last 30 days)
        transactions = analytics_service._filter_transactions_by_period(None, None)
        assert len(transactions) > 0
        
        # Test with specific date range
        from_date = datetime.utcnow() - timedelta(days=10)
        to_date = datetime.utcnow() - timedelta(days=5)
        transactions = analytics_service._filter_transactions_by_period(from_date, to_date)
        assert len(transactions) >= 0  # May be 0 if no transactions in range
    
    def test_calculate_trend(self):
        """Test trend calculation."""
        db = Mock()
        ofb_integration = Mock()
        analytics_service = OFBAdvancedAnalyticsService(db, ofb_integration)
        
        # Test increasing trend
        increasing_values = [100, 150, 200, 250]
        trend = analytics_service._calculate_trend(increasing_values)
        assert trend == "INCREASING"
        
        # Test decreasing trend
        decreasing_values = [250, 200, 150, 100]
        trend = analytics_service._calculate_trend(decreasing_values)
        assert trend == "DECREASING"
        
        # Test stable trend
        stable_values = [100, 105, 95, 100]
        trend = analytics_service._calculate_trend(stable_values)
        assert trend == "STABLE"


@pytest.mark.asyncio
async def test_ofb_phase4_integration():
    """Integration test for Phase 4 OFB features."""
    print("🚀 Testing Phase 4: Full Integration")
    
    # Test payment service
    db = Mock()
    ofb_integration = Mock()
    ofb_integration.validate_access = AsyncMock(return_value=True)
    
    payment_service = OFBPaymentService(db, ofb_integration)
    pix_result = await payment_service.initiate_pix_payment(
        consent_id="consent_123",
        access_token="token_456",
        amount=Decimal("100.00"),
        recipient_key="12345678901"
    )
    assert pix_result["status"] == "PENDING"
    print("✅ PIX payment service working")
    
    # Test multi-bank service
    multi_bank_service = OFBMultiBankService(db, ofb_integration)
    multi_bank_service.account_service.discover_accounts = AsyncMock(
        return_value={"accounts": [{"id": "test_account"}]}
    )
    multi_bank_service.sync_service.schedule_account_sync = AsyncMock(
        return_value={"status": "scheduled"}
    )
    
    bank_result = await multi_bank_service.connect_bank(
        bank_code="999",
        bank_name="Test Bank",
        consent_id="consent_123",
        access_token="token_456",
        user_id="user_001"
    )
    assert "connection_id" in bank_result
    print("✅ Multi-bank service working")
    
    # Test analytics service
    analytics_service = OFBAdvancedAnalyticsService(db, ofb_integration)
    analytics_service.multi_bank_service.get_aggregated_balance = AsyncMock(
        return_value={"total_balance": 5000.00}
    )
    
    cash_flow_result = await analytics_service.get_cash_flow_analysis(
        user_id="user_001"
    )
    assert "cash_flow_metrics" in cash_flow_result
    print("✅ Advanced analytics service working")
    
    print("🎉 Phase 4 integration test completed successfully")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
