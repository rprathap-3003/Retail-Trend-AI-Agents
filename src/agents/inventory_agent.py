import logging
import os
import base64
import fnmatch
from typing import List, Dict, Any, Optional
from PIL import Image
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage
from services.vector_store import vector_store

logger = logging.getLogger(__name__)

class EnhancedInventoryAgent:
    def __init__(self):
        print("🔵 Initializing Vertex AI LLM for inventory agent...")
        self.vision_llm = ChatVertexAI(
            model="gemini-2.5-pro",
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-east4")
        )

    def analyze_product_image_detailed(self, image_path: str, trend_description: str) -> Dict:
        """
        Detailed image analysis using Gemini Vision as fallback for low confidence CLIP matches.
        """
        try:
            # Load and encode image
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize for API efficiency
                img.thumbnail((512, 512))
                
                # Save to bytes
                import io
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format='JPEG')
                img_byte_arr = img_byte_arr.getvalue()
                
                # Encode to base64
                img_base64 = base64.b64encode(img_byte_arr).decode()
            
            # Create message with image and trend description
            message = HumanMessage(content=[
                {
                    "type": "text",
                    "text": f"""Analyze this fashion product image and determine if it matches the following trend description:
                    
                    TREND: {trend_description}
                    
                    Please analyze:
                    1. Colors present in the image
                    2. Patterns, textures, or designs visible
                    3. Style and category of the item
                    4. How well it matches the trend (0-100% match)
                    5. Specific matching elements (what makes it match)
                    
                    SCORING GUIDELINES:
                    - Direct flower/botanical matches (roses, daffodils, lavender, etc): 75-90%
                    - Similar color schemes to trend: 60-80%
                    - Similar fabric/texture: 60-75%
                    - General category match (tie, shirt, suit, accessory): 55-70%
                    - Partial visual elements: 50-65%
                    
                    Respond in JSON format:
                    {{
                        "match_percentage": 75,
                        "colors_detected": ["navy", "gold"],
                        "patterns_detected": ["geometric", "art deco"],
                        "category": "suit",
                        "matching_elements": ["geometric pattern", "color scheme"],
                        "recommendation": "PROMOTE|REPLENISH|NO_MATCH"
                    }}"""
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{img_base64}"
                    }
                }
            ])
            
            response = self.vision_llm.invoke([message])
            
            # Parse JSON response
            import json
            try:
                result = json.loads(response.content)
                result['analysis_method'] = 'GEMINI_VISION'
                result['image_path'] = image_path
                return result
            except json.JSONDecodeError:
                return {
                    'match_percentage': 0,
                    'analysis_method': 'GEMINI_VISION_ERROR',
                    'error': 'Failed to parse AI response'
                }
                
        except Exception as e:
            logger.error(f"Gemini Vision analysis failed for {image_path}: {e}")
            return {
                'match_percentage': 0,
                'analysis_method': 'GEMINI_VISION_ERROR',
                'error': str(e)
            }

    def check_trends_against_inventory(self, trends: List[Dict]) -> List[Dict]:
        """
        Enhanced method using CLIP hybrid search + Gemini Vision fallback.
        """
        recommendations = []
        
    def _analyze_single_trend(self, trend: Dict) -> Optional[Dict]:
        """
        Helper method to analyze a single trend, used for parallel processing.
        """
        trend_name = trend.get('name', 'Unknown')
        trend_description = f"{trend.get('description', '')} {trend.get('pattern_details', '')}"
        
        print(f"Analyzing trend: {trend_name}")
        
        # Use hybrid search (CLIP embeddings + text)
        query = f"{trend_name} {trend_description} {trend.get('category', '')}"
        
        # Check for pure Gemini Vision mode
        use_gemini_only = os.getenv("FORCE_GEMINI_VISION", "false").lower() == "true"
        
        best_match = None
        best_score = 0
        analysis_method = 'CLIP_HYBRID'
        detailed_analysis = None

        if use_gemini_only:
            print(f"  🤖 FORCE_GEMINI_VISION is ON for '{trend_name}'. skipping CLIP, using Text Search + Gemini Vision...")
            # 1. Get candidates via text search (broad filter)
            # Broader search using just category to capture items with vague descriptions
            search_term = trend.get('category', 'clothing')
            # print(f"    🔍 Pre-filtering for Vision using category: '{search_term}' (k=10)")
            candidates = vector_store.search_text_only(search_term, k=10)
            
            analysis_method = 'GEMINI_VISION_PURE'
            
            # 2. Analyze every candidate with Gemini Vision
            # Optimization: could parallellize this too, but trend-level parallelism is likely enough
            # 2. Analyze every candidate with Gemini Vision
            filename_filter = os.getenv("GEMINI_FILENAME_FILTER", "all")
            
            for item in candidates:
                item_id = item.get('id', '')
                image_path = item.get('image_path') or f"data/images/{item_id}.jpg"
                
                if os.path.exists(image_path):
                    # Apply filename filter if set
                    if filename_filter.lower() != 'all':
                        is_negative = filename_filter.startswith('!')
                        pattern = filename_filter[1:] if is_negative else filename_filter
                        match = fnmatch.fnmatch(os.path.basename(image_path), pattern)
                        
                        if is_negative:
                            # If negative filter (!FIGURE*), skip if it MATCHES
                            if match:
                                # print(f"    Skipping {item_id} (Excluded by filter: {filename_filter})")
                                continue
                        else:
                            # If positive filter (FIGURE*), skip if it DOES NOT match
                            if not match:
                                # print(f"    Skipping {item_id} (Not matched by filter: {filename_filter})")
                                continue
                    
                    # print(f"    🔍 Analyzing {item_id} with Gemini Vision...")
                    gemini_result = self.analyze_product_image_detailed(image_path, trend_description)
                    score = gemini_result.get('match_percentage', 0)
                    
                    # print(f"    📸 Gemini Score: {score}%")
                    
                    if score > best_score:
                        best_score = score
                        best_match = item
                        detailed_analysis = gemini_result
        
        # Try hybrid search if not using Gemini only
        elif not use_gemini_only:
            try:
                hybrid_results = vector_store.hybrid_search(
                    query=query, 
                    trend_image=None,  # No reference image for trends yet
                    k=3,  # Get top 3 candidates
                    text_weight=0.3,
                    image_weight=0.7
                )
                
                # Evaluate each hybrid result
                for item, confidence in hybrid_results:
                    item_id = item.get('id', '')
                    # print(f"  🔍 CLIP Analysis for {item.get('name', item_id)}: {confidence:.1f}% confidence")
                    
                    # If CLIP confidence is low, try Gemini Vision as fallback
                    if confidence < 60:  # Threshold for detailed analysis
                        image_path = f"data/images/{item_id}.jpg"
                        if os.path.exists(image_path):
                            print(f"    🔍 Low CLIP confidence for {trend_name}, trying Gemini Vision fallback...")
                            gemini_result = self.analyze_product_image_detailed(image_path, trend_description)
                            gemini_confidence = gemini_result.get('match_percentage', 0)
                            
                            # Use higher confidence score
                            if gemini_confidence > confidence:
                                confidence = gemini_confidence
                                analysis_method = 'GEMINI_VISION_FALLBACK'
                                detailed_analysis = gemini_result
                                print(f"    ✅ Gemini Vision improved confidence: {gemini_confidence}%")
                            else:
                                pass # print(f"    📊 CLIP confidence ({confidence:.1f}%) remained higher")
                    
                    # Track best match
                    if confidence > best_score:
                        best_score = confidence
                        best_match = item
                        if detailed_analysis:
                            best_match['detailed_analysis'] = detailed_analysis
                
            except Exception as e:
                logger.warning(f"Hybrid search failed for trend {trend_name}: {e}")
                # Fallback to traditional text search
                similar_items = vector_store.search_text_only(query, k=3)
                if similar_items:
                    best_match = similar_items[0]
                    best_score = 40  # Default confidence for text-only
                    analysis_method = 'TEXT_FALLBACK'

        # Generate recommendation
        if best_match:
            stock_level = best_match.get('stock_level', 0)
            
            # Only generate recommendations for trends with good matches (≥85% confidence)
            if best_score >= 85:
                # Determine action based on stock level and confidence
                if stock_level == 0:
                    action = 'URGENT BUY'
                    reason = f"🚨 Trend '{trend_name}' matched with {best_score:.1f}% confidence but has no stock (0 units)."
                elif stock_level <= 10:
                    action = 'URGENT BUY'
                    reason = f"🚨 Trend '{trend_name}' matched with {best_score:.1f}% confidence but has critically low stock ({stock_level} units)."
                elif stock_level <= 25:
                    action = 'REPLENISH'
                    reason = f"⚠️ Trend '{trend_name}' matched with {best_score:.1f}% confidence but has low stock ({stock_level} units)."
                elif stock_level <= 50:
                    action = 'REPLENISH'
                    reason = f"⚠️ Trend '{trend_name}' matched with {best_score:.1f}% confidence but has moderate stock ({stock_level} units)."
                else:
                    action = 'PROMOTE'
                    reason = f"✅ Ample stock ({stock_level} units) for trend '{trend_name}'. Display prominently."
                
                # Override for high AI confidence matches, but ONLY if stock is healthy
                if best_score >= 80 and stock_level > 10:
                    action = 'PROMOTE'
                    reason = f"🖼️ High-confidence AI match ({best_score:.1f}%). Feature prominently."
            else:
                # No good match found in inventory -> Recommend New Product
                print(f"    ❌ No existing stock matches '{trend_name}' enough (Best: {best_score:.1f}%). Suggesting new product.")
                action = 'NEW PRODUCT OPPORTUNITY'
                reason = f"✨ Trend '{trend_name}' has no matching inventory (Best match: {best_score:.1f}%). Opportunity to introduce new product."
                stock_level = 0
                
                # Create a dummy match object for the report if none exists
                if not best_match:
                        best_match = {'name': 'N/A', 'price': 0, 'id': 'NEW'}
            
            # Determine confidence display method
            if action == 'NEW PRODUCT OPPORTUNITY':
                    method_display = 'New Product Opportunity'
                    reason = f"❌ Didn't find matching items (Best match: {best_score:.1f}%), so requesting new opportunity."
            elif analysis_method.startswith('CLIP') and best_score >= 85:
                method_display = 'AI Analysis of Image'
            elif analysis_method.startswith('GEMINI') and best_score >= 85:
                method_display = 'AI Analysis of Image'
            else:
                method_display = 'AI Analysis of Text'
            
            recommendation = {
                'trend': trend_name,
                'matched_item': best_match,
                'action': action,
                'reason': reason,
                'analysis_method': method_display,
                'detailed_method': analysis_method,
                'match_confidence': best_score,
                'stock_level': stock_level
            }
            
            return recommendation
        return None

    def check_trends_against_inventory(self, trends: List[Dict]) -> List[Dict]:
        """
        Enhanced method using Parallel Processing for faster Vision Analysis.
        """
        recommendations = []
        import concurrent.futures
        import time
        
        start_time = time.time()
        print(f"🚀 Starting Parallel Analysis of {len(trends)} trends (Max Workers: 5)...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Submit all trends
            future_to_trend = {executor.submit(self._analyze_single_trend, trend): trend for trend in trends}
            
            for future in concurrent.futures.as_completed(future_to_trend):
                try:
                    result = future.result()
                    if result:
                        recommendations.append(result)
                except Exception as exc:
                    print(f"Generated an exception: {exc}")
        
        duration = time.time() - start_time
        print(f"✅ Analysis completed in {duration:.1f} seconds")
            
        return recommendations
    
    def find_similar_products(self, target_item_id: str, k: int = 5) -> List[Dict]:
        """
        Find products similar to target item using CLIP embeddings.
        """
        try:
            return vector_store.find_similar_products(target_item_id, k=k, use_images=True)
        except Exception as e:
            logger.error(f"Failed to find similar products for {target_item_id}: {e}")
            return []
    
    def cluster_inventory(self, n_clusters: int = 5) -> Dict:
        """
        Cluster inventory items by visual similarity.
        """
        try:
            return vector_store.cluster_inventory(n_clusters=n_clusters, use_images=True)
        except Exception as e:
            logger.error(f"Failed to cluster inventory: {e}")
            return {}

# Create enhanced agent instance with backward compatibility
enhanced_inventory_agent = EnhancedInventoryAgent()
inventory_agent = enhanced_inventory_agent  # Alias for backward compatibility
