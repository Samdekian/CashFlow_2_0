"""
Import and export related Pydantic schemas for the CashFlow Monitor API.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID


class ImportPreviewResponse(BaseModel):
    """Schema for import preview response."""
    import_id: str = Field(..., description="Import operation unique identifier")
    total_transactions: int = Field(..., description="Total transactions found in file")
    valid_transactions: int = Field(..., description="Number of valid transactions")
    errors: List[str] = Field(..., description="List of validation errors")
    preview_data: List[Dict[str, Any]] = Field(..., description="Preview of transaction data")
    status: str = Field(..., description="Import status")
    file_type: Optional[str] = Field(None, description="Type of file being imported")
    created_at: Optional[datetime] = Field(None, description="Import creation timestamp")


class ImportResultResponse(BaseModel):
    """Schema for import result response."""
    import_id: str = Field(..., description="Import operation unique identifier")
    status: str = Field(..., description="Import status")
    imported_count: int = Field(..., description="Number of transactions imported")
    errors: List[str] = Field(..., description="List of import errors")
    completed_at: datetime = Field(..., description="Import completion timestamp")
    file_type: Optional[str] = Field(None, description="Type of file imported")
    total_processing_time: Optional[float] = Field(None, description="Total processing time in seconds")


class ImportHistoryResponse(BaseModel):
    """Schema for import history response."""
    import_id: str = Field(..., description="Import operation unique identifier")
    file_type: str = Field(..., description="Type of file imported")
    status: str = Field(..., description="Import status")
    total_transactions: int = Field(..., description="Total transactions in file")
    imported_count: int = Field(..., description="Number of transactions imported")
    created_at: datetime = Field(..., description="Import creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Import completion timestamp")
    errors: Optional[List[str]] = Field(None, description="List of errors encountered")


class ValidationResultResponse(BaseModel):
    """Schema for file validation response."""
    is_valid: bool = Field(..., description="Whether file is valid")
    errors: List[str] = Field(..., description="List of validation errors")
    warnings: List[str] = Field(..., description="List of validation warnings")
    filename: str = Field(..., description="Name of validated file")
    file_size: int = Field(..., description="File size in bytes")
    supported_format: bool = Field(..., description="Whether file format is supported")
    estimated_transactions: Optional[int] = Field(None, description="Estimated number of transactions")


class DuplicateDetectionResponse(BaseModel):
    """Schema for duplicate detection response."""
    duplicates_found: int = Field(..., description="Number of duplicate groups found")
    duplicate_groups: List[Dict[str, Any]] = Field(..., description="Groups of duplicate transactions")
    threshold: float = Field(..., description="Duplicate detection threshold used")
    detection_method: str = Field("similarity", description="Method used for duplicate detection")
    confidence_scores: List[float] = Field(..., description="Confidence scores for duplicates")


class ExportRequest(BaseModel):
    """Schema for export request."""
    start_date: Optional[date] = Field(None, description="Export start date")
    end_date: Optional[date] = Field(None, description="Export end date")
    category_ids: Optional[List[UUID]] = Field(None, description="Filter by category IDs")
    transaction_types: Optional[List[str]] = Field(None, description="Filter by transaction types")
    min_amount: Optional[Decimal] = Field(None, description="Minimum transaction amount")
    max_amount: Optional[Decimal] = Field(None, description="Maximum transaction amount")
    search_term: Optional[str] = Field(None, description="Search term for transactions")
    sort_by: Optional[str] = Field(None, description="Sort field")
    sort_desc: bool = Field(False, description="Sort in descending order")
    limit: Optional[int] = Field(None, ge=1, le=10000, description="Maximum number of records")
    include_headers: bool = Field(True, description="Include headers in export")
    include_metadata: bool = Field(False, description="Include metadata in export")
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        """Validate that end date is after start date if both are provided."""
        if v and 'start_date' in values and values['start_date']:
            if v <= values['start_date']:
                raise ValueError('End date must be after start date')
        return v
    
    @validator('max_amount')
    def validate_max_amount(cls, v, values):
        """Validate that max amount is greater than min amount if both are provided."""
        if v and 'min_amount' in values and values['min_amount']:
            if v <= values['min_amount']:
                raise ValueError('Max amount must be greater than min amount')
        return v
    
    @validator('transaction_types')
    def validate_transaction_types(cls, v):
        """Validate transaction types if provided."""
        if v:
            valid_types = ["INCOME", "EXPENSE", "TRANSFER", "INVESTMENT"]
            for t_type in v:
                if t_type not in valid_types:
                    raise ValueError(f'Invalid transaction type: {t_type}. Must be one of: {", ".join(valid_types)}')
        return v


class ExportResultResponse(BaseModel):
    """Schema for export result response."""
    export_id: str = Field(..., description="Export unique identifier")
    status: str = Field(..., description="Export status")
    filename: str = Field(..., description="Export filename")
    format: str = Field(..., description="Export format")
    record_count: int = Field(..., description="Number of records exported")
    file_size: int = Field(..., description="File size in bytes")
    download_url: str = Field(..., description="Download URL")
    completed_at: datetime = Field(..., description="Export completion timestamp")
    errors: Optional[List[str]] = Field(None, description="List of export errors")
    notes: Optional[List[str]] = Field(None, description="Additional notes about export")
    expires_at: Optional[datetime] = Field(None, description="Download expiration timestamp")


class FileUploadRequest(BaseModel):
    """Schema for file upload request."""
    filename: str = Field(..., description="Name of file to upload")
    file_size: int = Field(..., ge=1, description="File size in bytes")
    file_type: str = Field(..., description="Type of file (csv, ofx, xlsx)")
    auto_categorize: bool = Field(True, description="Automatically categorize transactions")
    skip_duplicates: bool = Field(True, description="Skip duplicate detection")
    validation_mode: bool = Field(False, description="Only validate file without importing")
    
    @validator('file_type')
    def validate_file_type(cls, v):
        """Validate file type."""
        valid_types = ["csv", "ofx", "qfx", "xlsx", "xls"]
        if v.lower() not in valid_types:
            raise ValueError(f'File type must be one of: {", ".join(valid_types)}')
        return v
    
    @validator('file_size')
    def validate_file_size(cls, v):
        """Validate file size."""
        max_size = 50 * 1024 * 1024  # 50MB
        if v > max_size:
            raise ValueError(f'File size must be less than {max_size / (1024*1024):.0f}MB')
        return v


class ImportConfiguration(BaseModel):
    """Schema for import configuration."""
    auto_categorize: bool = Field(True, description="Automatically categorize transactions")
    skip_duplicates: bool = Field(True, description="Skip duplicate detection")
    duplicate_threshold: float = Field(0.8, ge=0.0, le=1.0, description="Duplicate detection threshold")
    category_mapping: Optional[Dict[str, UUID]] = Field(None, description="Custom category mapping")
    default_category_id: Optional[UUID] = Field(None, description="Default category for uncategorized transactions")
    date_format: Optional[str] = Field(None, description="Custom date format")
    currency: str = Field("BRL", description="Default currency for transactions")
    timezone: str = Field("America/Sao_Paulo", description="Default timezone")
    
    @validator('duplicate_threshold')
    def validate_threshold(cls, v):
        """Validate duplicate threshold."""
        if v < 0 or v > 1:
            raise ValueError('Duplicate threshold must be between 0 and 1')
        return v


class ExportConfiguration(BaseModel):
    """Schema for export configuration."""
    format: str = Field("csv", description="Export format")
    include_headers: bool = Field(True, description="Include headers in export")
    include_metadata: bool = Field(False, description="Include metadata in export")
    date_format: str = Field("%Y-%m-%d", description="Date format for export")
    number_format: str = Field("decimal", description="Number format (decimal, currency)")
    encoding: str = Field("utf-8", description="File encoding")
    delimiter: str = Field(",", description="CSV delimiter")
    quote_char: str = Field('"', description="CSV quote character")
    
    @validator('format')
    def validate_format(cls, v):
        """Validate export format."""
        valid_formats = ["csv", "json", "excel", "pdf"]
        if v not in valid_formats:
            raise ValueError(f'Export format must be one of: {", ".join(valid_formats)}')
        return v


class ImportProgressResponse(BaseModel):
    """Schema for import progress response."""
    import_id: str = Field(..., description="Import operation unique identifier")
    status: str = Field(..., description="Current import status")
    progress_percentage: float = Field(..., ge=0, le=100, description="Progress percentage")
    current_step: str = Field(..., description="Current processing step")
    records_processed: int = Field(..., description="Number of records processed")
    total_records: int = Field(..., description="Total number of records")
    estimated_time_remaining: Optional[float] = Field(None, description="Estimated time remaining in seconds")
    current_errors: List[str] = Field(..., description="Current processing errors")
    last_updated: datetime = Field(..., description="Last progress update timestamp")


class ExportProgressResponse(BaseModel):
    """Schema for export progress response."""
    export_id: str = Field(..., description="Export operation unique identifier")
    status: str = Field(..., description="Current export status")
    progress_percentage: float = Field(..., ge=0, le=100, description="Progress percentage")
    current_step: str = Field(..., description="Current processing step")
    records_processed: int = Field(..., description="Number of records processed")
    total_records: int = Field(..., description="Total number of records")
    estimated_time_remaining: Optional[float] = Field(None, description="Estimated time remaining in seconds")
    last_updated: datetime = Field(..., description="Last progress update timestamp")


class FileValidationRequest(BaseModel):
    """Schema for file validation request."""
    filename: str = Field(..., description="Name of file to validate")
    file_content: str = Field(..., description="File content for validation")
    file_type: str = Field(..., description="Type of file")
    validation_level: str = Field("basic", description="Validation level (basic, strict, custom)")
    custom_rules: Optional[Dict[str, Any]] = Field(None, description="Custom validation rules")
    
    @validator('validation_level')
    def validate_validation_level(cls, v):
        """Validate validation level."""
        valid_levels = ["basic", "strict", "custom"]
        if v not in valid_levels:
            raise ValueError(f'Validation level must be one of: {", ".join(valid_levels)}')
        return v


class DuplicateDetectionRequest(BaseModel):
    """Schema for duplicate detection request."""
    filename: str = Field(..., description="Name of file to check")
    file_content: str = Field(..., description="File content for duplicate detection")
    threshold: float = Field(0.8, ge=0.0, le=1.0, description="Duplicate detection threshold")
    detection_method: str = Field("similarity", description="Detection method")
    include_existing: bool = Field(False, description="Check against existing transactions")
    category_weight: float = Field(0.3, ge=0.0, le=1.0, description="Weight for category matching")
    amount_weight: float = Field(0.4, ge=0.0, le=1.0, description="Weight for amount matching")
    description_weight: float = Field(0.3, ge=0.0, le=1.0, description="Weight for description matching")
    
    @validator('threshold')
    def validate_threshold(cls, v):
        """Validate duplicate threshold."""
        if v < 0 or v > 1:
            raise ValueError('Duplicate threshold must be between 0 and 1')
        return v
    
    @validator('detection_method')
    def validate_detection_method(cls, v):
        """Validate detection method."""
        valid_methods = ["similarity", "exact", "fuzzy", "hybrid"]
        if v not in valid_methods:
            raise ValueError(f'Detection method must be one of: {", ".join(valid_methods)}')
        return v


class ImportTemplateResponse(BaseModel):
    """Schema for import template response."""
    template_id: str = Field(..., description="Template unique identifier")
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    file_type: str = Field(..., description="Supported file type")
    required_fields: List[str] = Field(..., description="Required fields for import")
    optional_fields: List[str] = Field(..., description="Optional fields for import")
    field_mapping: Dict[str, str] = Field(..., description="Field mapping configuration")
    sample_data: List[Dict[str, Any]] = Field(..., description="Sample data for template")
    is_default: bool = Field(False, description="Whether this is the default template")


class ExportTemplateResponse(BaseModel):
    """Schema for export template response."""
    template_id: str = Field(..., description="Template unique identifier")
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    format: str = Field(..., description="Export format")
    fields: List[str] = Field(..., description="Fields included in export")
    sorting: Optional[Dict[str, str]] = Field(None, description="Default sorting configuration")
    filtering: Optional[Dict[str, Any]] = Field(None, description="Default filtering configuration")
    is_default: bool = Field(False, description="Whether this is the default template")


class BulkImportRequest(BaseModel):
    """Schema for bulk import request."""
    files: List[FileUploadRequest] = Field(..., description="List of files to import")
    configuration: ImportConfiguration = Field(..., description="Import configuration")
    priority: str = Field("normal", description="Import priority")
    notify_on_completion: bool = Field(False, description="Send notification on completion")
    
    @validator('files')
    def validate_files(cls, v):
        """Validate files list."""
        if not v:
            raise ValueError('Files list cannot be empty')
        if len(v) > 10:
            raise ValueError('Cannot import more than 10 files at once')
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        """Validate priority level."""
        valid_priorities = ["low", "normal", "high", "urgent"]
        if v not in valid_priorities:
            raise ValueError(f'Priority must be one of: {", ".join(valid_priorities)}')
        return v


class BulkExportRequest(BaseModel):
    """Schema for bulk export request."""
    export_requests: List[ExportRequest] = Field(..., description="List of export requests")
    configuration: ExportConfiguration = Field(..., description="Export configuration")
    priority: str = Field("normal", description="Export priority")
    combine_results: bool = Field(False, description="Combine all exports into single file")
    notify_on_completion: bool = Field(False, description="Send notification on completion")
    
    @validator('export_requests')
    def validate_export_requests(cls, v):
        """Validate export requests list."""
        if not v:
            raise ValueError('Export requests list cannot be empty')
        if len(v) > 5:
            raise ValueError('Cannot export more than 5 requests at once')
        return v
    
    @validator('priority')
    def validate_priority(cls, v):
        """Validate priority level."""
        valid_priorities = ["low", "normal", "high", "urgent"]
        if v not in valid_priorities:
            raise ValueError(f'Priority must be one of: {", ".join(valid_priorities)}')
        return v
