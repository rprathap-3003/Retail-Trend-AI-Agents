import os
import json
import logging
from typing import List, Dict, Optional, Tuple
from langchain_community.vectorstores import Chroma
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_core.documents import Document
import numpy as np
from .image_processor import ImageProcessor

logger = logging.getLogger(__name__)

class EnhancedVectorStoreService:
    def __init__(self, persist_directory="./chroma_db"):
        # Text embeddings for ChromaDB using Vertex AI
        print("🔵 Initializing Vertex AI embeddings (OAuth2)...")
        self.text_embeddings = VertexAIEmbeddings(
            model_name="text-embedding-004",
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-east4")
        )
        
        # Image processor for CLIP embeddings
        self.image_processor = ImageProcessor()
        
        self.persist_directory = persist_directory
        self.text_db = None
        self.inventory_embeddings = {}  # Store image embeddings separately
        
    def initialize_db(self, inventory: List[Dict]):
        """
        Ingests inventory into ChromaDB with both text and image embeddings.
        """
        documents = []
        
        # Process all images in bulk first
        print("🖼️ Processing inventory images with CLIP...")
        self.inventory_embeddings = self.image_processor.bulk_process_inventory(inventory)
        
        # Create text documents for ChromaDB
        print(f"📝 Embedding {len(inventory)} text descriptions...")
        for item in inventory:
            # Create a rich text representation for embedding
            text_content = f"Item: {item['name']}. Description: {item['description']}. Category: {item['category']}. Color: {item['color']}. Style: {item['style']}."
            
            # Add image embedding info to metadata
            metadata = item.copy()
            item_id = item.get('id')
            if item_id in self.inventory_embeddings:
                metadata['has_image_embedding'] = True
                metadata['image_embedding_shape'] = str(self.inventory_embeddings[item_id]['image_embedding'].shape)
            else:
                metadata['has_image_embedding'] = False
                
            doc = Document(page_content=text_content, metadata=metadata)
            documents.append(doc)

        # Initialize text-based ChromaDB
        self.text_db = Chroma.from_documents(
            documents=documents,
            embedding=self.text_embeddings,
            persist_directory=self.persist_directory
        )
        
        print("✅ Enhanced Vector DB initialized with text and image embeddings.")
        
    def search_text_only(self, query: str, k: int = 5) -> List[Dict]:
        """
        Traditional text-only semantic search.
        """
        if not self.text_db:
            # load from disk if exists
            self.text_db = Chroma(persist_directory=self.persist_directory, embedding_function=self.text_embeddings)

        results = self.text_db.similarity_search(query, k=k)
        items = [doc.metadata for doc in results]
        return items
        
    def hybrid_search(self, query: str, trend_image: Optional[str] = None, 
                     k: int = 5, text_weight: float = 0.3, image_weight: float = 0.7) -> List[Tuple[Dict, float]]:
        """
        Hybrid search using both text and image similarity.
        
        Args:
            query: Text description of what to search for
            trend_image: Optional path to reference image
            k: Number of results to return
            text_weight: Weight for text similarity (0.0-1.0)
            image_weight: Weight for image similarity (0.0-1.0)
            
        Returns:
            List of (item, combined_score) tuples sorted by relevance
        """
        if not self.text_db:
            self.text_db = Chroma(persist_directory=self.persist_directory, embedding_function=self.text_embeddings)
            
        # Get text-based candidates (cast wider net)
        text_candidates = self.search_text_only(query, k=k*3)  # Get more candidates
        
        # Calculate hybrid scores for each candidate
        scored_items = []
        for item in text_candidates:
            item_id = item.get('id')
            
            if item_id not in self.inventory_embeddings:
                # Fallback to text-only scoring
                # Use a default confidence based on position in text results
                position = text_candidates.index(item)
                text_score = max(0.1, 1.0 - (position * 0.1))  # Decreasing confidence
                scored_items.append((item, text_score * 0.4))  # Default 40% confidence
                continue
                
            # Calculate hybrid similarity
            hybrid_score = self.image_processor.hybrid_similarity(
                item_embeddings=self.inventory_embeddings[item_id],
                trend_text=query,
                trend_image=trend_image,
                text_weight=text_weight,
                image_weight=image_weight
            )
            
            # Convert to percentage and ensure minimum threshold
            confidence = max(0.1, hybrid_score * 100)
            scored_items.append((item, confidence))
            
        # Sort by score and return top k
        scored_items.sort(key=lambda x: x[1], reverse=True)
        return scored_items[:k]
        
    def find_similar_products(self, target_item_id: str, k: int = 5, use_images: bool = True) -> List[Dict]:
        """
        Find products similar to a target item using CLIP embeddings.
        """
        return self.image_processor.find_similar_products(
            target_item_id=target_item_id,
            embeddings_dict=self.inventory_embeddings,
            top_k=k,
            use_images=use_images
        )
        
    def cluster_inventory(self, n_clusters: int = 5, use_images: bool = True) -> Dict:
        """
        Cluster inventory items based on their embeddings.
        """
        return self.image_processor.cluster_inventory(
            embeddings_dict=self.inventory_embeddings,
            n_clusters=n_clusters,
            use_images=use_images
        )
        
    def get_item_embedding(self, item_id: str, embedding_type: str = 'image') -> Optional[np.ndarray]:
        """
        Get the embedding for a specific item.
        
        Args:
            item_id: ID of the item
            embedding_type: 'image' or 'text'
            
        Returns:
            Numpy array of embeddings or None if not found
        """
        if item_id not in self.inventory_embeddings:
            return None
            
        key = f"{embedding_type}_embedding"
        return self.inventory_embeddings[item_id].get(key)
        
    def calculate_trend_confidence(self, item_id: str, trend_description: str, 
                                 trend_image: Optional[str] = None) -> Tuple[float, str]:
        """
        Calculate confidence score for how well an item matches a trend.
        
        Returns:
            Tuple of (confidence_score, method_used)
        """
        if item_id not in self.inventory_embeddings:
            return 0.4, "DESC"  # Default text fallback
            
        # Calculate hybrid similarity
        confidence = self.image_processor.hybrid_similarity(
            item_embeddings=self.inventory_embeddings[item_id],
            trend_text=trend_description,
            trend_image=trend_image,
            text_weight=0.3,
            image_weight=0.7
        )
        
        # Determine method used
        method = "AI"  # Image-based analysis was attempted
        if confidence < 0.5 and trend_image is None:
            method = "DESC"  # Primarily text-based
            
        return confidence, method

# Backward compatibility alias
VectorStoreService = EnhancedVectorStoreService

vector_store = VectorStoreService()
