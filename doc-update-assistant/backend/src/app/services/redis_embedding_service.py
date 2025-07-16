"""Redis-based embedding storage service with vector similarity search."""

import json
import hashlib
import numpy as np
from typing import Dict, List, Optional, Tuple
import redis
from redis.exceptions import ConnectionError, TimeoutError
import logging
from ..config import settings
from ..models.document import DocumentSection

logger = logging.getLogger(__name__)


class RedisEmbeddingService:
    """
    High-performance embedding storage using Redis with vector similarity search.
    
    Features:
    - Ultra-fast in-memory storage
    - Concurrent access support
    - Atomic operations
    - Query embedding caching
    - Batch operations
    """
    
    def __init__(self, redis_url: str = None):
        """Initialize Redis connection with optimized settings."""
        self.redis_url = redis_url or getattr(settings, 'redis_url', 'redis://localhost:6379/0')
        self.redis_client = None
        self.query_cache_ttl = 3600  # 1 hour cache for query embeddings
        self.batch_size = 100
        self._connect()
    
    def _connect(self) -> None:
        """Establish Redis connection with connection pooling."""
        try:
            # Create connection pool first
            connection_pool = redis.ConnectionPool.from_url(
                self.redis_url,
                decode_responses=False,  # Keep binary for numpy arrays
                socket_connect_timeout=5,
                socket_timeout=5,
                max_connections=20,
                retry_on_timeout=True,
                health_check_interval=30
            )
            self.redis_client = redis.Redis(connection_pool=connection_pool)
            # Test connection
            self.redis_client.ping()
            logger.info(f"SUCCESS: Connected to Redis at {self.redis_url}")
        except Exception as e:
            logger.error(f"ERROR: Failed to connect to Redis: {e}")
            raise
    
    def _embedding_key(self, section_id: str) -> str:
        """Generate Redis key for embedding storage."""
        return f"embedding:{section_id}"
    
    def _query_cache_key(self, query: str) -> str:
        """Generate Redis key for query embedding cache."""
        query_hash = hashlib.md5(query.encode()).hexdigest()
        return f"query_emb:{query_hash}"
    
    def _metadata_key(self, section_id: str) -> str:
        """Generate Redis key for section metadata."""
        return f"metadata:{section_id}"
    
    def _serialize_embedding(self, embedding: np.ndarray) -> bytes:
        """Serialize numpy array to bytes for Redis storage."""
        return embedding.tobytes()
    
    def _deserialize_embedding(self, data: bytes) -> np.ndarray:
        """Deserialize bytes back to numpy array."""
        return np.frombuffer(data, dtype=np.float32)
    
    async def store_embedding(self, section_id: str, embedding: np.ndarray, metadata: Dict = None) -> bool:
        """
        Store embedding and metadata atomically.
        
        Args:
            section_id: Unique section identifier
            embedding: Numpy array embedding vector
            metadata: Optional metadata dictionary
            
        Returns:
            bool: Success status
        """
        try:
            # Normalize embedding for consistent storage
            embedding_normalized = embedding.astype(np.float32)
            if np.linalg.norm(embedding_normalized) > 0:
                embedding_normalized = embedding_normalized / np.linalg.norm(embedding_normalized)
            
            # Use pipeline for atomic operations
            pipe = self.redis_client.pipeline()
            
            # Store embedding
            pipe.set(
                self._embedding_key(section_id),
                self._serialize_embedding(embedding_normalized),
                ex=86400 * 7  # 7 days TTL
            )
            
            # Store metadata if provided
            if metadata:
                pipe.set(
                    self._metadata_key(section_id),
                    json.dumps(metadata),
                    ex=86400 * 7
                )
            
            # Add to section index
            pipe.sadd("sections:index", section_id)
            
            # Execute all operations atomically
            pipe.execute()
            
            logger.debug(f"✅ Stored embedding for section {section_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to store embedding for {section_id}: {e}")
            return False
    
    async def batch_store_embeddings(self, embeddings: Dict[str, np.ndarray], metadata: Dict[str, Dict] = None) -> int:
        """
        Store multiple embeddings in optimized batches.
        
        Args:
            embeddings: Dictionary of section_id -> embedding
            metadata: Optional metadata for each section
            
        Returns:
            int: Number of successfully stored embeddings
        """
        stored_count = 0
        section_ids = list(embeddings.keys())
        
        for i in range(0, len(section_ids), self.batch_size):
            batch_ids = section_ids[i:i + self.batch_size]
            
            try:
                pipe = self.redis_client.pipeline()
                
                for section_id in batch_ids:
                    embedding = embeddings[section_id]
                    
                    # Normalize embedding
                    embedding_normalized = embedding.astype(np.float32)
                    if np.linalg.norm(embedding_normalized) > 0:
                        embedding_normalized = embedding_normalized / np.linalg.norm(embedding_normalized)
                    
                    # Add to pipeline
                    pipe.set(
                        self._embedding_key(section_id),
                        self._serialize_embedding(embedding_normalized),
                        ex=86400 * 7
                    )
                    
                    # Store metadata if provided
                    if metadata and section_id in metadata:
                        pipe.set(
                            self._metadata_key(section_id),
                            json.dumps(metadata[section_id]),
                            ex=86400 * 7
                        )
                    
                    # Add to index
                    pipe.sadd("sections:index", section_id)
                
                # Execute batch
                pipe.execute()
                stored_count += len(batch_ids)
                
                logger.info(f"✅ Stored batch {i//self.batch_size + 1}: {len(batch_ids)} embeddings")
                
            except Exception as e:
                logger.error(f"❌ Failed to store batch {i}-{i+self.batch_size}: {e}")
                continue
        
        logger.info(f"✅ Total stored: {stored_count}/{len(embeddings)} embeddings")
        return stored_count
    
    async def get_embedding(self, section_id: str) -> Optional[np.ndarray]:
        """Retrieve embedding for a section."""
        try:
            data = self.redis_client.get(self._embedding_key(section_id))
            if data:
                return self._deserialize_embedding(data)
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get embedding for {section_id}: {e}")
            return None
    
    async def get_all_embeddings(self) -> Dict[str, np.ndarray]:
        """Retrieve all embeddings efficiently."""
        try:
            # Get all section IDs
            section_ids = self.redis_client.smembers("sections:index")
            if not section_ids:
                return {}
            
            # Batch retrieve embeddings
            embeddings = {}
            embedding_keys = [self._embedding_key(sid.decode()) for sid in section_ids]
            
            # Use pipeline for batch retrieval
            pipe = self.redis_client.pipeline()
            for key in embedding_keys:
                pipe.get(key)
            
            results = pipe.execute()
            
            for i, data in enumerate(results):
                if data:
                    section_id = list(section_ids)[i].decode()
                    embeddings[section_id] = self._deserialize_embedding(data)
            
            logger.info(f"✅ Retrieved {len(embeddings)} embeddings")
            return embeddings
            
        except Exception as e:
            logger.error(f"❌ Failed to retrieve embeddings: {e}")
            return {}
    
    async def cache_query_embedding(self, query: str, embedding: np.ndarray) -> bool:
        """Cache query embedding for faster repeated searches."""
        try:
            cache_key = self._query_cache_key(query)
            embedding_normalized = embedding.astype(np.float32)
            
            self.redis_client.set(
                cache_key,
                self._serialize_embedding(embedding_normalized),
                ex=self.query_cache_ttl
            )
            return True
        except Exception as e:
            logger.error(f"❌ Failed to cache query embedding: {e}")
            return False
    
    async def get_cached_query_embedding(self, query: str) -> Optional[np.ndarray]:
        """Retrieve cached query embedding."""
        try:
            cache_key = self._query_cache_key(query)
            data = self.redis_client.get(cache_key)
            if data:
                return self._deserialize_embedding(data)
            return None
        except Exception as e:
            logger.error(f"❌ Failed to get cached query embedding: {e}")
            return None
    
    async def vector_similarity_search(self, query_embedding: np.ndarray, limit: int = 10, threshold: float = 0.1) -> List[Tuple[str, float]]:
        """
        Perform ultra-fast vector similarity search.
        
        Args:
            query_embedding: Query vector
            limit: Maximum number of results
            threshold: Minimum similarity threshold
            
        Returns:
            List of (section_id, similarity_score) tuples
        """
        try:
            # Get all embeddings
            embeddings = await self.get_all_embeddings()
            if not embeddings:
                return []
            
            # Normalize query embedding
            query_norm = np.linalg.norm(query_embedding)
            if query_norm == 0:
                return []
            query_normalized = query_embedding / query_norm
            
            # Vectorized similarity computation
            section_ids = list(embeddings.keys())
            embedding_matrix = np.vstack([embeddings[sid] for sid in section_ids])
            
            # Compute cosine similarities
            similarities = np.dot(embedding_matrix, query_normalized)
            
            # Get top results above threshold
            results = []
            for i, similarity in enumerate(similarities):
                if similarity > threshold:
                    results.append((section_ids[i], float(similarity)))
            
            # Sort by similarity and return top results
            results.sort(key=lambda x: x[1], reverse=True)
            return results[:limit]
            
        except Exception as e:
            logger.error(f"❌ Vector similarity search failed: {e}")
            return []
    
    async def delete_embedding(self, section_id: str) -> bool:
        """Delete embedding and metadata for a section."""
        try:
            pipe = self.redis_client.pipeline()
            pipe.delete(self._embedding_key(section_id))
            pipe.delete(self._metadata_key(section_id))
            pipe.srem("sections:index", section_id)
            pipe.execute()
            return True
        except Exception as e:
            logger.error(f"❌ Failed to delete embedding for {section_id}: {e}")
            return False
    
    async def clear_all_embeddings(self) -> bool:
        """Clear all embeddings and metadata."""
        try:
            # Get all section IDs
            section_ids = self.redis_client.smembers("sections:index")
            
            if section_ids:
                # Delete all embeddings and metadata
                keys_to_delete = []
                for section_id in section_ids:
                    sid = section_id.decode()
                    keys_to_delete.extend([
                        self._embedding_key(sid),
                        self._metadata_key(sid)
                    ])
                
                # Batch delete
                if keys_to_delete:
                    self.redis_client.delete(*keys_to_delete)
                
                # Clear index
                self.redis_client.delete("sections:index")
            
            # Clear query cache
            query_keys = self.redis_client.keys("query_emb:*")
            if query_keys:
                self.redis_client.delete(*query_keys)
            
            logger.info("✅ Cleared all embeddings and cache")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to clear embeddings: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, int]:
        """Get embedding storage statistics."""
        try:
            section_count = self.redis_client.scard("sections:index")
            query_cache_count = len(self.redis_client.keys("query_emb:*"))
            
            return {
                "total_embeddings": section_count,
                "cached_queries": query_cache_count,
                "redis_memory_usage": self.redis_client.memory_usage("sections:index") or 0
            }
        except Exception as e:
            logger.error(f"❌ Failed to get stats: {e}")
            return {"total_embeddings": 0, "cached_queries": 0, "redis_memory_usage": 0}
    
    def close(self) -> None:
        """Close Redis connection."""
        if self.redis_client:
            self.redis_client.close()
            logger.info("✅ Redis connection closed")