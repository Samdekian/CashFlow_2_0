"""
Open Finance Brasil Payment Service
Handles payment initiation for PIX, TED/DOC, and scheduled payments.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from decimal import Decimal
from uuid import uuid4

from ..core.open_finance_brasil import OpenFinanceBrasilIntegration
from ..models.transaction import Transaction
from ..schemas.transaction import TransactionCreate

logger = logging.getLogger(__name__)


class OFBPaymentService:
    """Service for handling Open Finance Brasil payment operations."""
    
    def __init__(self, db, ofb_integration: OpenFinanceBrasilIntegration):
        self.db = db
        self.ofb_integration = ofb_integration
        self.payment_statuses = {
            "PENDING": "pending",
            "PROCESSING": "processing", 
            "COMPLETED": "completed",
            "FAILED": "failed",
            "CANCELLED": "cancelled"
        }
    
    async def initiate_pix_payment(
        self,
        consent_id: str,
        access_token: str,
        amount: Decimal,
        recipient_key: str,
        recipient_key_type: str = "CPF",
        description: str = "",
        scheduled_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Initiate a PIX instant payment."""
        try:
            # Validate access token
            if not await self.ofb_integration.validate_access(consent_id, access_token):
                raise ValueError("Invalid or expired access token")
            
            # Create payment request
            payment_data = {
                "payment_type": "PIX",
                "amount": float(amount),
                "currency": "BRL",
                "recipient_key": recipient_key,
                "recipient_key_type": recipient_key_type,
                "description": description,
                "scheduled_date": scheduled_date.isoformat() if scheduled_date else None,
                "consent_id": consent_id
            }
            
            # Mock PIX payment initiation (replace with actual OFB API call)
            payment_id = f"pix_{uuid4().hex[:8]}"
            payment_status = "PENDING"
            
            if scheduled_date and scheduled_date > datetime.utcnow():
                payment_status = "SCHEDULED"
            
            # Store payment record
            payment_record = {
                "id": payment_id,
                "status": payment_status,
                "payment_data": payment_data,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"PIX payment initiated: {payment_id}")
            
            return {
                "payment_id": payment_id,
                "status": payment_status,
                "message": "PIX payment initiated successfully",
                "payment_data": payment_data,
                "estimated_completion": self._estimate_completion_time(payment_status)
            }
            
        except Exception as e:
            logger.error(f"PIX payment initiation failed: {str(e)}")
            raise
    
    async def initiate_ted_doc_transfer(
        self,
        consent_id: str,
        access_token: str,
        amount: Decimal,
        recipient_bank_code: str,
        recipient_agency: str,
        recipient_account: str,
        recipient_name: str,
        transfer_type: str = "TED",
        description: str = "",
        scheduled_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Initiate a TED or DOC transfer."""
        try:
            # Validate access token
            if not await self.ofb_integration.validate_access(consent_id, access_token):
                raise ValueError("Invalid or expired access token")
            
            # Validate transfer type
            if transfer_type not in ["TED", "DOC"]:
                raise ValueError("Transfer type must be TED or DOC")
            
            # Create transfer request
            transfer_data = {
                "transfer_type": transfer_type,
                "amount": float(amount),
                "currency": "BRL",
                "recipient_bank_code": recipient_bank_code,
                "recipient_agency": recipient_agency,
                "recipient_account": recipient_account,
                "recipient_name": recipient_name,
                "description": description,
                "scheduled_date": scheduled_date.isoformat() if scheduled_date else None,
                "consent_id": consent_id
            }
            
            # Mock transfer initiation (replace with actual OFB API call)
            transfer_id = f"{transfer_type.lower()}_{uuid4().hex[:8]}"
            transfer_status = "PENDING"
            
            if scheduled_date and scheduled_date > datetime.utcnow():
                transfer_status = "SCHEDULED"
            
            # Store transfer record
            transfer_record = {
                "id": transfer_id,
                "status": transfer_status,
                "transfer_data": transfer_data,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"{transfer_type} transfer initiated: {transfer_id}")
            
            return {
                "transfer_id": transfer_id,
                "status": transfer_status,
                "message": f"{transfer_type} transfer initiated successfully",
                "transfer_data": transfer_data,
                "estimated_completion": self._estimate_completion_time(transfer_status, transfer_type)
            }
            
        except Exception as e:
            logger.error(f"{transfer_type} transfer initiation failed: {str(e)}")
            raise
    
    async def schedule_recurring_payment(
        self,
        consent_id: str,
        access_token: str,
        payment_type: str,
        amount: Decimal,
        frequency: str,
        start_date: datetime,
        end_date: Optional[datetime] = None,
        max_occurrences: Optional[int] = None,
        **payment_details
    ) -> Dict[str, Any]:
        """Schedule a recurring payment."""
        try:
            # Validate access token
            if not await self.ofb_integration.validate_access(consent_id, access_token):
                raise ValueError("Invalid or expired access token")
            
            # Validate frequency
            valid_frequencies = ["daily", "weekly", "monthly", "yearly"]
            if frequency not in valid_frequencies:
                raise ValueError(f"Frequency must be one of: {valid_frequencies}")
            
            # Create recurring payment schedule
            schedule_id = f"recurring_{uuid4().hex[:8]}"
            
            schedule_data = {
                "schedule_id": schedule_id,
                "payment_type": payment_type,
                "amount": float(amount),
                "frequency": frequency,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat() if end_date else None,
                "max_occurrences": max_occurrences,
                "payment_details": payment_details,
                "consent_id": consent_id,
                "status": "ACTIVE"
            }
            
            # Store schedule record
            schedule_record = {
                "id": schedule_id,
                "schedule_data": schedule_data,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Recurring payment scheduled: {schedule_id}")
            
            return {
                "schedule_id": schedule_id,
                "message": "Recurring payment scheduled successfully",
                "schedule_data": schedule_data,
                "next_payment_date": self._calculate_next_payment_date(start_date, frequency)
            }
            
        except Exception as e:
            logger.error(f"Recurring payment scheduling failed: {str(e)}")
            raise
    
    async def get_payment_status(
        self,
        payment_id: str,
        consent_id: str,
        access_token: str
    ) -> Dict[str, Any]:
        """Get the status of a payment."""
        try:
            # Validate access token
            if not await self.ofb_integration.validate_access(consent_id, access_token):
                raise ValueError("Invalid or expired access token")
            
            # Mock payment status retrieval (replace with actual OFB API call)
            # In real implementation, this would query the OFB payment status endpoint
            
            payment_status = {
                "payment_id": payment_id,
                "status": "COMPLETED",  # Mock status
                "last_updated": datetime.utcnow().isoformat(),
                "details": {
                    "amount": 100.00,
                    "currency": "BRL",
                    "recipient": "John Doe",
                    "description": "Payment for services"
                }
            }
            
            return payment_status
            
        except Exception as e:
            logger.error(f"Payment status retrieval failed: {str(e)}")
            raise
    
    async def cancel_payment(
        self,
        payment_id: str,
        consent_id: str,
        access_token: str
    ) -> Dict[str, Any]:
        """Cancel a pending or scheduled payment."""
        try:
            # Validate access token
            if not await self.ofb_integration.validate_access(consent_id, access_token):
                raise ValueError("Invalid or expired access token")
            
            # Mock payment cancellation (replace with actual OFB API call)
            cancellation_result = {
                "payment_id": payment_id,
                "status": "CANCELLED",
                "cancelled_at": datetime.utcnow().isoformat(),
                "message": "Payment cancelled successfully"
            }
            
            logger.info(f"Payment cancelled: {payment_id}")
            
            return cancellation_result
            
        except Exception as e:
            logger.error(f"Payment cancellation failed: {str(e)}")
            raise
    
    async def get_payment_history(
        self,
        consent_id: str,
        access_token: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None,
        payment_type: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 25
    ) -> Dict[str, Any]:
        """Get payment history with filtering and pagination."""
        try:
            # Validate access token
            if not await self.ofb_integration.validate_access(consent_id, access_token):
                raise ValueError("Invalid or expired access token")
            
            # Mock payment history (replace with actual OFB API call)
            mock_payments = [
                {
                    "id": f"pix_{uuid4().hex[:8]}",
                    "type": "PIX",
                    "amount": 50.00,
                    "status": "COMPLETED",
                    "created_at": (datetime.utcnow() - timedelta(days=1)).isoformat(),
                    "recipient": "Jane Smith",
                    "description": "Coffee payment"
                },
                {
                    "id": f"ted_{uuid4().hex[:8]}",
                    "type": "TED",
                    "amount": 500.00,
                    "status": "COMPLETED",
                    "created_at": (datetime.utcnow() - timedelta(days=3)).isoformat(),
                    "recipient": "ABC Company",
                    "description": "Invoice payment"
                }
            ]
            
            # Apply filters (in real implementation, this would be done at database level)
            filtered_payments = mock_payments
            
            if payment_type:
                filtered_payments = [p for p in filtered_payments if p["type"] == payment_type]
            
            if status:
                filtered_payments = [p for p in filtered_payments if p["status"] == status]
            
            # Apply pagination
            total_count = len(filtered_payments)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_payments = filtered_payments[start_idx:end_idx]
            
            return {
                "payments": paginated_payments,
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "total_count": total_count,
                    "total_pages": (total_count + page_size - 1) // page_size
                },
                "filters": {
                    "from_date": from_date.isoformat() if from_date else None,
                    "to_date": to_date.isoformat() if to_date else None,
                    "payment_type": payment_type,
                    "status": status
                }
            }
            
        except Exception as e:
            logger.error(f"Payment history retrieval failed: {str(e)}")
            raise
    
    def _estimate_completion_time(self, status: str, payment_type: str = "PIX") -> str:
        """Estimate completion time based on payment type and status."""
        if status == "COMPLETED":
            return "Already completed"
        
        if payment_type == "PIX":
            if status == "PENDING":
                return "Within 10 seconds"
            elif status == "PROCESSING":
                return "Within 30 seconds"
        elif payment_type in ["TED", "DOC"]:
            if status == "PENDING":
                return "Within 1 business day"
            elif status == "PROCESSING":
                return "Within 2 business days"
        
        return "Unknown"
    
    def _calculate_next_payment_date(self, start_date: datetime, frequency: str) -> str:
        """Calculate the next payment date based on frequency."""
        current_date = datetime.utcnow()
        
        if start_date > current_date:
            return start_date.isoformat()
        
        if frequency == "daily":
            next_date = current_date + timedelta(days=1)
        elif frequency == "weekly":
            next_date = current_date + timedelta(weeks=1)
        elif frequency == "monthly":
            # Simple monthly calculation (30 days)
            next_date = current_date + timedelta(days=30)
        elif frequency == "yearly":
            next_date = current_date + timedelta(days=365)
        else:
            next_date = current_date + timedelta(days=1)
        
        return next_date.isoformat()
