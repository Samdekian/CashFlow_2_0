"""
Import and export endpoints for data management.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy.orm import Session
from uuid import UUID
import io
import csv
import json

from ....database import get_db
from ....schemas.import_export import (
    ImportPreviewResponse,
    ImportResultResponse,
    ImportHistoryResponse,
    ExportRequest,
    ExportResultResponse,
    DuplicateDetectionResponse,
    ValidationResultResponse
)
from ....services.import_service import ImportService
from ....services.export_service import ExportService
from ....core.open_finance_standards import validate_import_data, get_supported_formats

# Create router
router = APIRouter()

# Initialize services
import_service = ImportService()
export_service = ExportService()


@router.post("/import/csv", response_model=ImportPreviewResponse)
async def import_csv_file(
    file: UploadFile = File(..., description="CSV file to import"),
    auto_categorize: bool = Form(True, description="Automatically categorize transactions"),
    skip_duplicates: bool = Form(True, description="Skip duplicate transactions"),
    db: Session = Depends(get_db)
):
    """
    Import transactions from a CSV file with preview.
    
    Args:
        file: CSV file to import
        auto_categorize: Whether to auto-categorize transactions
        skip_duplicates: Whether to skip duplicate detection
        db: Database session
        
    Returns:
        Import preview with validation results and transaction count
        
    Raises:
        HTTPException: If file format is invalid or processing fails
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.csv'):
            raise HTTPException(status_code=400, detail="File must be a CSV file")
        
        # Read file content
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Process CSV import
        preview = import_service.process_csv_file(
            content, 
            auto_categorize=auto_categorize,
            skip_duplicates=skip_duplicates,
            db=db
        )
        
        return preview
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process CSV file: {str(e)}")


@router.post("/import/ofx", response_model=ImportPreviewResponse)
async def import_ofx_file(
    file: UploadFile = File(..., description="OFX file to import"),
    auto_categorize: bool = Form(True, description="Automatically categorize transactions"),
    skip_duplicates: bool = Form(True, description="Skip duplicate transactions"),
    db: Session = Depends(get_db)
):
    """
    Import transactions from an OFX file with preview.
    
    Args:
        file: OFX file to import
        auto_categorize: Whether to auto-categorize transactions
        skip_duplicates: Whether to skip duplicate detection
        db: Database session
        
    Returns:
        Import preview with validation results and transaction count
        
    Raises:
        HTTPException: If file format is invalid or processing fails
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.ofx', '.qfx')):
            raise HTTPException(status_code=400, detail="File must be an OFX or QFX file")
        
        # Read file content
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Process OFX import
        preview = import_service.process_ofx_file(
            content,
            auto_categorize=auto_categorize,
            skip_duplicates=skip_duplicates,
            db=db
        )
        
        return preview
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process OFX file: {str(e)}")


@router.post("/import/excel", response_model=ImportPreviewResponse)
async def import_excel_file(
    file: UploadFile = File(..., description="Excel file to import"),
    sheet_name: str = Form("Sheet1", description="Sheet name to import from"),
    auto_categorize: bool = Form(True, description="Automatically categorize transactions"),
    skip_duplicates: bool = Form(True, description="Skip duplicate transactions"),
    db: Session = Depends(get_db)
):
    """
    Import transactions from an Excel file with preview.
    
    Args:
        file: Excel file to import
        sheet_name: Sheet name to import from
        auto_categorize: Whether to auto-categorize transactions
        skip_duplicates: Whether to skip duplicate detection
        db: Database session
        
    Returns:
        Import preview with validation results and transaction count
        
    Raises:
        HTTPException: If file format is invalid or processing fails
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="File must be an Excel file (.xlsx or .xls)")
        
        # Read file content
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Process Excel import
        preview = import_service.process_excel_file(
            content,
            sheet_name=sheet_name,
            auto_categorize=auto_categorize,
            skip_duplicates=skip_duplicates,
            db=db
        )
        
        return preview
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process Excel file: {str(e)}")


@router.post("/import/confirm/{import_id}", response_model=ImportResultResponse)
async def confirm_import(
    import_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Confirm and execute a previewed import operation.
    
    Args:
        import_id: Import operation identifier
        db: Database session
        
    Returns:
        Import result with success count and any errors
        
    Raises:
        HTTPException: If import ID not found or confirmation fails
    """
    try:
        result = import_service.confirm_import(import_id, db)
        if not result:
            raise HTTPException(status_code=404, detail="Import operation not found")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to confirm import: {str(e)}")


@router.get("/import/preview/{import_id}", response_model=ImportPreviewResponse)
async def get_import_preview(
    import_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get import preview for a specific import operation.
    
    Args:
        import_id: Import operation identifier
        db: Database session
        
    Returns:
        Import preview with validation results
        
    Raises:
        HTTPException: If import ID not found
    """
    try:
        preview = import_service.get_import_preview(import_id, db)
        if not preview:
            raise HTTPException(status_code=404, detail="Import operation not found")
        
        return preview
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve import preview: {str(e)}")


@router.get("/import/history", response_model=List[ImportHistoryResponse])
async def get_import_history(
    limit: int = Query(50, ge=1, le=100, description="Number of records to return"),
    offset: int = Query(0, ge=0, description="Number of records to skip"),
    db: Session = Depends(get_db)
):
    """
    Get import operation history.
    
    Args:
        limit: Maximum number of records to return
        offset: Number of records to skip
        db: Database session
        
    Returns:
        List of import history records
    """
    try:
        history = import_service.get_import_history(limit, offset, db)
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve import history: {str(e)}")


@router.post("/import/validate", response_model=ValidationResultResponse)
async def validate_import_data(
    file: UploadFile = File(..., description="File to validate"),
    db: Session = Depends(get_db)
):
    """
    Validate import file without processing.
    
    Args:
        file: File to validate
        db: Database session
        
    Returns:
        Validation results with any errors or warnings
        
    Raises:
        HTTPException: If validation fails
    """
    try:
        # Read file content
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Validate file
        validation = import_service.validate_import_file(content, file.filename, db)
        return validation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to validate file: {str(e)}")


@router.post("/import/detect-duplicates", response_model=DuplicateDetectionResponse)
async def detect_duplicates(
    file: UploadFile = File(..., description="File to check for duplicates"),
    threshold: float = Form(0.8, ge=0.0, le=1.0, description="Duplicate detection threshold"),
    db: Session = Depends(get_db)
):
    """
    Detect potential duplicate transactions in import file.
    
    Args:
        file: File to check for duplicates
        threshold: Duplicate detection threshold (0.0-1.0)
        db: Database session
        
    Returns:
        Duplicate detection results with potential matches
        
    Raises:
        HTTPException: If duplicate detection fails
    """
    try:
        # Read file content
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="File is empty")
        
        # Detect duplicates
        duplicates = import_service.detect_duplicates(content, file.filename, threshold, db)
        return duplicates
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to detect duplicates: {str(e)}")


@router.post("/export/csv", response_model=ExportResultResponse)
async def export_to_csv(
    export_request: ExportRequest,
    db: Session = Depends(get_db)
):
    """
    Export transactions to CSV format.
    
    Args:
        export_request: Export configuration and filters
        db: Database session
        
    Returns:
        Export result with file download
        
    Raises:
        HTTPException: If export fails
    """
    try:
        result = export_service.export_to_csv(export_request, db)
        if not result:
            raise HTTPException(status_code=500, detail="Export failed")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export to CSV: {str(e)}")


@router.post("/export/excel", response_model=ExportResultResponse)
async def export_to_excel(
    export_request: ExportRequest,
    include_charts: bool = Form(False, description="Include charts in Excel export"),
    db: Session = Depends(get_db)
):
    """
    Export transactions to Excel format.
    
    Args:
        export_request: Export configuration and filters
        include_charts: Whether to include charts in export
        db: Database session
        
    Returns:
        Export result with file download
        
    Raises:
        HTTPException: If export fails
    """
    try:
        result = export_service.export_to_excel(export_request, include_charts, db)
        if not result:
            raise HTTPException(status_code=500, detail="Export failed")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export to Excel: {str(e)}")


@router.post("/export/pdf", response_model=ExportResultResponse)
async def export_to_pdf(
    export_request: ExportRequest,
    include_charts: bool = Form(True, description="Include charts in PDF export"),
    template: str = Form("standard", description="PDF template to use"),
    db: Session = Depends(get_db)
):
    """
    Export transactions to PDF format.
    
    Args:
        export_request: Export configuration and filters
        include_charts: Whether to include charts in export
        template: PDF template to use
        db: Database session
        
    Returns:
        Export result with file download
        
    Raises:
        HTTPException: If export fails
    """
    try:
        result = export_service.export_to_pdf(export_request, include_charts, template, db)
        if not result:
            raise HTTPException(status_code=500, detail="Export failed")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export to PDF: {str(e)}")


@router.post("/export/json", response_model=ExportResultResponse)
async def export_to_json(
    export_request: ExportRequest,
    pretty_print: bool = Form(True, description="Pretty print JSON output"),
    db: Session = Depends(get_db)
):
    """
    Export transactions to JSON format.
    
    Args:
        export_request: Export configuration and filters
        pretty_print: Whether to pretty print JSON
        db: Database session
        
    Returns:
        Export result with JSON data
        
    Raises:
        HTTPException: If export fails
    """
    try:
        result = export_service.export_to_json(export_request, pretty_print, db)
        if not result:
            raise HTTPException(status_code=500, detail="Export failed")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to export to JSON: {str(e)}")


@router.get("/export/templates", response_model=dict)
async def get_export_templates():
    """
    Get available export templates and formats.
    
    Returns:
        Available export templates and supported formats
    """
    try:
        templates = export_service.get_export_templates()
        return templates
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve export templates: {str(e)}")


@router.get("/export/supported-formats", response_model=dict)
async def get_supported_formats():
    """
    Get supported import and export formats.
    
    Returns:
        Supported file formats for import and export
    """
    try:
        formats = get_supported_formats()
        return formats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve supported formats: {str(e)}")


@router.post("/export/custom", response_model=ExportResultResponse)
async def custom_export(
    export_request: ExportRequest,
    custom_format: str = Form(..., description="Custom export format"),
    custom_config: str = Form("{}", description="Custom export configuration (JSON)"),
    db: Session = Depends(get_db)
):
    """
    Export transactions in a custom format.
    
    Args:
        export_request: Export configuration and filters
        custom_format: Custom export format identifier
        custom_config: Custom export configuration
        db: Database session
        
    Returns:
        Export result with custom format data
        
    Raises:
        HTTPException: If custom export fails
    """
    try:
        # Parse custom configuration
        try:
            config = json.loads(custom_config)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid custom configuration JSON")
        
        result = export_service.custom_export(export_request, custom_format, config, db)
        if not result:
            raise HTTPException(status_code=500, detail="Custom export failed")
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to perform custom export: {str(e)}")


@router.delete("/import/{import_id}", status_code=204)
async def cancel_import(
    import_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Cancel a pending import operation.
    
    Args:
        import_id: Import operation identifier
        db: Database session
        
    Raises:
        HTTPException: If import ID not found or cancellation fails
    """
    try:
        success = import_service.cancel_import(import_id, db)
        if not success:
            raise HTTPException(status_code=404, detail="Import operation not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel import: {str(e)}")


@router.get("/import/status/{import_id}", response_model=dict)
async def get_import_status(
    import_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get status of an import operation.
    
    Args:
        import_id: Import operation identifier
        db: Database session
        
    Returns:
        Import operation status
        
    Raises:
        HTTPException: If import ID not found
    """
    try:
        status = import_service.get_import_status(import_id, db)
        if not status:
            raise HTTPException(status_code=404, detail="Import operation not found")
        
        return status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve import status: {str(e)}")
