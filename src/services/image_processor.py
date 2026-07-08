"""
Image Processing Service for CLIP-based Image Embeddings and Analysis
"""
import os
import logging
import json
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import pickle

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Enhanced image processor with CLIP embeddings and clustering capabilities"""
    
    def __init__(self, model_name: str = 'clip-ViT-B-32', cache_dir: str = 'cache'):
        """
        Initialize the image processor with CLIP model
        
        Args:
            model_name: CLIP model to use for embeddings
            cache_dir: Directory to cache embeddings and models
        """
        self.model_name = model_name
        self.cache_dir = cache_dir
        self.embeddings_cache = {}
        self.model = None
        
        # Ensure cache directory exists
        os.makedirs(cache_dir, exist_ok=True)
        self.cache_file = os.path.join(cache_dir, 'image_embeddings.pkl')
        
        # Load cached embeddings if they exist
        self._load_cache()
        
    def _initialize_model(self):
        """Lazy initialization of CLIP model"""
        if self.model is None:
            logger.info(f"Initializing CLIP model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            
    def _load_cache(self):
        """Load cached embeddings from disk"""
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'rb') as f:
                    self.embeddings_cache = pickle.load(f)
                logger.info(f"Loaded {len(self.embeddings_cache)} cached image embeddings")
            except Exception as e:
                logger.warning(f"Failed to load embeddings cache: {e}")
                self.embeddings_cache = {}
                
    def _save_cache(self):
        """Save embeddings cache to disk"""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump(self.embeddings_cache, f)
            logger.info(f"Saved {len(self.embeddings_cache)} image embeddings to cache")
        except Exception as e:
            logger.error(f"Failed to save embeddings cache: {e}")
            
    def process_image(self, image_path: str) -> np.ndarray:
        """
        Process a single image and return its CLIP embedding
        
        Args:
            image_path: Path to the image file
            
        Returns:
            numpy array of image embeddings
        """
        # Check cache first
        if image_path in self.embeddings_cache:
            return self.embeddings_cache[image_path]
            
        try:
            self._initialize_model()
            
            # Load and process image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                    
                # Generate embedding
                embedding = self.model.encode(img)
                
                # Cache the result
                self.embeddings_cache[image_path] = embedding
                
                logger.debug(f"Generated embedding for {image_path}, shape: {embedding.shape}")
                return embedding
                
        except Exception as e:
            logger.error(f"Failed to process image {image_path}: {e}")
            # Return zero vector as fallback
            self._initialize_model()
            return np.zeros(512)  # CLIP embeddings are 512-dimensional
            
    def process_text(self, text: str) -> np.ndarray:
        """
        Process text using the same CLIP model for hybrid similarity
        
        Args:
            text: Text description to encode
            
        Returns:
            numpy array of text embeddings
        """
        try:
            self._initialize_model()
            embedding = self.model.encode(text)
            logger.debug(f"Generated text embedding for '{text}', shape: {embedding.shape}")
            return embedding
        except Exception as e:
            logger.error(f"Failed to process text '{text}': {e}")
            self._initialize_model()
            return np.zeros(512)  # CLIP embeddings are 512-dimensional
            
    def bulk_process_inventory(self, inventory_data: List[Dict[str, Any]]) -> Dict[str, Dict[str, np.ndarray]]:
        """
        Process all inventory images in bulk for efficiency
        
        Args:
            inventory_data: List of inventory items with image paths
            
        Returns:
            Dictionary mapping item IDs to their embeddings
        """
        logger.info(f"Processing {len(inventory_data)} inventory items in bulk...")
        
        results = {}
        processed_count = 0
        cached_count = 0
        
        for item in inventory_data:
            item_id = item.get('id')
            image_path = item.get('image_path')
            description = item.get('description', '')
            name = item.get('name', '')
            
            if not item_id or not image_path:
                continue
                
            # Process image
            was_cached = image_path in self.embeddings_cache
            image_embedding = self.process_image(image_path)
            
            # Process text (combine name and description)
            text = f"{name} {description}".strip()
            text_embedding = self.process_text(text)
            
            results[item_id] = {
                'image_embedding': image_embedding,
                'text_embedding': text_embedding,
                'image_path': image_path,
                'text': text
            }
            
            if was_cached:
                cached_count += 1
            else:
                processed_count += 1
                
        # Save updated cache
        if processed_count > 0:
            self._save_cache()
            
        logger.info(f"Bulk processing complete: {processed_count} new, {cached_count} cached")
        return results
        
    def calculate_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Reshape for sklearn cosine_similarity
            emb1 = embedding1.reshape(1, -1)
            emb2 = embedding2.reshape(1, -1)
            
            similarity = cosine_similarity(emb1, emb2)[0][0]
            # Convert from [-1, 1] to [0, 1] range
            return (similarity + 1) / 2
        except Exception as e:
            logger.error(f"Failed to calculate similarity: {e}")
            return 0.0
            
    def hybrid_similarity(self, item_embeddings: Dict[str, np.ndarray], 
                         trend_text: str, trend_image: Optional[str] = None,
                         text_weight: float = 0.3, image_weight: float = 0.7) -> float:
        """
        Calculate hybrid similarity using both text and image embeddings
        
        Args:
            item_embeddings: Dictionary with 'text_embedding' and 'image_embedding'
            trend_text: Text description of the trend
            trend_image: Optional path to trend reference image
            text_weight: Weight for text similarity (default 0.3)
            image_weight: Weight for image similarity (default 0.7)
            
        Returns:
            Combined similarity score between 0 and 1
        """
        total_weight = 0
        combined_score = 0
        
        # Text similarity
        if 'text_embedding' in item_embeddings:
            trend_text_embedding = self.process_text(trend_text)
            text_similarity = self.calculate_similarity(
                item_embeddings['text_embedding'], 
                trend_text_embedding
            )
            combined_score += text_similarity * text_weight
            total_weight += text_weight
            
        # Image similarity (if reference image provided)
        if trend_image and 'image_embedding' in item_embeddings:
            try:
                trend_image_embedding = self.process_image(trend_image)
                image_similarity = self.calculate_similarity(
                    item_embeddings['image_embedding'],
                    trend_image_embedding
                )
                combined_score += image_similarity * image_weight
                total_weight += image_weight
            except Exception as e:
                logger.warning(f"Failed to process trend image {trend_image}: {e}")
                
        # Normalize by actual weights used
        if total_weight > 0:
            return combined_score / total_weight
        else:
            return 0.0
            
    def cluster_inventory(self, embeddings_dict: Dict[str, Dict[str, np.ndarray]], 
                         n_clusters: int = 5, use_images: bool = True) -> Dict[str, Any]:
        """
        Cluster inventory items based on their embeddings
        
        Args:
            embeddings_dict: Dictionary of item embeddings
            n_clusters: Number of clusters to create
            use_images: Whether to use image embeddings (True) or text (False)
            
        Returns:
            Dictionary with cluster assignments and analysis
        """
        if not embeddings_dict:
            return {}
            
        # Extract embeddings for clustering
        item_ids = []
        embeddings = []
        
        embedding_type = 'image_embedding' if use_images else 'text_embedding'
        
        for item_id, data in embeddings_dict.items():
            if embedding_type in data:
                item_ids.append(item_id)
                embeddings.append(data[embedding_type])
                
        if not embeddings:
            logger.warning("No embeddings found for clustering")
            return {}
            
        embeddings_array = np.array(embeddings)
        logger.info(f"Clustering {len(embeddings)} items into {n_clusters} clusters using {embedding_type}")
        
        try:
            # Perform K-means clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(embeddings_array)
            
            # Organize results
            clusters = {}
            for item_id, label in zip(item_ids, cluster_labels):
                label = int(label)  # Convert numpy int to Python int
                if label not in clusters:
                    clusters[label] = []
                clusters[label].append(item_id)
                
            # Calculate cluster statistics
            cluster_stats = {}
            for cluster_id, items in clusters.items():
                cluster_embeddings = np.array([embeddings_dict[item][embedding_type] for item in items])
                centroid = np.mean(cluster_embeddings, axis=0)
                
                # Calculate intra-cluster similarity
                similarities = []
                for i in range(len(cluster_embeddings)):
                    for j in range(i+1, len(cluster_embeddings)):
                        sim = self.calculate_similarity(cluster_embeddings[i], cluster_embeddings[j])
                        similarities.append(sim)
                        
                avg_similarity = np.mean(similarities) if similarities else 0.0
                
                cluster_stats[cluster_id] = {
                    'items': items,
                    'size': len(items),
                    'avg_similarity': float(avg_similarity),
                    'centroid': centroid.tolist()  # Convert to list for JSON serialization
                }
                
            return {
                'clusters': cluster_stats,
                'n_clusters': n_clusters,
                'embedding_type': embedding_type,
                'total_items': len(item_ids)
            }
            
        except Exception as e:
            logger.error(f"Clustering failed: {e}")
            return {}
            
    def find_similar_products(self, target_item_id: str, embeddings_dict: Dict[str, Dict[str, np.ndarray]],
                            top_k: int = 5, use_images: bool = True) -> List[Dict[str, Any]]:
        """
        Find products similar to a target item
        
        Args:
            target_item_id: ID of the target item
            embeddings_dict: Dictionary of all item embeddings
            top_k: Number of similar items to return
            use_images: Whether to use image embeddings (True) or text (False)
            
        Returns:
            List of similar items with similarity scores
        """
        if target_item_id not in embeddings_dict:
            logger.warning(f"Target item {target_item_id} not found")
            return []
            
        embedding_type = 'image_embedding' if use_images else 'text_embedding'
        target_embedding = embeddings_dict[target_item_id].get(embedding_type)
        
        if target_embedding is None:
            logger.warning(f"No {embedding_type} found for {target_item_id}")
            return []
            
        similarities = []
        for item_id, data in embeddings_dict.items():
            if item_id == target_item_id or embedding_type not in data:
                continue
                
            similarity = self.calculate_similarity(target_embedding, data[embedding_type])
            similarities.append({
                'item_id': item_id,
                'similarity': float(similarity),
                'text': data.get('text', ''),
                'image_path': data.get('image_path', '')
            })
            
        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:top_k]