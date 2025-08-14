"""
Open Finance Brasil Data Synchronization Service
Phase 3: Automated Account Data Synchronization
"""

import asyncio
import logging
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..core.open_finance_brasil import OpenFinanceBrasilIntegration, OFBConfig
from ..services.ofb_account_service import OFBAccountService
from ..config_ofb import ofb_settings

logger = logging.getLogger(__name__)


class OFBSyncService:
    """Service for automated Open Finance Brasil data synchronization"""
    
    def __init__(self, db: Session):
        self.db = db
        self.account_service = OFBAccountService(db)
        self.sync_jobs: Dict[str, Dict[str, Any]] = {}  # Track sync jobs
        
    async def schedule_account_sync(self,
                                  account_id: str,
                                  consent_id: str,
                                  access_token: str,
                                  sync_frequency: str = "daily",
                                  sync_time: str = "06:00") -> Dict[str, Any]:
        """Schedule automated account synchronization"""
        
        try:
            # Create sync job configuration
            sync_job = {
                "account_id": account_id,
                "consent_id": consent_id,
                "access_token": access_token,
                "sync_frequency": sync_frequency,
                "sync_time": sync_time,
                "last_sync": None,
                "next_sync": self._calculate_next_sync(sync_frequency, sync_time),
                "status": "scheduled",
                "created_at": datetime.utcnow().isoformat(),
                "enabled": True
            }
            
            # Store sync job
            self.sync_jobs[account_id] = sync_job
            
            logger.info(f"Scheduled sync for account {account_id} with frequency {sync_frequency}")
            
            return {
                "status": "scheduled",
                "account_id": account_id,
                "sync_frequency": sync_frequency,
                "next_sync": sync_job["next_sync"],
                "job_id": account_id
            }
            
        except Exception as e:
            logger.error(f"Failed to schedule account sync: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to schedule account sync: {str(e)}"
            )
    
    async def execute_scheduled_sync(self) -> Dict[str, Any]:
        """Execute all scheduled synchronization jobs"""
        
        try:
            sync_results = []
            current_time = datetime.utcnow()
            
            for account_id, sync_job in self.sync_jobs.items():
                if not sync_job["enabled"]:
                    continue
                
                # Check if it's time to sync
                next_sync = datetime.fromisoformat(sync_job["next_sync"])
                if current_time >= next_sync:
                    try:
                        # Execute sync
                        sync_result = await self.account_service.sync_account_data(
                            account_id=account_id,
                            consent_id=sync_job["consent_id"],
                            access_token=sync_job["access_token"]
                        )
                        
                        # Update sync job
                        sync_job["last_sync"] = current_time.isoformat()
                        sync_job["next_sync"] = self._calculate_next_sync(
                            sync_job["sync_frequency"], 
                            sync_job["sync_time"]
                        )
                        sync_job["status"] = "completed"
                        
                        sync_results.append({
                            "account_id": account_id,
                            "status": "success",
                            "result": sync_result
                        })
                        
                        logger.info(f"Successfully synced account {account_id}")
                        
                    except Exception as e:
                        # Update sync job with error
                        sync_job["last_sync"] = current_time.isoformat()
                        sync_job["next_sync"] = self._calculate_next_sync(
                            sync_job["sync_frequency"], 
                            sync_job["sync_time"]
                        )
                        sync_job["status"] = "failed"
                        
                        sync_results.append({
                            "account_id": account_id,
                            "status": "failed",
                            "error": str(e)
                        })
                        
                        logger.error(f"Failed to sync account {account_id}: {e}")
            
            return {
                "status": "completed",
                "total_jobs": len(self.sync_jobs),
                "executed_jobs": len(sync_results),
                "results": sync_results,
                "execution_time": current_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Scheduled sync execution failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Scheduled sync execution failed: {str(e)}"
            )
    
    async def sync_all_accounts(self, user_consents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Synchronize all accounts for a user"""
        
        try:
            sync_results = []
            
            for consent in user_consents:
                consent_id = consent["consent_id"]
                access_token = consent["access_token"]
                
                # Discover accounts for this consent
                accounts = await self.account_service.discover_accounts(consent_id, access_token)
                
                for account in accounts:
                    try:
                        # Sync account data
                        sync_result = await self.account_service.sync_account_data(
                            account_id=account["accountId"],
                            consent_id=consent_id,
                            access_token=access_token
                        )
                        
                        sync_results.append({
                            "account_id": account["accountId"],
                            "bank_name": account["brandName"],
                            "status": "success",
                            "result": sync_result
                        })
                        
                    except Exception as e:
                        sync_results.append({
                            "account_id": account["accountId"],
                            "bank_name": account["brandName"],
                            "status": "failed",
                            "error": str(e)
                        })
                        
                        logger.error(f"Failed to sync account {account['accountId']}: {e}")
            
            return {
                "status": "completed",
                "total_accounts": len(sync_results),
                "successful_syncs": len([r for r in sync_results if r["status"] == "success"]),
                "failed_syncs": len([r for r in sync_results if r["status"] == "failed"]),
                "results": sync_results,
                "sync_timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Multi-account sync failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Multi-account sync failed: {str(e)}"
            )
    
    async def get_sync_status(self, account_id: Optional[str] = None) -> Dict[str, Any]:
        """Get synchronization status for accounts"""
        
        try:
            if account_id:
                # Get status for specific account
                if account_id not in self.sync_jobs:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"No sync job found for account {account_id}"
                    )
                
                sync_job = self.sync_jobs[account_id]
                return {
                    "account_id": account_id,
                    "sync_status": sync_job
                }
            else:
                # Get status for all accounts
                return {
                    "total_jobs": len(self.sync_jobs),
                    "enabled_jobs": len([j for j in self.sync_jobs.values() if j["enabled"]]),
                    "disabled_jobs": len([j for j in self.sync_jobs.values() if not j["enabled"]]),
                    "sync_jobs": self.sync_jobs
                }
                
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get sync status: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get sync status: {str(e)}"
            )
    
    async def update_sync_config(self,
                               account_id: str,
                               sync_frequency: Optional[str] = None,
                               sync_time: Optional[str] = None,
                               enabled: Optional[bool] = None) -> Dict[str, Any]:
        """Update synchronization configuration for an account"""
        
        try:
            if account_id not in self.sync_jobs:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No sync job found for account {account_id}"
                )
            
            sync_job = self.sync_jobs[account_id]
            
            # Update configuration
            if sync_frequency is not None:
                sync_job["sync_frequency"] = sync_frequency
                sync_job["next_sync"] = self._calculate_next_sync(sync_frequency, sync_job["sync_time"])
            
            if sync_time is not None:
                sync_job["sync_time"] = sync_time
                sync_job["next_sync"] = self._calculate_next_sync(sync_job["sync_frequency"], sync_time)
            
            if enabled is not None:
                sync_job["enabled"] = enabled
            
            logger.info(f"Updated sync config for account {account_id}")
            
            return {
                "status": "updated",
                "account_id": account_id,
                "sync_config": sync_job
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to update sync config: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update sync config: {str(e)}"
            )
    
    async def remove_sync_job(self, account_id: str) -> Dict[str, Any]:
        """Remove synchronization job for an account"""
        
        try:
            if account_id not in self.sync_jobs:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No sync job found for account {account_id}"
                )
            
            # Remove sync job
            removed_job = self.sync_jobs.pop(account_id)
            
            logger.info(f"Removed sync job for account {account_id}")
            
            return {
                "status": "removed",
                "account_id": account_id,
                "removed_job": removed_job
            }
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to remove sync job: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to remove sync job: {str(e)}"
            )
    
    def _calculate_next_sync(self, frequency: str, sync_time: str) -> str:
        """Calculate next sync time based on frequency and time"""
        
        try:
            # Parse sync time
            hour, minute = map(int, sync_time.split(":"))
            current_time = datetime.utcnow()
            
            # Create next sync time
            if frequency == "daily":
                next_sync = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if next_sync <= current_time:
                    next_sync += timedelta(days=1)
            
            elif frequency == "weekly":
                # Sync every Monday at specified time
                days_ahead = 7 - current_time.weekday()
                if days_ahead == 7:
                    days_ahead = 0
                next_sync = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0) + timedelta(days=days_ahead)
            
            elif frequency == "monthly":
                # Sync on the 1st of each month
                if current_time.day > 1:
                    next_sync = current_time.replace(day=1, hour=hour, minute=minute, second=0, microsecond=0)
                    if current_time.month == 12:
                        next_sync = next_sync.replace(year=current_time.year + 1, month=1)
                    else:
                        next_sync = next_sync.replace(month=current_time.month + 1)
                else:
                    next_sync = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            else:
                # Default to daily
                next_sync = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)
                if next_sync <= current_time:
                    next_sync += timedelta(days=1)
            
            return next_sync.isoformat()
            
        except Exception as e:
            logger.error(f"Failed to calculate next sync time: {e}")
            # Default to tomorrow at current time
            return (datetime.utcnow() + timedelta(days=1)).isoformat()
