import { api } from './api';

// Category Types
export interface Category {
  id: string;
  name: string;
  description: string;
  level: number;
  parent_id?: string;
  children?: Category[];
  is_active: boolean;
  color?: string;
  icon?: string;
  created_at: string;
  updated_at: string;
}

export interface CategoryCreate {
  name: string;
  description: string;
  level: number;
  parent_id?: string;
  is_active?: boolean;
  color?: string;
  icon?: string;
}

export interface CategoryUpdate {
  name?: string;
  description?: string;
  level?: number;
  parent_id?: string;
  is_active?: boolean;
  color?: string;
  icon?: string;
}

export interface CategoryFilters {
  level?: number;
  parent_id?: string;
  is_active?: boolean;
  search?: string;
}

// Category Service
export const categoryService = {
  // Get all categories
  getCategories: async (filters: CategoryFilters = {}): Promise<Category[]> => {
    return api.get<Category[]>('/api/v1/categories', filters);
  },

  // Get category by ID
  getCategory: async (id: string): Promise<Category> => {
    return api.get<Category>(`/api/v1/categories/${id}`);
  },

  // Create new category
  createCategory: async (category: CategoryCreate): Promise<Category> => {
    return api.post<Category>('/api/v1/categories', category);
  },

  // Update category
  updateCategory: async (id: string, category: CategoryUpdate): Promise<Category> => {
    return api.put<Category>(`/api/v1/categories/${id}`, category);
  },

  // Delete category
  deleteCategory: async (id: string): Promise<void> => {
    return api.delete<void>(`/api/v1/categories/${id}`);
  },

  // Get category hierarchy
  getCategoryHierarchy: async (): Promise<Category[]> => {
    return api.get<Category[]>('/api/v1/categories/hierarchy');
  },

  // Get categories by level
  getCategoriesByLevel: async (level: number): Promise<Category[]> => {
    return api.get<Category[]>(`/api/v1/categories/level/${level}`);
  },

  // Get subcategories
  getSubcategories: async (parentId: string): Promise<Category[]> => {
    return api.get<Category[]>(`/api/v1/categories/${parentId}/children`);
  },

  // Bulk create categories
  bulkCreateCategories: async (categories: CategoryCreate[]): Promise<Category[]> => {
    return api.post<Category[]>('/api/v1/categories/bulk', { categories });
  },

  // Bulk delete categories
  bulkDeleteCategories: async (ids: string[]): Promise<void> => {
    return api.delete<void>('/api/v1/categories/bulk');
  },
};
