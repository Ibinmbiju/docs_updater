"""Redis-optimized document processor with ultra-fast embedding search."""

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from openai import OpenAI
from ..config import settings
from ..models.document import Document, DocumentSection, DocumentType
from ..utils.exceptions import DocumentProcessingError
from .redis_embedding_service import RedisEmbeddingService
import logging
import asyncio

logger = logging.getLogger(__name__)


class RedisDocumentProcessor:
    """
    High-performance document processor with Redis-based embedding storage.
    
    Features:
    - Ultra-fast Redis-based embedding storage
    - Concurrent document processing
    - Optimized batch operations
    - Query caching for repeated searches
    - Automatic fallback to keyword search
    """
    
    def __init__(self, redis_url: str = None) -> None:
        """Initialize with Redis embedding service."""
        self.documents: Dict[str, Document] = {}
        self.sections: Dict[str, DocumentSection] = {}
        
        # Initialize OpenAI client
        self.embeddings_model = OpenAI(
            api_key=settings.openai_api_key,
            timeout=30
        )
        
        # Initialize Redis embedding service
        try:
            self.redis_service = RedisEmbeddingService(redis_url)
            # Test the Redis connection
            if hasattr(self.redis_service, 'redis_client') and self.redis_service.redis_client:
                self.redis_service.redis_client.ping()
                logger.info("✅ Redis Document Processor initialized with working Redis connection")
            else:
                raise Exception("Redis client not properly initialized")
        except Exception as e:
            logger.error(f"❌ Redis Document Processor failed to initialize: {e}")
            raise
    
    async def load_documents_from_directory(self, docs_path: str) -> List[Document]:
        """Load all JSON documents from directory with optimized processing."""
        docs_path_obj = Path(docs_path)
        if not docs_path_obj.exists():
            raise DocumentProcessingError(f"Directory not found: {docs_path}")
        
        # Get all JSON files
        json_files = list(docs_path_obj.rglob("*.json"))
        logger.info(f"Found {len(json_files)} JSON files to process")
        
        # Process documents concurrently
        tasks = [self._load_single_document(file_path) for file_path in json_files]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter successful results
        documents = []
        for result in results:
            if isinstance(result, Document):
                documents.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Document processing failed: {result}")
        
        logger.info(f"✅ Successfully loaded {len(documents)} documents")
        
        if documents:
            # Generate embeddings for all new sections
            await self._generate_embeddings_for_documents(documents)
        
        return documents
    
    async def _load_single_document(self, file_path: Path) -> Optional[Document]:
        """Load and process a single document."""
        try:
            # Load JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            markdown_content = data.get('markdown', '')
            metadata = data.get('metadata', {})
            
            if not markdown_content:
                logger.warning(f"No markdown content in {file_path}")
                return None
            
            # Process document
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
            
            # Store in memory
            self.documents[document.id] = document
            for section in document.sections:
                self.sections[section.id] = section
            
            return document
            
        except Exception as e:
            logger.error(f"Failed to load document {file_path}: {e}")
            return None
    
    async def _generate_embeddings_for_documents(self, documents: List[Document]) -> None:
        """Generate embeddings for all sections in documents."""
        # Collect all sections that need embeddings
        sections_to_embed = []
        for document in documents:
            for section in document.sections:
                if section.content and section.content.strip():
                    sections_to_embed.append(section)
        
        if not sections_to_embed:
            logger.info("No sections to embed")
            return
        
        logger.info(f"Generating embeddings for {len(sections_to_embed)} sections")
        
        # Generate embeddings in batches
        embeddings_dict = {}
        metadata_dict = {}
        
        batch_size = 50
        for i in range(0, len(sections_to_embed), batch_size):
            batch = sections_to_embed[i:i + batch_size]
            
            # Prepare texts for embedding
            texts = [section.content[:2000] for section in batch]  # Truncate for speed
            
            try:
                # Generate embeddings
                response = self.embeddings_model.embeddings.create(
                    input=texts,
                    model="text-embedding-ada-002",
                    timeout=25
                )
                
                # Store embeddings
                for idx, section in enumerate(batch):
                    embedding = np.array(response.data[idx].embedding)
                    embeddings_dict[section.id] = embedding
                    
                    # Prepare metadata
                    metadata_dict[section.id] = {
                        "title": section.title,
                        "file_path": section.file_path,
                        "section_type": section.section_type.value,
                        "word_count": section.metadata.get("word_count", 0),
                        "created_at": section.created_at.isoformat()
                    }
                
                logger.info(f"✅ Generated embeddings for batch {i//batch_size + 1}/{(len(sections_to_embed)-1)//batch_size + 1}")
                
            except Exception as e:
                logger.error(f"Failed to generate embeddings for batch {i}-{i+batch_size}: {e}")
                continue
        
        # Store all embeddings in Redis
        if embeddings_dict:
            stored_count = await self.redis_service.batch_store_embeddings(
                embeddings_dict, 
                metadata_dict
            )
            logger.info(f"✅ Stored {stored_count} embeddings in Redis")
    
    async def search_sections(self, query: str, limit: int = 10) -> List[DocumentSection]:
        """Ultra-fast embedding-based search with Redis."""
        try:
            # Check for cached query embedding
            query_embedding = await self.redis_service.get_cached_query_embedding(query)
            
            if query_embedding is None:
                # Generate new query embedding
                response = self.embeddings_model.embeddings.create(
                    input=query[:1000],  # Truncate for speed
                    model="text-embedding-ada-002",
                    timeout=15
                )
                query_embedding = np.array(response.data[0].embedding)
                
                # Cache the query embedding
                await self.redis_service.cache_query_embedding(query, query_embedding)
            
            # Perform vector similarity search
            similar_sections = await self.redis_service.vector_similarity_search(
                query_embedding,
                limit=limit,
                threshold=0.1
            )
            
            # Convert to DocumentSection objects
            results = []
            for section_id, similarity in similar_sections:
                section = self.sections.get(section_id)
                if section:
                    results.append(section)
            
            # Fill remaining slots with keyword search if needed
            if len(results) < limit:
                keyword_results = self._keyword_search_sections(query, limit - len(results))
                existing_ids = {section.id for section in results}
                
                for section in keyword_results:
                    if section.id not in existing_ids:
                        results.append(section)
                        if len(results) >= limit:
                            break
            
            logger.info(f"✅ Found {len(results)} sections for query: {query[:50]}...")
            return results[:limit]
            
        except Exception as e:
            logger.error(f"❌ Search failed: {e}, falling back to keyword search")
            return self._keyword_search_sections(query, limit)
    
    def _keyword_search_sections(self, query: str, limit: int = 10) -> List[DocumentSection]:
        """Fallback keyword search when embedding search fails."""
        results = []
        query_lower = query.lower()
        query_terms = query_lower.split()
        
        for section in self.sections.values():
            score = 0
            title_lower = section.title.lower()
            content_lower = section.content.lower()
            
            # Score based on term matches
            for term in query_terms:
                if term in title_lower:
                    score += 10
                if term in content_lower:
                    score += 1
            
            # Exact phrase matches
            if query_lower in title_lower:
                score += 20
            if query_lower in content_lower:
                score += 5
            
            # Domain-specific terms
            domain_terms = {
                'agent': 5, 'handoff': 5, 'guardrail': 5, 'tool': 3,
                'runner': 3, 'instruction': 2, 'function': 2
            }
            for term, bonus in domain_terms.items():
                if term in content_lower:
                    score += bonus
            
            if score > 0:
                results.append((section, score))
        
        # Sort by score and return top results
        results.sort(key=lambda x: x[1], reverse=True)
        return [section for section, score in results[:limit]]
    
    def _parse_markdown_sections(self, content: str, file_path: str) -> List[DocumentSection]:
        """Parse markdown content into logical sections."""
        lines = content.split('\n')
        sections = []
        current_section = None
        section_content = []
        line_start = 0
        header_level = 0
        
        for i, line in enumerate(lines):
            if line.strip().startswith('#'):
                # Save previous section
                if current_section:
                    sections.append(self._create_section(
                        current_section,
                        '\n'.join(section_content),
                        file_path,
                        line_start,
                        i - 1,
                        header_level
                    ))
                
                # Start new section
                header_match = re.match(r'^(#+)\\s*(.+)', line.strip())
                if header_match:
                    header_level = len(header_match.group(1))
                    current_section = header_match.group(2).strip()
                    section_content = []
                    line_start = i
            else:
                section_content.append(line)
        
        # Save last section
        if current_section:
            sections.append(self._create_section(
                current_section,
                '\n'.join(section_content),
                file_path,
                line_start,
                len(lines) - 1,
                header_level
            ))
        
        # Create default section if no headers found
        if not sections:
            sections.append(self._create_section(
                "Main Content",
                content,
                file_path,
                0,
                len(lines) - 1,
                1
            ))
        
        return sections
    
    def _create_section(
        self,
        title: str,
        content: str,
        file_path: str,
        line_start: int,
        line_end: int,
        header_level: int = 1
    ) -> DocumentSection:
        """Create a DocumentSection with metadata."""
        section_id = self._generate_section_id(title, file_path, line_start)
        content = content.strip()
        
        # Determine section type
        section_type = DocumentType.CODE if '```' in content else DocumentType.MARKDOWN
        
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
        """Generate unique document ID."""
        return hashlib.md5(file_path.encode()).hexdigest()
    
    def _generate_section_id(self, title: str, file_path: str, line_start: int) -> str:
        """Generate unique section ID."""
        content = f"{file_path}:{title}:{line_start}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get_document_by_id(self, doc_id: str) -> Optional[Document]:
        """Get document by ID."""
        return self.documents.get(doc_id)
    
    def get_section_by_id(self, section_id: str) -> Optional[DocumentSection]:
        """Get section by ID."""
        return self.sections.get(section_id)
    
    async def get_embedding_stats(self) -> Dict[str, Any]:
        """Get embedding storage statistics."""
        return await self.redis_service.get_stats()
    
    async def clear_embeddings(self) -> bool:
        """Clear all embeddings from Redis."""
        return await self.redis_service.clear_all_embeddings()
    
    def close(self) -> None:
        """Close Redis connection."""
        self.redis_service.close()
        logger.info("✅ Redis Document Processor closed")