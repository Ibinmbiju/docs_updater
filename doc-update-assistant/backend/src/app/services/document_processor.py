# Document processing service
"""Document processing service for OpenAI Agents SDK docs."""

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from openai import OpenAI
from ..config import settings
import os
import pickle
import hashlib
from typing import Any, Dict, List, Optional


from ..models.document import Document, DocumentSection, DocumentType
from ..utils.exceptions import DocumentProcessingError


class DocumentProcessor:
    """Handles document loading, parsing, and indexing for OpenAI Agents SDK docs. Provides search and sectioning utilities."""
    
    def __init__(self) -> None:
        """Initialize the document processor and in-memory stores."""
        self.documents: Dict[str, Document] = {}
        self.sections: Dict[str, DocumentSection] = {}
        self.embeddings: Dict[str, np.ndarray] = {}  # section_id -> embedding vector
        
        # Initialize OpenAI client only if API key is available
        api_key = settings.openai_api_key or os.getenv("OPENAI_API_KEY")
        if api_key:
            try:
                self.embeddings_model = OpenAI(api_key=api_key, timeout=30)
                print("[DEBUG] OpenAI client initialized successfully")
            except Exception as e:
                print(f"[DEBUG] Failed to initialize OpenAI client: {e}")
                self.embeddings_model = None
        else:
            print("[DEBUG] No OpenAI API key found, embeddings will be disabled")
            self.embeddings_model = None
        
        # Fast embedding search optimizations
        self.embedding_matrix: Optional[np.ndarray] = None
        self.section_ids_list: List[str] = []
        self.query_embedding_cache: Dict[str, np.ndarray] = {}  # Cache for query embeddings
        self._embedding_matrix_dirty = True
        
        # Load existing embeddings on initialization
        print("[DocumentProcessor] Loading existing embeddings from pickle file...")
        self.load_embeddings()
        
    def save_embeddings(self, path: str = "data/embeddings.pkl") -> None:
        """Persist embeddings to disk as a pickle file."""
        with open(path, "wb") as f:
            # Save as {section_id: embedding.tolist()}
            pickle.dump({k: v.tolist() for k, v in self.embeddings.items()}, f)

    def load_embeddings(self, path: str = "data/embeddings.pkl") -> None:
        """Load embeddings from disk if available."""
        try:
            with open(path, "rb") as f:
                loaded = pickle.load(f)
                self.embeddings = {k: np.array(v) for k, v in loaded.items()}
        except Exception as e:
            print(f"[Embedding] No existing embeddings loaded: {e}")

    async def load_documents_from_json_file(self, json_file_path: str) -> Document | None:
        """Load a single JSON document in the OpenAI Agents SDK format and process it into sections."""
        file_path = self._ensure_path(json_file_path)
        if not file_path.exists():
            print(f"[DocumentProcessor] File not found: {file_path}")
            raise DocumentProcessingError(f"File not found: {file_path}")
        data = self._load_json_file(file_path)
        markdown_content = data.get('markdown', '')
        metadata = data.get('metadata', {})
        if not markdown_content:
            print(f"[DocumentProcessor] No markdown content found in JSON file: {file_path}")
            raise DocumentProcessingError(f"No markdown content found in JSON file: {file_path}")
        document = await self._process_json_document(file_path, markdown_content, metadata)
        if document:
            self._store_document(document)
        else:
            print(f"[DocumentProcessor] Failed to process document: {file_path}")
        return document

    def _ensure_path(self, path_input: str) -> Path:
        """Ensure the input is a Path object."""
        return Path(path_input) if not isinstance(path_input, Path) else path_input

    def _load_json_file(self, file_path: Path) -> dict[str, Any]:
        """Load and parse a JSON file from disk."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[DocumentProcessor] Exception loading JSON file {file_path}: {str(e)}")
            raise DocumentProcessingError(f"Failed to load JSON file: {str(e)}")

    def _store_document(self, document: Document) -> None:
        """Store a document and its sections in memory for fast access."""
        self.documents[document.id] = document
        for section in document.sections:
            self.sections[section.id] = section
    
    async def load_documents_from_directory(self, docs_path: str) -> list[Document]:
        """Load all JSON documents from a directory and process them."""
        docs_path_path = self._ensure_path(docs_path)
        if not docs_path_path.exists():
            print(f"[DocumentProcessor] Directory not found: {docs_path_path}")
            raise DocumentProcessingError(f"Directory not found: {docs_path_path}")
        
        
        documents = []
        for file_path in docs_path_path.rglob("*.json"):
            document = await self._load_single_document(file_path)
            if document:
                documents.append(document)
        
        if not documents:
            print(f"[DocumentProcessor] No valid documents loaded from directory: {docs_path_path}")
        else:
            print(f"[DocumentProcessor] Loaded {len(documents)} documents")
            
            # Only generate embeddings for sections that don't have them
            sections_needing_embeddings = [
                section for section in self.sections.values()
                if section.id not in self.embeddings and section.content and section.content.strip()
            ]
            
            if sections_needing_embeddings:
                print(f"[DocumentProcessor] Need to generate embeddings for {len(sections_needing_embeddings)} new sections")
                await self.generate_section_embeddings()
                self.save_embeddings()
            else:
                print("[DocumentProcessor] All sections already have embeddings, skipping generation")
        
        return documents

    async def _load_single_document(self, file_path: Path) -> Document | None:
        """Load a single document from a file path, handling errors gracefully."""
        try:
            return await self.load_documents_from_json_file(str(file_path))
        except Exception as e:
            print(f"[DocumentProcessor] Error processing {file_path}: {str(e)}")
            return None
    
    async def _process_json_document(
        self, 
        file_path: Path, 
        markdown_content: str, 
        metadata: dict[str, Any]
    ) -> Document | None:
        """Process a JSON document with markdown content into a Document object with sections."""
        try:
            doc_id = self._generate_doc_id(str(file_path))
            sections = self._parse_markdown_sections(markdown_content, str(file_path))
            title = metadata.get('title', file_path.stem)
            document = Document(
                id=doc_id,
                name=title,
                file_path=str(file_path),
                content=markdown_content,
                sections=sections,
                metadata=metadata,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            return document
        except Exception as e:
            print(f"[DocumentProcessor] Error processing document {file_path}: {str(e)}")
            return None
    
    def _parse_markdown_sections(self, content: str, file_path: str) -> list[DocumentSection]:
        """Parse markdown content into logical sections based on headers."""
        lines = content.split('\n')
        sections = self._parse_sections_from_lines(lines, file_path)
        if not sections:
            sections.append(self._create_default_section(content, file_path))
        return sections

    def _parse_sections_from_lines(self, lines: list[str], file_path: str) -> list[DocumentSection]:
        """Parse sections from lines of content, splitting on markdown headers."""
        sections = []
        current_section = None
        section_content = []
        line_start = 0
        header_level = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('#'):
                if current_section:
                    sections.append(self._create_section(
                        current_section, 
                        '\n'.join(section_content),
                        file_path,
                        line_start,
                        i - 1,
                        header_level
                    ))
                header_match = re.match(r'^(#+)\s*(.+)', line.strip())
                if header_match:
                    header_level = len(header_match.group(1))
                    current_section = header_match.group(2).strip()
                    section_content = []
                    line_start = i
            else:
                section_content.append(line)
        if current_section:
            sections.append(self._create_section(
                current_section, 
                '\n'.join(section_content),
                file_path,
                line_start,
                len(lines) - 1,
                header_level
            ))
        return sections

    def _create_default_section(self, content: str, file_path: str) -> DocumentSection:
        """Create a default section when no headers are found in the markdown."""
        return self._create_section(
            "Main Content",
            content,
            file_path,
            0,
            len(content.split('\n')) - 1,
            1
        )
    
    def _create_section(
        self, 
        title: str, 
        content: str, 
        file_path: str, 
        line_start: int, 
        line_end: int, 
        header_level: int = 1
    ) -> DocumentSection:
        """Create a DocumentSection object with metadata and content analysis."""
        section_id = self._generate_section_id(title, file_path, line_start)
        
        # Clean up content
        content = content.strip()
        
        # Determine section type based on content
        section_type = DocumentType.MARKDOWN
        if '```' in content:
            section_type = DocumentType.CODE
        
        return DocumentSection(
            id=section_id,
            title=title,
            content=content,
            file_path=file_path,
            line_start=line_start,
            line_end=line_end,
            section_type=section_type,
            metadata={
                "header_level": header_level,
                "has_code": '```' in content,
                "word_count": len(content.split()),
                "char_count": len(content)
            },
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def _generate_doc_id(self, file_path: str) -> str:
        """Generate a unique document ID based on file path."""
        return hashlib.md5(file_path.encode()).hexdigest()
    
    def _generate_section_id(self, title: str, file_path: str, line_start: int) -> str:
        """Generate a unique section ID based on title, file path, and line start."""
        content = f"{file_path}:{title}:{line_start}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_document_by_id(self, doc_id: str) -> Document | None:
        """Get a document by its unique ID."""
        return self.documents.get(doc_id)
    
    def get_section_by_id(self, section_id: str) -> DocumentSection | None:
        """Get a section by its unique ID."""
        return self.sections.get(section_id)
    
    async def generate_section_embeddings(self, batch_size: int = 50) -> None:
        """Generate and store embeddings for all document sections using optimized batching."""
        # Skip embedding generation if no OpenAI client is available
        if not self.embeddings_model:
            print("[DEBUG] No OpenAI client available, skipping embedding generation")
            return
        
        # Only embed non-empty, valid string contents
        to_embed = [
            (section.id, str(section.content)[:2000])  # Truncate content for faster embedding
            for section in self.sections.values()
            if section.id not in self.embeddings and section.content and isinstance(section.content, str) and section.content.strip()
        ]
        
        if not to_embed:
            print("[DEBUG] No sections to embed")
            return
        
        print(f"[DEBUG] Generating embeddings for {len(to_embed)} sections")
        
        for i in range(0, len(to_embed), batch_size):
            batch = to_embed[i:i+batch_size]
            ids, texts = zip(*batch)
            try:
                response = self.embeddings_model.embeddings.create(
                    input=list(texts),
                    model="text-embedding-ada-002",
                    timeout=20  # Reduced timeout for faster processing
                )
                for idx, emb in enumerate(response.data):
                    self.embeddings[ids[idx]] = np.array(emb.embedding)
                
                print(f"[DEBUG] Embedded batch {i//batch_size + 1}/{(len(to_embed) - 1)//batch_size + 1}")
                
            except Exception as e:
                print(f"[Embedding] Error embedding batch {i}-{i+batch_size}: {e}")
                # Don't raise on embedding errors, just skip embeddings
                print("[DEBUG] Skipping embedding generation due to API error")
                return
        
        # Mark matrix as dirty after adding new embeddings
        self._embedding_matrix_dirty = True

    async def _embed_text(self, text: str) -> np.ndarray | None:
        """Get embedding for a text using OpenAI API with optimization."""
        if not self.embeddings_model:
            print("[DEBUG] No OpenAI client available for text embedding")
            return None
            
        try:
            # Truncate text for faster embedding
            truncated_text = text[:1000] if len(text) > 1000 else text
            
            response = self.embeddings_model.embeddings.create(
                input=truncated_text,
                model="text-embedding-ada-002",
                timeout=15  # Reduced timeout for faster processing
            )
            return np.array(response.data[0].embedding)
        except Exception as e:
            print(f"[Embedding] Error embedding text: {e}")
            return None

    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        if np.linalg.norm(a) == 0 or np.linalg.norm(b) == 0:
            return 0.0
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    
    async def _get_cached_query_embedding(self, query: str) -> np.ndarray | None:
        """Get query embedding with caching for speed."""
        query_hash = hashlib.md5(query.encode()).hexdigest()
        
        if query_hash in self.query_embedding_cache:
            return self.query_embedding_cache[query_hash]
        
        embedding = await self._embed_text(query)
        if embedding is not None:
            # Cache the embedding for future use
            self.query_embedding_cache[query_hash] = embedding
            # Keep cache size manageable
            if len(self.query_embedding_cache) > 100:
                # Remove oldest entries
                oldest_keys = list(self.query_embedding_cache.keys())[:50]
                for key in oldest_keys:
                    del self.query_embedding_cache[key]
        
        return embedding
    
    def _build_embedding_matrix(self) -> None:
        """Build embedding matrix for fast similarity search."""
        if not self.embeddings or not self._embedding_matrix_dirty:
            return
        
        self.section_ids_list = list(self.embeddings.keys())
        embeddings_list = [self.embeddings[section_id] for section_id in self.section_ids_list]
        
        if embeddings_list:
            self.embedding_matrix = np.vstack(embeddings_list)
            # Normalize embeddings for faster cosine similarity
            norms = np.linalg.norm(self.embedding_matrix, axis=1, keepdims=True)
            self.embedding_matrix = self.embedding_matrix / np.maximum(norms, 1e-8)
        else:
            self.embedding_matrix = None
            
        self._embedding_matrix_dirty = False
        print(f"[DEBUG] Built embedding matrix with {len(self.section_ids_list)} sections")
    
    def _fast_embedding_search(self, query_emb: np.ndarray, limit: int) -> list[DocumentSection]:
        """Ultra-fast embedding search using vectorized operations."""
        if self._embedding_matrix_dirty:
            self._build_embedding_matrix()
        
        if self.embedding_matrix is None or len(self.section_ids_list) == 0:
            return []
        
        # Normalize query embedding
        query_norm = np.linalg.norm(query_emb)
        if query_norm == 0:
            return []
        query_emb_normalized = query_emb / query_norm
        
        # Vectorized cosine similarity computation
        similarities = np.dot(self.embedding_matrix, query_emb_normalized)
        
        # Get top k indices
        top_indices = np.argsort(similarities)[::-1][:limit]
        
        # Filter by minimum similarity threshold
        results = []
        for idx in top_indices:
            similarity = similarities[idx]
            if similarity > 0.1:  # Minimum threshold
                section_id = self.section_ids_list[idx]
                section = self.sections.get(section_id)
                if section:
                    results.append(section)
        
        return results

    async def search_sections(self, query: str, limit: int = 10) -> list[DocumentSection]:
        """Ultra-fast embedding-based search with context preservation."""
        if not self.embeddings:
            print("[DEBUG] No embeddings available, using keyword search")
            return self._keyword_search_sections(query, limit)
        
        try:
            # Get query embedding with caching
            query_emb = await self._get_cached_query_embedding(query)
            if query_emb is None:
                print("[DEBUG] Failed to get query embedding, using keyword search")
                return self._keyword_search_sections(query, limit)
            
            # Use fast matrix operations for similarity search
            results = self._fast_embedding_search(query_emb, limit)
            
            if len(results) < limit:
                # Fill remaining slots with keyword search if needed
                keyword_results = self._keyword_search_sections(query, limit - len(results))
                # Add keyword results that aren't already in embedding results
                existing_ids = {section.id for section in results}
                for section in keyword_results:
                    if section.id not in existing_ids:
                        results.append(section)
                        if len(results) >= limit:
                            break
            
            return results[:limit]
            
        except Exception as e:
            print(f"[DEBUG] Embedding search failed: {e}, using keyword search")
            return self._keyword_search_sections(query, limit)

    def _keyword_search_sections(self, query: str, limit: int = 10) -> list[DocumentSection]:
        """Fallback: keyword-based search (original logic)."""
        results = []
        query_lower = query.lower()
        query_terms = query_lower.split()
        for section in self.sections.values():
            score = 0
            title_lower = section.title.lower()
            content_lower = section.content.lower()
            for term in query_terms:
                if term in title_lower:
                    score += 10
                if term in content_lower:
                    score += 1
            if query_lower in title_lower:
                score += 20
            if query_lower in content_lower:
                score += 5
            agents_terms = {
                'agent': 5, 'handoff': 5, 'guardrail': 5, 'tool': 3, 
                'runner': 3, 'instruction': 2, 'function': 2
            }
            for term, bonus in agents_terms.items():
                if term in content_lower:
                    score += bonus
            if score > 0:
                results.append((section, score))
        results.sort(key=lambda x: x[1], reverse=True)
        return [section for section, score in results[:limit]]
    
    def get_sections_by_type(self, section_type: DocumentType) -> list[DocumentSection]:
        """Get all sections of a given type (e.g., code, markdown)."""
        return [
            section for section in self.sections.values() 
            if section.section_type == section_type
        ]
    
    def get_sections_with_code(self) -> list[DocumentSection]:
        """Get all sections that contain code blocks."""
        return [
            section for section in self.sections.values() 
            if '```' in section.content
        ]