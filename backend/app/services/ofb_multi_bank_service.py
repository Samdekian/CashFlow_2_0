"""
Open Finance Brasil Multi-Bank Aggregation Service
Handles multiple bank connections and aggregated financial data.
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Set
from decimal import Decimal
from uuid import uuid4

from ..core.open_finance_brasil import OpenFinanceBrasilIntegration
from ..services.ofb_account_service import OFBAccountService
from ..services.ofb_sync_service import OFBSyncService

logger = logging.getLogger(__name__)


class OFBMultiBankService:
    """Service for handling multi-bank aggregation and management."""
    
    def __init__(self, db, ofb_integration: OpenFinanceBrasilIntegration):
        self.db = db
        self.ofb_integration = ofb_integration
        self.account_service = OFBAccountService(db)
        self.sync_service = OFBSyncService(db)
        
        # Mock bank connections (replace with database storage)
        self.bank_connections = {
            "bank_001": {
                "id": "bank_001",
                "name": "Banco do Brasil",
                "code": "001",
                "status": "ACTIVE",
                "consent_id": "consent_bb_123",
                "access_token": "token_bb_456",
                "connected_at": (datetime.utcnow() - timedelta(days=30)).isoformat(),
                "last_sync": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                "accounts": ["account_bb_001", "account_bb_002"]
            },
            "bank_002": {
                "id": "bank_002",
                "name": "Itaú Unibanco",
                "code": "341",
                "status": "ACTIVE",
                "consent_id": "consent_itau_789",
                "access_token": "token_itau_012",
                "connected_at": (datetime.utcnow() - timedelta(days=15)).isoformat(),
                "last_sync": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                "accounts": ["account_itau_001"]
            },
            "bank_003": {
                "id": "bank_003",
                "name": "Bradesco",
                "code": "237",
                "status": "PENDING",
                "consent_id": "consent_bradesco_345",
                "access_token": "token_bradesco_678",
                "connected_at": (datetime.utcnow() - timedelta(days=5)).isoformat(),
                "last_sync": None,
                "accounts": []
            }
        }
    
    async def connect_bank(
        self,
        bank_code: str,
        bank_name: str,
        consent_id: str,
        access_token: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Connect a new bank to the user's account."""
        try:
            # Validate access token
            if not await self.ofb_integration.validate_access(consent_id, access_token):
                raise ValueError("Invalid or expired access token")
            
            # Check if bank is already connected
            existing_connection = next(
                (conn for conn in self.bank_connections.values() 
                 if conn["code"] == bank_code and conn["status"] == "ACTIVE"),
                None
            )
            
            if existing_connection:
                raise ValueError(f"Bank {bank_name} is already connected")
            
            # Create new bank connection
            connection_id = f"bank_{uuid4().hex[:8]}"
            
            new_connection = {
                "id": connection_id,
                "name": bank_name,
                "code": bank_code,
                "status": "ACTIVE",
                "consent_id": consent_id,
                "access_token": access_token,
                "user_id": user_id,
                "connected_at": datetime.utcnow().isoformat(),
                "last_sync": None,
                "accounts": []
            }
            
            # Store connection
            self.bank_connections[connection_id] = new_connection
            
            # Discover accounts for the new bank
            accounts = await self.account_service.discover_accounts(consent_id, access_token)
            new_connection["accounts"] = [acc["id"] for acc in accounts.get("accounts", [])]
            
            # Schedule initial sync
            for account_id in new_connection["accounts"]:
                await self.sync_service.schedule_account_sync(
                    account_id, consent_id, access_token, "daily"
                )
            
            logger.info(f"Bank {bank_name} connected successfully: {connection_id}")
            
            return {
                "connection_id": connection_id,
                "message": f"Bank {bank_name} connected successfully",
                "connection": new_connection,
                "accounts_discovered": len(new_connection["accounts"])
            }
            
        except Exception as e:
            logger.error(f"Bank connection failed: {str(e)}")
            raise
    
    async def disconnect_bank(
        self,
        connection_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """Disconnect a bank from the user's account."""
        try:
            # Find the connection
            connection = self.bank_connections.get(connection_id)
            if not connection:
                raise ValueError("Bank connection not found")
            
            # Verify user ownership
            if connection.get("user_id") != user_id:
                raise ValueError("Unauthorized access to bank connection")
            
            # Remove sync jobs for all accounts
            for account_id in connection["accounts"]:
                await self.sync_service.remove_sync_job(account_id)
            
            # Update connection status
            connection["status"] = "DISCONNECTED"
            connection["disconnected_at"] = datetime.utcnow().isoformat()
            
            logger.info(f"Bank {connection['name']} disconnected: {connection_id}")
            
            return {
                "connection_id": connection_id,
                "message": f"Bank {connection['name']} disconnected successfully",
                "status": "DISCONNECTED",
                "disconnected_at": connection["disconnected_at"]
            }
            
        except Exception as e:
            logger.error(f"Bank disconnection failed: {str(e)}")
            raise
    
    async def get_connected_banks(self, user_id: str) -> Dict[str, Any]:
        """Get all connected banks for a user."""
        try:
            user_connections = [
                conn for conn in self.bank_connections.values()
                if conn.get("user_id") == user_id
            ]
            
            # Group by status
            active_connections = [conn for conn in user_connections if conn["status"] == "ACTIVE"]
            pending_connections = [conn for conn in user_connections if conn["status"] == "PENDING"]
            disconnected_connections = [conn for conn in user_connections if conn["status"] == "DISCONNECTED"]
            
            return {
                "total_connections": len(user_connections),
                "active_connections": active_connections,
                "pending_connections": pending_connections,
                "disconnected_connections": disconnected_connections,
                "summary": {
                    "total_accounts": sum(len(conn["accounts"]) for conn in active_connections),
                    "last_sync": max(
                        (conn["last_sync"] for conn in active_connections if conn["last_sync"]),
                        default=None
                    )
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get connected banks: {str(e)}")
            raise
    
    async def get_aggregated_balance(self, user_id: str) -> Dict[str, Any]:
        """Get aggregated balance across all connected banks."""
        try:
            active_connections = [
                conn for conn in self.bank_connections.values()
                if conn.get("user_id") == user_id and conn["status"] == "ACTIVE"
            ]
            
            total_balance = Decimal('0.00')
            bank_balances = []
            
            for connection in active_connections:
                bank_total = Decimal('0.00')
                
                for account_id in connection["accounts"]:
                    try:
                        balance_data = await self.account_service.get_account_balances(
                            account_id, connection["consent_id"], connection["access_token"]
                        )
                        
                        if "balances" in balance_data:
                            for balance in balance_data["balances"]:
                                if balance.get("type") == "AVAILABLE":
                                    account_balance = Decimal(str(balance.get("amount", 0)))
                                    bank_total += account_balance
                                    break
                    except Exception as e:
                        logger.warning(f"Failed to get balance for account {account_id}: {str(e)}")
                        continue
                
                bank_balances.append({
                    "bank_name": connection["name"],
                    "bank_code": connection["code"],
                    "total_balance": float(bank_total),
                    "currency": "BRL"
                })
                
                total_balance += bank_total
            
            return {
                "total_balance": float(total_balance),
                "currency": "BRL",
                "bank_breakdown": bank_balances,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get aggregated balance: {str(e)}")
            raise
    
    async def sync_all_banks(self, user_id: str) -> Dict[str, Any]:
        """Sync all connected banks for a user."""
        try:
            active_connections = [
                conn for conn in self.bank_connections.values()
                if conn.get("user_id") == user_id and conn["status"] == "ACTIVE"
            ]
            
            sync_results = []
            total_accounts_synced = 0
            
            for connection in active_connections:
                try:
                    # Sync all accounts for this bank
                    sync_result = await self.sync_service.sync_all_accounts([
                        {
                            "account_id": account_id,
                            "consent_id": connection["consent_id"],
                            "access_token": connection["access_token"]
                        }
                        for account_id in connection["accounts"]
                    ])
                    
                    sync_results.append({
                        "bank_name": connection["name"],
                        "bank_code": connection["code"],
                        "sync_result": sync_result
                    })
                    
                    total_accounts_synced += len(connection["accounts"])
                    
                    # Update last sync timestamp
                    connection["last_sync"] = datetime.utcnow().isoformat()
                    
                except Exception as e:
                    logger.error(f"Failed to sync bank {connection['name']}: {str(e)}")
                    sync_results.append({
                        "bank_name": connection["name"],
                        "bank_code": connection["code"],
                        "sync_result": {"status": "failed", "error": str(e)}
                    })
            
            return {
                "total_banks_synced": len(active_connections),
                "total_accounts_synced": total_accounts_synced,
                "sync_results": sync_results,
                "sync_completed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to sync all banks: {str(e)}")
            raise
    
    async def get_bank_health_status(self, user_id: str) -> Dict[str, Any]:
        """Get health status of all connected banks."""
        try:
            active_connections = [
                conn for conn in self.bank_connections.values()
                if conn.get("user_id") == user_id and conn["status"] == "ACTIVE"
            ]
            
            health_status = []
            
            for connection in active_connections:
                # Check last sync time
                last_sync = connection.get("last_sync")
                if last_sync:
                    last_sync_dt = datetime.fromisoformat(last_sync)
                    hours_since_sync = (datetime.utcnow() - last_sync_dt).total_seconds() / 3600
                    
                    if hours_since_sync < 1:
                        sync_status = "EXCELLENT"
                    elif hours_since_sync < 6:
                        sync_status = "GOOD"
                    elif hours_since_sync < 24:
                        sync_status = "WARNING"
                    else:
                        sync_status = "CRITICAL"
                else:
                    sync_status = "NEVER_SYNCED"
                
                # Check account count
                account_count = len(connection["accounts"])
                if account_count > 0:
                    account_status = "HEALTHY"
                else:
                    account_status = "NO_ACCOUNTS"
                
                health_status.append({
                    "bank_name": connection["name"],
                    "bank_code": connection["code"],
                    "sync_status": sync_status,
                    "account_status": account_status,
                    "last_sync": last_sync,
                    "account_count": account_count,
                    "overall_status": "HEALTHY" if sync_status in ["EXCELLENT", "GOOD"] else "NEEDS_ATTENTION"
                })
            
            return {
                "total_banks": len(active_connections),
                "healthy_banks": len([h for h in health_status if h["overall_status"] == "HEALTHY"]),
                "banks_needing_attention": len([h for h in health_status if h["overall_status"] == "NEEDS_ATTENTION"]),
                "health_details": health_status,
                "last_checked": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get bank health status: {str(e)}")
            raise
