// Backend Data Types
export type DocumentType = "markdown" | "text" | "code";
export type SuggestionStatus = "pending" | "approved" | "rejected" | "merged";
export type SuggestionType = "update" | "delete" | "add" | "move";

// Document Models
export interface DocumentSection {
  id: string;
  title: string;
  content: string;
  file_path: string;
  line_start: number;
  line_end: number;
  section_type: DocumentType;
  metadata: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface Document {
  id: string;
  name: string;
  file_path: string;
  content: string;
  sections_count: number;
  version: string;
  created_at: string;
  updated_at: string;
  metadata: Record<string, any>;
}

// Suggestion Models
export interface DiffHunk {
  old_start: number;
  old_count: number;
  new_start: number;
  new_count: number;
  old_lines: string[];
  new_lines: string[];
  context_before: string[];
  context_after: string[];
}

export interface Suggestion {
  id: string;
  document_id: string;
  section_id: string;
  title: string;
  description: string;
  suggestion_type: SuggestionType;
  status: SuggestionStatus;
  confidence_score: number;
  diff_hunks: DiffHunk[];
  original_content: string;
  suggested_content: string;
  created_at: string;
  updated_at: string;
  created_by: string;
  reviewed_by: string | null;
  reviewed_at: string | null;
  reasoning: string;
  affected_sections: string[];
}

// API Request/Response Types
export interface LoadDocumentRequest {
  file_path: string;
}

export interface LoadDocumentResponse {
  message: string;
  document_id?: string;
  document_ids?: string[];
  sections_count?: number;
  total_sections?: number;
}

export interface GenerateSuggestionsRequest {
  query: string;
  limit?: number;
  context?: string;
  target_sections?: string[];
}

export interface SuggestionBatchResponse {
  query: string;
  suggestions: Suggestion[];
  total_suggestions: number;
  message?: string;
}

export interface SearchRequest {
  query: string;
  limit?: number;
}

export interface SearchResponse {
  query: string;
  results: DocumentSection[];
  total_results: number;
}

export interface UpdateSuggestionRequest {
  status?: SuggestionStatus;
  reviewed_by?: string;
}

export interface DiffStats {
  additions: number;
  deletions: number;
  changes: number;
}

export interface DiffResponse {
  suggestion_id: string;
  diff_hunks: DiffHunk[];
  stats: DiffStats;
  original_content: string;
  suggested_content: string;
}

export interface SuggestionStats {
  total_suggestions: number;
  by_status: Record<string, number>;
  by_type: Record<string, number>;
  average_confidence: number;
}

// UI State Types
export interface SuggestionFilters {
  status?: SuggestionStatus;
  suggestion_type?: SuggestionType;
  limit?: number;
}

export interface AppError {
  message: string;
  code?: string;
  details?: any;
}