"""
Open Finance Brasil Account Information Service
Phase 3: Account Discovery, Balance Retrieval, and Transaction Import
"""

import logging
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..core.open_finance_brasil import OpenFinanceBrasilIntegration, OFBConfig
from ..models.transaction import Transaction
from ..models.category import Category
from ..services.categorization_service import CategorizationService
from ..schemas.transaction import TransactionCreate
from ..config_ofb import ofb_settings

logger = logging.getLogger(__name__)


class OFBAccountService:
    """Service for Open Finance Brasil Account Information APIs"""
    
    def __init__(self, db: Session):
        self.db = db
        self.categorization_service = CategorizationService(db)
        self.ofb_integration: Optional[OpenFinanceBrasilIntegration] = None
        
    async def _get_ofb_integration(self) -> OpenFinanceBrasilIntegration:
        """Get OFB integration instance"""
        if self.ofb_integration is None:
            if not ofb_settings.is_configured():
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Open Finance Brasil integration not configured"
                )
            
            # Create OFB configuration
            cert_paths = ofb_settings.get_certificate_paths()
            endpoints = ofb_settings.get_endpoints()
            
            config = OFBConfig(
                client_id=ofb_settings.ofb_client_id,
                client_secret=ofb_settings.ofb_client_secret,
                redirect_uri=ofb_settings.ofb_redirect_uri,
                **endpoints,
                **cert_paths,
                request_timeout=ofb_settings.ofb_request_timeout,
                max_retries=ofb_settings.ofb_max_retries,
                rate_limit_requests=ofb_settings.ofb_rate_limit_requests,
                rate_limit_window=ofb_settings.ofb_rate_limit_window
            )
            
            self.ofb_integration = OpenFinanceBrasilIntegration(config)
            await self.ofb_integration.initialize()
        
        return self.ofb_integration
    
    async def discover_accounts(self, consent_id: str, access_token: str) -> List[Dict[str, Any]]:
        """Discover bank accounts for a user"""
        
        try:
            ofb = await self._get_ofb_integration()
            
            # Validate consent has account permissions
            has_access = await ofb.validate_access(consent_id, ["accounts"])
            if not has_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions for account discovery"
                )
            
            # In production, this would call the actual OFB accounts API
            # For now, return mock data for development
            mock_accounts = [
                {
                    "accountId": "account_001",
                    "type": "CACC",
                    "subtype": "CURRENT_ACCOUNT",
                    "currency": "BRL",
                    "brandName": "Banco do Brasil",
                    "companyCnpj": "00000000000191",
                    "number": "12345-6",
                    "checkDigit": "7",
                    "agencyNumber": "1234",
                    "agencyCheckDigit": "5",
                    "status": "ACTIVE"
                },
                {
                    "accountId": "account_002",
                    "type": "SVGS",
                    "subtype": "SAVINGS_ACCOUNT",
                    "currency": "BRL",
                    "brandName": "Banco do Brasil",
                    "companyCnpj": "00000000000191",
                    "number": "98765-4",
                    "checkDigit": "3",
                    "agencyNumber": "1234",
                    "agencyCheckDigit": "5",
                    "status": "ACTIVE"
                }
            ]
            
            logger.info(f"Discovered {len(mock_accounts)} accounts for consent {consent_id}")
            return mock_accounts
            
        except Exception as e:
            logger.error(f"Account discovery failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Account discovery failed: {str(e)}"
            )
    
    async def get_account_balances(self, 
                                 account_id: str, 
                                 consent_id: str, 
                                 access_token: str) -> Dict[str, Any]:
        """Get account balance information"""
        
        try:
            ofb = await self._get_ofb_integration()
            
            # Validate consent has account permissions
            has_access = await ofb.validate_access(consent_id, ["accounts"])
            if not has_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions for balance retrieval"
                )
            
            # In production, this would call the actual OFB balances API
            # For now, return mock data for development
            mock_balance = {
                "availableAmount": "1250.75",
                "availableAmountCurrency": "BRL",
                "blockedAmount": "0.00",
                "blockedAmountCurrency": "BRL",
                "automaticallyInvestedAmount": "500.00",
                "automaticallyInvestedAmountCurrency": "BRL",
                "lastUpdated": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Retrieved balance for account {account_id}")
            return mock_balance
            
        except Exception as e:
            logger.error(f"Balance retrieval failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Balance retrieval failed: {str(e)}"
            )
    
    async def get_account_transactions(self,
                                     account_id: str,
                                     consent_id: str,
                                     access_token: str,
                                     from_date: Optional[date] = None,
                                     to_date: Optional[date] = None,
                                     page_size: int = 25,
                                     page: int = 1) -> Dict[str, Any]:
        """Get account transactions"""
        
        try:
            ofb = await self._get_ofb_integration()
            
            # Validate consent has transaction permissions
            has_access = await ofb.validate_access(consent_id, ["transactions"])
            if not has_access:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions for transaction retrieval"
                )
            
            # Set default date range if not provided
            if not from_date:
                from_date = date.today() - timedelta(days=30)
            if not to_date:
                to_date = date.today()
            
            # In production, this would call the actual OFB transactions API
            # For now, return mock data for development
            mock_transactions = [
                {
                    "transactionId": "txn_001",
                    "bookingDate": "2024-01-15",
                    "amount": "150.50",
                    "currency": "BRL",
                    "creditDebitType": "DEBITO",
                    "transactionName": "RESTAURANTE ABC",
                    "referenceNumber": "REF123456",
                    "type": "PURCHASE",
                    "transactionCategory": "ALIMENTACAO"
                },
                {
                    "transactionId": "txn_002",
                    "bookingDate": "2024-01-14",
                    "amount": "2500.00",
                    "currency": "BRL",
                    "creditDebitType": "CREDITO",
                    "transactionName": "SALARIO",
                    "referenceNumber": "REF789012",
                    "type": "CREDIT",
                    "transactionCategory": "RECEITA"
                },
                {
                    "transactionId": "txn_003",
                    "bookingDate": "2024-01-13",
                    "amount": "89.90",
                    "currency": "BRL",
                    "creditDebitType": "DEBITO",
                    "transactionName": "COMBUSTIVEL",
                    "referenceNumber": "REF345678",
                    "type": "PURCHASE",
                    "transactionCategory": "TRANSPORTE"
                }
            ]
            
            # Filter transactions by date range
            filtered_transactions = []
            for txn in mock_transactions:
                txn_date = datetime.strptime(txn["bookingDate"], "%Y-%m-%d").date()
                if from_date <= txn_date <= to_date:
                    filtered_transactions.append(txn)
            
            # Apply pagination
            total = len(filtered_transactions)
            start = (page - 1) * page_size
            end = start + page_size
            paginated_transactions = filtered_transactions[start:end]
            
            logger.info(f"Retrieved {len(paginated_transactions)} transactions for account {account_id}")
            
            return {
                "transactions": paginated_transactions,
                "pagination": {
                    "total": total,
                    "page": page,
                    "size": page_size,
                    "pages": (total + page_size - 1) // page_size
                },
                "dateRange": {
                    "from": from_date.isoformat(),
                    "to": to_date.isoformat()
                }
            }
            
        except Exception as e:
            logger.error(f"Transaction retrieval failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Transaction retrieval failed: {str(e)}"
            )
    
    async def import_transactions(self,
                                account_id: str,
                                consent_id: str,
                                access_token: str,
                                from_date: Optional[date] = None,
                                to_date: Optional[date] = None,
                                auto_categorize: bool = True) -> Dict[str, Any]:
        """Import transactions from OFB to local database"""
        
        try:
            # Get transactions from OFB
            transactions_data = await self.get_account_transactions(
                account_id=account_id,
                consent_id=consent_id,
                access_token=access_token,
                from_date=from_date,
                to_date=to_date,
                page_size=1000,  # Get all transactions for import
                page=1
            )
            
            transactions = transactions_data["transactions"]
            imported_count = 0
            skipped_count = 0
            errors = []
            
            for txn in transactions:
                try:
                    # Check if transaction already exists
                    existing_txn = self.db.query(Transaction).filter(
                        Transaction.external_id == txn["transactionId"]
                    ).first()
                    
                    if existing_txn:
                        skipped_count += 1
                        continue
                    
                    # Transform OFB transaction to local format
                    amount = Decimal(txn["amount"])
                    if txn["creditDebitType"] == "DEBITO":
                        amount = -amount  # Negative for expenses
                    
                    # Auto-categorize if requested
                    category_id = None
                    if auto_categorize:
                        category = await self.categorization_service.suggest_category(
                            txn.get("transactionName", ""),
                            float(abs(amount)),
                            txn.get("transactionCategory", "")
                        )
                        if category:
                            category_id = category.id
                    
                    # Create transaction
                    transaction_data = TransactionCreate(
                        date=datetime.strptime(txn["bookingDate"], "%Y-%m-%d").date(),
                        amount=amount,
                        description=txn.get("transactionName", txn.get("referenceNumber", "")),
                        transaction_type=self._map_transaction_type(txn.get("type", "")),
                        category_id=category_id,
                        external_id=txn["transactionId"],
                        currency=txn.get("currency", "BRL"),
                        country_code="BR",
                        reference_number=txn.get("referenceNumber"),
                        tags=self._extract_tags(txn),
                        notes=self._extract_notes(txn)
                    )
                    
                    # Save to database
                    transaction = Transaction(**transaction_data.dict())
                    self.db.add(transaction)
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Transaction {txn.get('transactionId', 'unknown')}: {str(e)}")
                    logger.error(f"Failed to import transaction {txn.get('transactionId', 'unknown')}: {e}")
            
            # Commit all transactions
            self.db.commit()
            
            logger.info(f"Imported {imported_count} transactions, skipped {skipped_count}")
            
            return {
                "status": "completed",
                "imported_count": imported_count,
                "skipped_count": skipped_count,
                "total_processed": len(transactions),
                "errors": errors,
                "account_id": account_id,
                "date_range": {
                    "from": from_date.isoformat() if from_date else None,
                    "to": to_date.isoformat() if to_date else None
                }
            }
            
        except Exception as e:
            logger.error(f"Transaction import failed: {e}")
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Transaction import failed: {str(e)}"
            )
    
    async def sync_account_data(self,
                               account_id: str,
                               consent_id: str,
                               access_token: str) -> Dict[str, Any]:
        """Synchronize all account data (balance + recent transactions)"""
        
        try:
            # Get account balance
            balance = await self.get_account_balances(account_id, consent_id, access_token)
            
            # Get recent transactions (last 7 days)
            from_date = date.today() - timedelta(days=7)
            transactions_data = await self.get_account_transactions(
                account_id=account_id,
                consent_id=consent_id,
                access_token=access_token,
                from_date=from_date,
                page_size=100
            )
            
            # Import new transactions
            import_result = await self.import_transactions(
                account_id=account_id,
                consent_id=consent_id,
                access_token=access_token,
                from_date=from_date,
                auto_categorize=True
            )
            
            return {
                "status": "synced",
                "account_id": account_id,
                "balance": balance,
                "recent_transactions": len(transactions_data["transactions"]),
                "import_result": import_result,
                "sync_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Account sync failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Account sync failed: {str(e)}"
            )
    
    def _map_transaction_type(self, ofb_type: str) -> str:
        """Map OFB transaction type to local transaction type"""
        mapping = {
            "PURCHASE": "DESPESA",
            "CREDIT": "RECEITA",
            "TRANSFER": "TRANSFERENCIA",
            "INVESTMENT": "INVESTIMENTO"
        }
        return mapping.get(ofb_type, "OUTROS")
    
    def _extract_tags(self, transaction: Dict[str, Any]) -> List[str]:
        """Extract relevant tags from transaction data"""
        tags = []
        
        if transaction.get("type"):
            tags.append(transaction["type"])
        
        if transaction.get("transactionCategory"):
            tags.append(transaction["transactionCategory"])
        
        return tags
    
    def _extract_notes(self, transaction: Dict[str, Any]) -> str:
        """Extract additional notes from transaction data"""
        notes_parts = []
        
        if transaction.get("referenceNumber"):
            notes_parts.append(f"Ref: {transaction['referenceNumber']}")
        
        if transaction.get("type"):
            notes_parts.append(f"Type: {transaction['type']}")
        
        return " | ".join(notes_parts) if notes_parts else None
