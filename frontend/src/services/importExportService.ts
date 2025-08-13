import { api } from './api';

// Import/Export Types
export interface ImportPreview {
  id: string;
  filename: string;
  format: string;
  total_records: number;
  valid_records: number;
  duplicate_records: number;
  invalid_records: number;
  status: 'pending' | 'validated' | 'confirmed' | 'completed' | 'failed';
  created_at: string;
  preview_data: any[];
}

export interface ImportResult {
  import_id: string;
  status: 'success' | 'partial' | 'failed';
  total_imported: number;
  total_failed: number;
  errors: string[];
  created_at: string;
}

export interface ImportHistory {
  id: string;
  filename: string;
  format: string;
  status: string;
  total_records: number;
  imported_records: number;
  created_at: string;
}

export interface ExportRequest {
  format: 'csv' | 'json' | 'excel' | 'pdf';
  filters?: {
    start_date?: string;
    end_date?: string;
    category_id?: string;
    type?: 'income' | 'expense';
  };
  options?: {
    include_headers?: boolean;
    include_charts?: boolean;
    group_by?: string;
  };
}

export interface ExportResult {
  export_id: string;
  status: 'processing' | 'completed' | 'failed';
  download_url?: string;
  created_at: string;
}

export interface SupportedFormat {
  format: string;
  extensions: string[];
  features: string[];
  status?: 'supported' | 'placeholder' | 'deprecated';
}

// Import/Export Service
export const importExportService = {
  // Import file
  importFile: async (file: File, format: string): Promise<ImportPreview> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('format', format);
    
    return api.post<ImportPreview>('/api/v1/import-export/import', formData);
  },

  // Get import preview
  getImportPreview: async (importId: string): Promise<ImportPreview> => {
    return api.get<ImportPreview>(`/api/v1/import-export/import/${importId}/preview`);
  },

  // Confirm import
  confirmImport: async (importId: string): Promise<ImportResult> => {
    return api.post<ImportResult>(`/api/v1/import-export/import/${importId}/confirm`);
  },

  // Get import history
  getImportHistory: async (): Promise<ImportHistory[]> => {
    return api.get<ImportHistory[]>('/api/v1/import-export/import/history');
  },

  // Cancel import
  cancelImport: async (importId: string): Promise<void> => {
    return api.delete<void>(`/api/v1/import-export/import/${importId}`);
  },

  // Get import status
  getImportStatus: async (importId: string): Promise<ImportPreview> => {
    return api.get<ImportPreview>(`/api/v1/import-export/import/${importId}/status`);
  },

  // Validate import file
  validateImportFile: async (file: File, format: string): Promise<{
    is_valid: boolean;
    errors: string[];
    warnings: string[];
    preview_data: any[];
  }> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('format', format);
    
    return api.post('/api/v1/import-export/import/validate', formData);
  },

  // Detect duplicates
  detectDuplicates: async (importId: string): Promise<{
    duplicate_count: number;
    duplicate_records: any[];
    suggested_actions: string[];
  }> => {
    return api.get(`/api/v1/import-export/import/${importId}/duplicates`);
  },

  // Export data
  exportData: async (request: ExportRequest): Promise<ExportResult> => {
    return api.post<ExportResult>('/api/v1/import-export/export', request);
  },

  // Get export status
  getExportStatus: async (exportId: string): Promise<ExportResult> => {
    return api.get<ExportResult>(`/api/v1/import-export/export/${exportId}/status`);
  },

  // Download export
  downloadExport: async (exportId: string): Promise<Blob> => {
    const response = await api.get(`/api/v1/import-export/export/${exportId}/download`);
    return response as Blob;
  },

  // Get supported formats
  getSupportedFormats: async (): Promise<{
    import_formats: SupportedFormat[];
    export_formats: SupportedFormat[];
  }> => {
    return api.get('/api/v1/import-export/formats');
  },

  // Get export templates
  getExportTemplates: async (): Promise<{
    name: string;
    description: string;
    format: string;
    filters: any;
    options: any;
  }[]> => {
    return api.get('/api/v1/import-export/export/templates');
  },

  // Custom export
  customExport: async (request: ExportRequest): Promise<ExportResult> => {
    return api.post<ExportResult>('/api/v1/import-export/export/custom', request);
  },
};
