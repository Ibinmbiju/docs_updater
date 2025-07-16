import axios, { AxiosResponse } from 'axios';
import {
  Document,
  DocumentSection,
  Suggestion,
  LoadDocumentRequest,
  LoadDocumentResponse,
  GenerateSuggestionsRequest,
  SuggestionBatchResponse,
  SearchRequest,
  SearchResponse,
  UpdateSuggestionRequest,
  DiffResponse,
  SuggestionFilters,
  DocumentType,
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || '/api';

console.log('API DEBUG: API_BASE_URL =', API_BASE_URL);
console.log('API DEBUG: Environment:', process.env.NODE_ENV);

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for debugging
apiClient.interceptors.request.use(
  (config) => {
    const fullUrl = `${config.baseURL || ''}${config.url || ''}`;
    console.log('API DEBUG: Making request to:', fullUrl);
    console.log('API DEBUG: Request config:', config);
    return config;
  },
  (error) => {
    console.error('API DEBUG: Request error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      message: error.response?.data?.detail || error.message,
    });
    
    const errorMessage = error.response?.data?.detail || error.message || 'Unknown API error';
    throw new Error(errorMessage);
  }
);

export class ApiService {
  // Health check
  async healthCheck(): Promise<{ status: string; app: string; version: string }> {
    const response = await apiClient.get('/health');
    return response.data;
  }

  // Document endpoints
  async getDocuments(): Promise<Document[]> {
    const response: AxiosResponse<Document[]> = await apiClient.get('/docs/documents');
    return response.data;
  }

  async getDocument(id: string): Promise<Document> {
    const response: AxiosResponse<Document> = await apiClient.get(`/docs/documents/${id}`);
    return response.data;
  }

  async getDocumentSections(id: string, sectionType?: DocumentType): Promise<DocumentSection[]> {
    const params = sectionType ? { section_type: sectionType } : {};
    const response: AxiosResponse<DocumentSection[]> = await apiClient.get(
      `/docs/documents/${id}/sections`,
      { params }
    );
    return response.data;
  }

  async getSection(id: string): Promise<DocumentSection> {
    const response: AxiosResponse<DocumentSection> = await apiClient.get(`/docs/sections/${id}`);
    return response.data;
  }

  async searchSections(request: SearchRequest): Promise<SearchResponse> {
    const response: AxiosResponse<SearchResponse> = await apiClient.post('/docs/search', request);
    return response.data;
  }

  async listSections(sectionType?: DocumentType, limit: number = 20): Promise<DocumentSection[]> {
    const params: any = { limit };
    if (sectionType) params.section_type = sectionType;
    
    const response: AxiosResponse<DocumentSection[]> = await apiClient.get('/docs/sections', { params });
    return response.data;
  }

  async getCodeSections(): Promise<DocumentSection[]> {
    const response: AxiosResponse<DocumentSection[]> = await apiClient.get('/docs/sections/code');
    return response.data;
  }

  // Suggestion endpoints
  async generateSuggestions(request: GenerateSuggestionsRequest): Promise<SuggestionBatchResponse> {
    const response: AxiosResponse<SuggestionBatchResponse> = await apiClient.post(
      '/suggestions/generate',
      request
    );
    return response.data;
  }

  async getSuggestions(filters?: SuggestionFilters): Promise<Suggestion[]> {
    const params = filters || {};
    const response: AxiosResponse<Suggestion[]> = await apiClient.get('/suggestions/', { params });
    return response.data;
  }

  async getSuggestion(id: string): Promise<Suggestion> {
    const response: AxiosResponse<Suggestion> = await apiClient.get(`/suggestions/${id}`);
    return response.data;
  }

  async updateSuggestionStatus(id: string, request: UpdateSuggestionRequest): Promise<Suggestion> {
    const response: AxiosResponse<Suggestion> = await apiClient.put(`/suggestions/${id}`, request);
    return response.data;
  }

  async approveSuggestion(id: string): Promise<{ message: string; suggestion_id: string; status: string }> {
    const response = await apiClient.post(`/suggestions/${id}/approve`);
    return response.data;
  }

  async rejectSuggestion(id: string): Promise<{ message: string; suggestion_id: string; status: string }> {
    const response = await apiClient.post(`/suggestions/${id}/reject`);
    return response.data;
  }

  async getSuggestionDiff(id: string): Promise<DiffResponse> {
    const response: AxiosResponse<DiffResponse> = await apiClient.get(`/suggestions/${id}/diff`);
    return response.data;
  }

  async deleteSuggestion(id: string): Promise<{ message: string; suggestion_id: string }> {
    const response = await apiClient.delete(`/suggestions/${id}`);
    return response.data;
  }
}

// Export singleton instance
export const apiService = new ApiService();