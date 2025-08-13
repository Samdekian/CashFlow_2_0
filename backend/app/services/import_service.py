"""
Import service for processing various file formats.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, date
from decimal import Decimal
from uuid import UUID, uuid4
import csv
import io
import json

from ..models.transaction import Transaction
from ..models.category import Category
from ..schemas.import_export import (
    ImportPreviewResponse,
    ImportResultResponse,
    ImportHistoryResponse,
    ValidationResultResponse,
    DuplicateDetectionResponse
)
from ..services.categorization_service import CategorizationService


class ImportService:
    """Service for importing transactions from various file formats."""
    
    def __init__(self):
        self.import_sessions = {}  # In-memory storage for import sessions
    
    def process_csv_file(self, content: bytes, auto_categorize: bool = True, 
                        skip_duplicates: bool = True, db: Session = None) -> ImportPreviewResponse:
        """Process CSV file and return import preview."""
        try:
            # Decode content
            text_content = content.decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(text_content))
            
            # Process rows
            transactions = []
            errors = []
            
            for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (1 is header)
                try:
                    transaction = self._parse_csv_row(row, row_num)
                    if transaction:
                        transactions.append(transaction)
                except Exception as e:
                    errors.append(f"Row {row_num}: {str(e)}")
            
            # Auto-categorize if requested
            if auto_categorize and db:
                categorization_service = CategorizationService(db)
                for transaction in transactions:
                    category = categorization_service.suggest_category(
                        transaction["description"], float(transaction["amount"])
                    )
                    if category:
                        transaction["category_id"] = category.id
            
            # Create import session
            import_id = str(uuid4())
            self.import_sessions[import_id] = {
                "transactions": transactions,
                "errors": errors,
                "status": "preview",
                "created_at": datetime.utcnow(),
                "file_type": "csv"
            }
            
            return ImportPreviewResponse(
                import_id=import_id,
                total_transactions=len(transactions),
                valid_transactions=len(transactions),
                errors=errors,
                preview_data=transactions[:10],  # First 10 transactions
                status="preview"
            )
            
        except Exception as e:
            return ImportPreviewResponse(
                import_id="",
                total_transactions=0,
                valid_transactions=0,
                errors=[f"File processing failed: {str(e)}"],
                preview_data=[],
                status="error"
            )
    
    def process_ofx_file(self, content: bytes, auto_categorize: bool = True,
                         skip_duplicates: bool = True, db: Session = None) -> ImportPreviewResponse:
        """Process OFX file and return import preview."""
        try:
            # Basic OFX parsing (simplified)
            text_content = content.decode('utf-8', errors='ignore')
            
            # Extract transaction data from OFX
            transactions = self._parse_ofx_content(text_content)
            
            # Auto-categorize if requested
            if auto_categorize and db:
                categorization_service = CategorizationService(db)
                for transaction in transactions:
                    category = categorization_service.suggest_category(
                        transaction["description"], float(transaction["amount"])
                    )
                    if category:
                        transaction["category_id"] = category.id
            
            # Create import session
            import_id = str(uuid4())
            self.import_sessions[import_id] = {
                "transactions": transactions,
                "errors": [],
                "status": "preview",
                "created_at": datetime.utcnow(),
                "file_type": "ofx"
            }
            
            return ImportPreviewResponse(
                import_id=import_id,
                total_transactions=len(transactions),
                valid_transactions=len(transactions),
                errors=[],
                preview_data=transactions[:10],
                status="preview"
            )
            
        except Exception as e:
            return ImportPreviewResponse(
                import_id="",
                total_transactions=0,
                valid_transactions=0,
                errors=[f"OFX processing failed: {str(e)}"],
                preview_data=[],
                status="error"
            )
    
    def process_excel_file(self, content: bytes, sheet_name: str = "Sheet1",
                          auto_categorize: bool = True, skip_duplicates: bool = True,
                          db: Session = None) -> ImportPreviewResponse:
        """Process Excel file and return import preview."""
        try:
            # For now, return a placeholder response
            # Excel processing would require additional dependencies like openpyxl
            transactions = []
            
            import_id = str(uuid4())
            self.import_sessions[import_id] = {
                "transactions": transactions,
                "errors": ["Excel processing not yet implemented"],
                "status": "preview",
                "created_at": datetime.utcnow(),
                "file_type": "excel"
            }
            
            return ImportPreviewResponse(
                import_id=import_id,
                total_transactions=0,
                valid_transactions=0,
                errors=["Excel processing not yet implemented"],
                preview_data=[],
                status="preview"
            )
            
        except Exception as e:
            return ImportPreviewResponse(
                import_id="",
                total_transactions=0,
                valid_transactions=0,
                errors=[f"Excel processing failed: {str(e)}"],
                preview_data=[],
                status="error"
            )
    
    def confirm_import(self, import_id: str, db: Session) -> Optional[ImportResultResponse]:
        """Confirm and execute a previewed import operation."""
        if import_id not in self.import_sessions:
            return None
        
        session = self.import_sessions[import_id]
        if session["status"] != "preview":
            return None
        
        try:
            # Import transactions to database
            imported_count = 0
            errors = []
            
            for transaction_data in session["transactions"]:
                try:
                    # Create transaction
                    transaction = Transaction(**transaction_data)
                    db.add(transaction)
                    imported_count += 1
                except Exception as e:
                    errors.append(f"Transaction import failed: {str(e)}")
            
            db.commit()
            
            # Update session status
            session["status"] = "completed"
            session["imported_count"] = imported_count
            session["import_errors"] = errors
            
            return ImportResultResponse(
                import_id=import_id,
                status="completed",
                imported_count=imported_count,
                errors=errors,
                completed_at=datetime.utcnow()
            )
            
        except Exception as e:
            db.rollback()
            session["status"] = "failed"
            session["error"] = str(e)
            
            return ImportResultResponse(
                import_id=import_id,
                status="failed",
                imported_count=0,
                errors=[f"Import failed: {str(e)}"],
                completed_at=datetime.utcnow()
            )
    
    def get_import_preview(self, import_id: str, db: Session) -> Optional[ImportPreviewResponse]:
        """Get import preview for a specific import operation."""
        if import_id not in self.import_sessions:
            return None
        
        session = self.import_sessions[import_id]
        
        return ImportPreviewResponse(
            import_id=import_id,
            total_transactions=len(session["transactions"]),
            valid_transactions=len(session["transactions"]),
            errors=session.get("errors", []),
            preview_data=session["transactions"][:10],
            status=session["status"]
        )
    
    def get_import_history(self, limit: int = 50, offset: int = 0, db: Session = None) -> List[ImportHistoryResponse]:
        """Get import operation history."""
        # Return recent import sessions
        sessions = list(self.import_sessions.values())
        sessions.sort(key=lambda x: x["created_at"], reverse=True)
        
        history = []
        for session in sessions[offset:offset + limit]:
            history.append(ImportHistoryResponse(
                import_id=session.get("import_id", ""),
                file_type=session["file_type"],
                status=session["status"],
                total_transactions=len(session["transactions"]),
                imported_count=session.get("imported_count", 0),
                created_at=session["created_at"],
                completed_at=session.get("completed_at")
            ))
        
        return history
    
    def validate_import_file(self, content: bytes, filename: str, db: Session) -> ValidationResultResponse:
        """Validate import file without processing."""
        errors = []
        warnings = []
        
        try:
            if filename.lower().endswith('.csv'):
                # Validate CSV format
                text_content = content.decode('utf-8')
                csv_reader = csv.DictReader(io.StringIO(text_content))
                
                if not csv_reader.fieldnames:
                    errors.append("No headers found in CSV file")
                else:
                    required_fields = ["date", "amount", "description"]
                    missing_fields = [field for field in required_fields if field not in csv_reader.fieldnames]
                    if missing_fields:
                        errors.append(f"Missing required fields: {', '.join(missing_fields)}")
                    
                    # Check first few rows for data quality
                    row_count = 0
                    for row in csv_reader:
                        row_count += 1
                        if row_count > 5:  # Check first 5 rows
                            break
                        
                        # Validate date
                        try:
                            datetime.strptime(row.get("date", ""), "%Y-%m-%d")
                        except ValueError:
                            warnings.append(f"Row {row_count}: Invalid date format")
                        
                        # Validate amount
                        try:
                            float(row.get("amount", ""))
                        except ValueError:
                            warnings.append(f"Row {row_count}: Invalid amount format")
                    
                    if row_count == 0:
                        errors.append("No data rows found in CSV file")
            
            elif filename.lower().endswith(('.ofx', '.qfx')):
                # Basic OFX validation
                text_content = content.decode('utf-8', errors='ignore')
                if "<OFX>" not in text_content:
                    errors.append("Invalid OFX file format")
                if "<STMTTRN>" not in text_content:
                    warnings.append("No transaction data found in OFX file")
            
            elif filename.lower().endswith(('.xlsx', '.xls')):
                # Excel validation
                if len(content) < 100:  # Basic size check
                    errors.append("File appears to be too small for Excel format")
            
            else:
                errors.append("Unsupported file format")
                
        except Exception as e:
            errors.append(f"File validation failed: {str(e)}")
        
        return ValidationResultResponse(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            filename=filename,
            file_size=len(content)
        )
    
    def detect_duplicates(self, content: bytes, filename: str, threshold: float, db: Session) -> DuplicateDetectionResponse:
        """Detect potential duplicate transactions in import file."""
        duplicates = []
        
        try:
            if filename.lower().endswith('.csv'):
                text_content = content.decode('utf-8')
                csv_reader = csv.DictReader(io.StringIO(text_content))
                
                transactions = []
                for row in csv_reader:
                    transaction = self._parse_csv_row(row, 0)
                    if transaction:
                        transactions.append(transaction)
                
                # Simple duplicate detection based on amount and description
                for i, t1 in enumerate(transactions):
                    for j, t2 in enumerate(transactions[i+1:], i+1):
                        if (abs(t1["amount"] - t2["amount"]) < 0.01 and
                            t1["description"].lower() == t2["description"].lower()):
                            duplicates.append({
                                "transaction1": {"row": i+2, "data": t1},
                                "transaction2": {"row": j+2, "data": t2},
                                "similarity_score": 1.0
                            })
            
        except Exception as e:
            duplicates = [{"error": str(e)}]
        
        return DuplicateDetectionResponse(
            duplicates_found=len(duplicates),
            duplicate_groups=duplicates,
            threshold=threshold
        )
    
    def cancel_import(self, import_id: str, db: Session) -> bool:
        """Cancel a pending import operation."""
        if import_id in self.import_sessions:
            del self.import_sessions[import_id]
            return True
        return False
    
    def get_import_status(self, import_id: str, db: Session) -> Optional[Dict[str, Any]]:
        """Get status of an import operation."""
        if import_id not in self.import_sessions:
            return None
        
        session = self.import_sessions[import_id]
        return {
            "import_id": import_id,
            "status": session["status"],
            "file_type": session["file_type"],
            "total_transactions": len(session["transactions"]),
            "imported_count": session.get("imported_count", 0),
            "created_at": session["created_at"].isoformat(),
            "completed_at": session.get("completed_at", "").isoformat() if session.get("completed_at") else None,
            "errors": session.get("errors", [])
        }
    
    def _parse_csv_row(self, row: Dict[str, str], row_num: int) -> Optional[Dict[str, Any]]:
        """Parse a CSV row into transaction data."""
        try:
            # Parse date
            date_str = row.get("date", "").strip()
            if not date_str:
                raise ValueError("Date is required")
            
            # Try different date formats
            transaction_date = None
            for date_format in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%m-%d-%Y"]:
                try:
                    transaction_date = datetime.strptime(date_str, date_format).date()
                    break
                except ValueError:
                    continue
            
            if not transaction_date:
                raise ValueError(f"Invalid date format: {date_str}")
            
            # Parse amount
            amount_str = row.get("amount", "").strip()
            if not amount_str:
                raise ValueError("Amount is required")
            
            # Remove currency symbols and commas
            amount_str = amount_str.replace("R$", "").replace("$", "").replace(",", "").strip()
            try:
                amount = Decimal(amount_str)
            except:
                raise ValueError(f"Invalid amount: {amount_str}")
            
            # Get description
            description = row.get("description", "").strip()
            if not description:
                raise ValueError("Description is required")
            
            # Build transaction data
            transaction_data = {
                "date": transaction_date,
                "amount": amount,
                "description": description,
                "category_id": None,  # Will be set by categorization service
                "transaction_type": "EXPENSE" if amount < 0 else "INCOME",
                "currency": "BRL",
                "reference_number": row.get("reference", "").strip() or None,
                "institution_code": row.get("institution", "").strip() or None
            }
            
            return transaction_data
            
        except Exception as e:
            raise ValueError(f"Row {row_num}: {str(e)}")
    
    def _parse_ofx_content(self, content: str) -> List[Dict[str, Any]]:
        """Parse OFX content and extract transactions."""
        transactions = []
        
        # Simple OFX parsing (this is a basic implementation)
        # In production, use a proper OFX parser library
        
        # Look for transaction blocks
        transaction_blocks = content.split("<STMTTRN>")
        
        for block in transaction_blocks[1:]:  # Skip first split (before first transaction)
            try:
                # Extract transaction data
                amount_match = self._extract_ofx_field(block, "TRNAMT")
                date_match = self._extract_ofx_field(block, "DTPOSTED")
                memo_match = self._extract_ofx_field(block, "MEMO")
                
                if amount_match and date_match:
                    # Parse amount
                    amount = Decimal(amount_match)
                    
                    # Parse date (OFX format: YYYYMMDDHHMMSS)
                    date_str = date_match[:8]  # Take YYYYMMDD part
                    transaction_date = datetime.strptime(date_str, "%Y%m%d").date()
                    
                    # Build transaction
                    transaction = {
                        "date": transaction_date,
                        "amount": amount,
                        "description": memo_match or "OFX Transaction",
                        "category_id": None,
                        "transaction_type": "EXPENSE" if amount < 0 else "INCOME",
                        "currency": "BRL",
                        "reference_number": None,
                        "institution_code": None
                    }
                    
                    transactions.append(transaction)
                    
            except Exception as e:
                # Skip invalid transactions
                continue
        
        return transactions
    
    def _extract_ofx_field(self, block: str, field_name: str) -> Optional[str]:
        """Extract field value from OFX block."""
        start_tag = f"<{field_name}>"
        end_tag = f"</{field_name}>"
        
        start_pos = block.find(start_tag)
        if start_pos == -1:
            return None
        
        start_pos += len(start_tag)
        end_pos = block.find(end_tag, start_pos)
        
        if end_pos == -1:
            return None
        
        return block[start_pos:end_pos].strip()
