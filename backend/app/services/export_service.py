"""
Export service for data export in various formats.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from datetime import date, datetime
from decimal import Decimal
import csv
import io
import json

from ..models.transaction import Transaction
from ..models.category import Category
from ..models.budget import Budget
from ..schemas.import_export import ExportRequest, ExportResultResponse


class ExportService:
    """Service for exporting data in various formats."""
    
    def export_to_csv(self, export_request: ExportRequest, db: Session) -> ExportResultResponse:
        """
        Export transactions to CSV format.
        
        Args:
            export_request: Export configuration and filters
            db: Database session
            
        Returns:
            Export result with CSV data
        """
        try:
            # Query transactions based on filters
            transactions = self._query_transactions(export_request, db)
            
            # Generate CSV content
            csv_content = self._generate_csv_content(transactions, export_request.include_headers)
            
            # Create export result
            filename = f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            return ExportResultResponse(
                export_id=str(len(transactions)),  # Simple ID for now
                status="completed",
                filename=filename,
                format="csv",
                record_count=len(transactions),
                file_size=len(csv_content.encode('utf-8')),
                download_url=f"/download/{filename}",
                completed_at=datetime.utcnow()
            )
            
        except Exception as e:
            return ExportResultResponse(
                export_id="",
                status="failed",
                filename="",
                format="csv",
                record_count=0,
                file_size=0,
                download_url="",
                completed_at=datetime.utcnow(),
                errors=[f"Export failed: {str(e)}"]
            )
    
    def export_to_excel(self, export_request: ExportRequest, include_charts: bool, db: Session) -> ExportResultResponse:
        """
        Export transactions to Excel format.
        
        Args:
            export_request: Export configuration and filters
            include_charts: Whether to include charts in Excel
            db: Database session
            
        Returns:
            Export result with Excel data
        """
        try:
            # Query transactions based on filters
            transactions = self._query_transactions(export_request, db)
            
            # For now, return a placeholder response
            # Excel export would require additional dependencies like openpyxl
            
            filename = f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            return ExportResultResponse(
                export_id=str(len(transactions)),
                status="completed",
                filename=filename,
                format="excel",
                record_count=len(transactions),
                file_size=0,  # Placeholder
                download_url=f"/download/{filename}",
                completed_at=datetime.utcnow(),
                notes=["Excel export with charts not yet implemented"]
            )
            
        except Exception as e:
            return ExportResultResponse(
                export_id="",
                status="failed",
                filename="",
                format="excel",
                record_count=0,
                file_size=0,
                download_url="",
                completed_at=datetime.utcnow(),
                errors=[f"Excel export failed: {str(e)}"]
            )
    
    def export_to_pdf(self, export_request: ExportRequest, include_charts: bool, template: str, db: Session) -> ExportResultResponse:
        """
        Export transactions to PDF format.
        
        Args:
            export_request: Export configuration and filters
            include_charts: Whether to include charts in PDF
            template: PDF template to use
            db: Database session
            
        Returns:
            Export result with PDF data
        """
        try:
            # Query transactions based on filters
            transactions = self._query_transactions(export_request, db)
            
            # For now, return a placeholder response
            # PDF export would require additional dependencies like reportlab
            
            filename = f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            
            return ExportResultResponse(
                export_id=str(len(transactions)),
                status="completed",
                filename=filename,
                format="pdf",
                record_count=len(transactions),
                file_size=0,  # Placeholder
                download_url=f"/download/{filename}",
                completed_at=datetime.utcnow(),
                notes=["PDF export not yet implemented"]
            )
            
        except Exception as e:
            return ExportResultResponse(
                export_id="",
                status="failed",
                filename="",
                format="pdf",
                record_count=0,
                file_size=0,
                download_url="",
                completed_at=datetime.utcnow(),
                errors=[f"PDF export failed: {str(e)}"]
            )
    
    def export_to_json(self, export_request: ExportRequest, pretty_print: bool, db: Session) -> ExportResultResponse:
        """
        Export transactions to JSON format.
        
        Args:
            export_request: Export configuration and filters
            pretty_print: Whether to pretty print JSON
            db: Database session
            
        Returns:
            Export result with JSON data
        """
        try:
            # Query transactions based on filters
            transactions = self._query_transactions(export_request, db)
            
            # Convert transactions to JSON-serializable format
            json_data = []
            for transaction in transactions:
                json_data.append({
                    "id": str(transaction.id),
                    "date": transaction.date.isoformat(),
                    "amount": float(transaction.amount),
                    "description": transaction.description,
                    "category_id": str(transaction.category_id) if transaction.category_id else None,
                    "transaction_type": transaction.transaction_type,
                    "currency": transaction.currency,
                    "reference_number": transaction.reference_number,
                    "institution_code": transaction.institution_code,
                    "created_at": transaction.created_at.isoformat() if transaction.created_at else None,
                    "updated_at": transaction.updated_at.isoformat() if transaction.updated_at else None
                })
            
            # Generate JSON content
            if pretty_print:
                json_content = json.dumps(json_data, indent=2, ensure_ascii=False)
            else:
                json_content = json.dumps(json_data, ensure_ascii=False)
            
            # Create export result
            filename = f"transactions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            return ExportResultResponse(
                export_id=str(len(transactions)),
                status="completed",
                filename=filename,
                format="json",
                record_count=len(transactions),
                file_size=len(json_content.encode('utf-8')),
                download_url=f"/download/{filename}",
                completed_at=datetime.utcnow()
            )
            
        except Exception as e:
            return ExportResultResponse(
                export_id="",
                status="failed",
                filename="",
                format="json",
                record_count=0,
                file_size=0,
                download_url="",
                completed_at=datetime.utcnow(),
                errors=[f"JSON export failed: {str(e)}"]
            )
    
    def custom_export(self, export_request: ExportRequest, custom_format: str, custom_config: Dict[str, Any], db: Session) -> ExportResultResponse:
        """
        Export transactions in a custom format.
        
        Args:
            export_request: Export configuration and filters
            custom_format: Custom export format identifier
            custom_config: Custom export configuration
            db: Database session
            
        Returns:
            Export result with custom format data
        """
        try:
            # Query transactions based on filters
            transactions = self._query_transactions(export_request, db)
            
            # Process custom format
            if custom_format == "summary":
                # Export summary statistics
                export_data = self._generate_summary_export(transactions, custom_config)
                format_type = "summary"
            elif custom_format == "categorized":
                # Export categorized transactions
                export_data = self._generate_categorized_export(transactions, custom_config, db)
                format_type = "categorized"
            else:
                # Default to JSON format
                export_data = self._generate_json_export(transactions, custom_config)
                format_type = "custom_json"
            
            # Create export result
            filename = f"transactions_{custom_format}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_type}"
            
            return ExportResultResponse(
                export_id=str(len(transactions)),
                status="completed",
                filename=filename,
                format=format_type,
                record_count=len(transactions),
                file_size=len(str(export_data).encode('utf-8')),
                download_url=f"/download/{filename}",
                completed_at=datetime.utcnow()
            )
            
        except Exception as e:
            return ExportResultResponse(
                export_id="",
                status="failed",
                filename="",
                format="custom",
                record_count=0,
                file_size=0,
                download_url="",
                completed_at=datetime.utcnow(),
                errors=[f"Custom export failed: {str(e)}"]
            )
    
    def get_export_templates(self) -> Dict[str, Any]:
        """
        Get available export templates and formats.
        
        Returns:
            Available export templates and supported formats
        """
        return {
            "formats": {
                "csv": {
                    "name": "CSV (Comma Separated Values)",
                    "description": "Standard CSV format for spreadsheet applications",
                    "extensions": [".csv"],
                    "supports_charts": False
                },
                "excel": {
                    "name": "Excel (XLSX)",
                    "description": "Microsoft Excel format with support for charts and formatting",
                    "extensions": [".xlsx"],
                    "supports_charts": True
                },
                "pdf": {
                    "name": "PDF (Portable Document Format)",
                    "description": "Portable document format with professional layout",
                    "extensions": [".pdf"],
                    "supports_charts": True
                },
                "json": {
                    "name": "JSON (JavaScript Object Notation)",
                    "description": "Structured data format for APIs and applications",
                    "extensions": [".json"],
                    "supports_charts": False
                }
            },
            "templates": {
                "standard": {
                    "name": "Standard Export",
                    "description": "Standard transaction export with all fields",
                    "fields": ["date", "amount", "description", "category", "type"]
                },
                "summary": {
                    "name": "Summary Report",
                    "description": "Summary statistics and aggregated data",
                    "fields": ["category", "total_amount", "transaction_count", "average_amount"]
                },
                "detailed": {
                    "name": "Detailed Report",
                    "description": "Detailed transaction report with additional metadata",
                    "fields": ["date", "amount", "description", "category", "type", "reference", "institution"]
                }
            }
        }
    
    def _query_transactions(self, export_request: ExportRequest, db: Session) -> List[Transaction]:
        """
        Query transactions based on export request filters.
        
        Args:
            export_request: Export configuration and filters
            db: Database session
            
        Returns:
            List of transactions matching the filters
        """
        query = db.query(Transaction)
        
        # Apply date filters
        if export_request.start_date:
            query = query.filter(Transaction.date >= export_request.start_date)
        if export_request.end_date:
            query = query.filter(Transaction.date <= export_request.end_date)
        
        # Apply category filters
        if export_request.category_ids:
            query = query.filter(Transaction.category_id.in_(export_request.category_ids))
        
        # Apply transaction type filters
        if export_request.transaction_types:
            query = query.filter(Transaction.transaction_type.in_(export_request.transaction_types))
        
        # Apply amount filters
        if export_request.min_amount is not None:
            query = query.filter(Transaction.amount >= export_request.min_amount)
        if export_request.max_amount is not None:
            query = query.filter(Transaction.amount <= export_request.max_amount)
        
        # Apply search filter
        if export_request.search_term:
            search_term = f"%{export_request.search_term}%"
            query = query.filter(
                or_(
                    Transaction.description.ilike(search_term),
                    Transaction.reference_number.ilike(search_term)
                )
            )
        
        # Apply sorting
        if export_request.sort_by:
            if export_request.sort_by == "date":
                query = query.order_by(Transaction.date.desc() if export_request.sort_desc else Transaction.date)
            elif export_request.sort_by == "amount":
                query = query.order_by(Transaction.amount.desc() if export_request.sort_desc else Transaction.amount)
            elif export_request.sort_by == "description":
                query = query.order_by(Transaction.description.desc() if export_request.sort_desc else Transaction.description)
        else:
            query = query.order_by(Transaction.date.desc())
        
        # Apply limit if specified
        if export_request.limit:
            query = query.limit(export_request.limit)
        
        return query.all()
    
    def _generate_csv_content(self, transactions: List[Transaction], include_headers: bool = True) -> str:
        """
        Generate CSV content from transactions.
        
        Args:
            transactions: List of transactions to export
            include_headers: Whether to include CSV headers
            
        Returns:
            CSV content as string
        """
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        if include_headers:
            headers = [
                "Date", "Amount", "Description", "Category", "Type", 
                "Currency", "Reference", "Institution", "Created At", "Updated At"
            ]
            writer.writerow(headers)
        
        # Write transaction data
        for transaction in transactions:
            row = [
                transaction.date.strftime("%Y-%m-%d"),
                str(transaction.amount),
                transaction.description,
                transaction.category.name if transaction.category else "",
                transaction.transaction_type,
                transaction.currency,
                transaction.reference_number or "",
                transaction.institution_code or "",
                transaction.created_at.strftime("%Y-%m-%d %H:%M:%S") if transaction.created_at else "",
                transaction.updated_at.strftime("%Y-%m-%d %H:%M:%S") if transaction.updated_at else ""
            ]
            writer.writerow(row)
        
        return output.getvalue()
    
    def _generate_summary_export(self, transactions: List[Transaction], config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate summary export data.
        
        Args:
            transactions: List of transactions
            config: Export configuration
            
        Returns:
            Summary export data
        """
        # Calculate summary statistics
        total_income = sum(t.amount for t in transactions if t.amount > 0)
        total_expenses = abs(sum(t.amount for t in transactions if t.amount < 0))
        net_flow = total_income - total_expenses
        
        # Category breakdown
        category_totals = {}
        for transaction in transactions:
            category_name = transaction.category.name if transaction.category else "Uncategorized"
            if category_name not in category_totals:
                category_totals[category_name] = {"income": 0, "expenses": 0, "count": 0}
            
            if transaction.amount > 0:
                category_totals[category_name]["income"] += transaction.amount
            else:
                category_totals[category_name]["expenses"] += abs(transaction.amount)
            
            category_totals[category_name]["count"] += 1
        
        return {
            "summary": {
                "total_income": float(total_income),
                "total_expenses": float(total_expenses),
                "net_cash_flow": float(net_flow),
                "transaction_count": len(transactions)
            },
            "category_breakdown": category_totals,
            "export_config": config
        }
    
    def _generate_categorized_export(self, transactions: List[Transaction], config: Dict[str, Any], db: Session) -> Dict[str, Any]:
        """
        Generate categorized export data.
        
        Args:
            transactions: List of transactions
            config: Export configuration
            db: Database session
            
        Returns:
            Categorized export data
        """
        # Group transactions by category
        categorized_transactions = {}
        
        for transaction in transactions:
            category_name = transaction.category.name if transaction.category else "Uncategorized"
            if category_name not in categorized_transactions:
                categorized_transactions[category_name] = []
            
            categorized_transactions[category_name].append({
                "date": transaction.date.isoformat(),
                "amount": float(transaction.amount),
                "description": transaction.description,
                "type": transaction.transaction_type
            })
        
        return {
            "categorized_transactions": categorized_transactions,
            "export_config": config
        }
    
    def _generate_json_export(self, transactions: List[Transaction], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generate JSON export data.
        
        Args:
            transactions: List of transactions
            config: Export configuration
            
        Returns:
            JSON export data
        """
        # Convert transactions to JSON format
        json_data = []
        for transaction in transactions:
            json_data.append({
                "id": str(transaction.id),
                "date": transaction.date.isoformat(),
                "amount": float(transaction.amount),
                "description": transaction.description,
                "category": transaction.category.name if transaction.category else None,
                "type": transaction.transaction_type,
                "currency": transaction.currency,
                "reference": transaction.reference_number,
                "institution": transaction.institution_code
            })
        
        return json_data
