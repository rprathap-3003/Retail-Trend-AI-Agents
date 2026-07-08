import json
import os
import random
import time
import requests
import urllib.parse
from typing import List, Dict
from langchain_google_vertexai import ChatVertexAI
from duckduckgo_search import DDGS

class DataGenerator:
    def __init__(self):
        print("🔵 Initializing Vertex AI LLM for generator...")
        self.llm = ChatVertexAI(
            model="gemini-2.5-pro",
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-east4")
        )

    def generate_inventory(self, count: int = 50) -> List[Dict]:
        """
        Generates synthetic inventory items (Suits, Ties, Shoes).
        """
        print(f"Generating {count} inventory items...")
        
        categories = ["Suit", "Tie", "Shoes"]
        colors = ["Navy", "Charcoal", "Black", "Burgundy", "Emerald Green", "Beige", "Grey", "White", "Pastel Pink"]
        styles = ["Slim Fit", "Classic Fit", "Modern Fit", "Tuxedo", "Double Breasted"]
        fabrics = ["Wool", "Linen", "Velvet", "Silk", "Cotton Blend", "Tweed"]
        
        inventory = []
        for i in range(count):
            cat = random.choice(categories)
            item = {
                "id": f"ITEM-{1000+i}",
                "category": cat,
                "name": "",
                "color": random.choice(colors),
                "style": random.choice(styles) if cat == "Suit" else ("Oxford" if cat == "Shoes" else "Silk Pattern"),
                "fabric": random.choice(fabrics) if cat != "Shoes" else "Leather",
                "price": random.randint(300, 1200) if cat == "Suit" else (random.randint(50, 150) if cat == "Tie" else random.randint(100, 400)),
                "stock_level": random.randint(0, 50), # Some low stock for RAG testing
                "description": ""
            }
            
            # Construct a descriptive name
            item["name"] = f"{item['color']} {item['fabric']} {item['style']} {cat}"
            item["description"] = f"A premium {item['name']} suitable for formal events. Features high quality {item['fabric']}."
            
            inventory.append(item)
            
        # Save to file
        os.makedirs("data", exist_ok=True)
        with open("data/inventory.json", "w") as f:
            json.dump(inventory, f, indent=2)
            
        print("Inventory saved to data/inventory.json")
        return inventory

    def generate_flower_test_items(self) -> List[Dict]:
        """
        Creates custom flower-themed test inventory items that match current trends.
        """
        flower_items = [
            {
                "id": "FLOWER-001",
                "category": "Tie",
                "name": "Rose Garden Silk Tie",
                "color": "Deep Red",
                "style": "Romantic Vintage",
                "fabric": "Silk",
                "price": 85,
                "stock_level": 15,  # Low stock for urgent replenishment
                "description": "Hand-drawn style red roses with dark green stems and leaves on cream-colored silk background. Romantic vintage-inspired design.",
                "search_query": "red rose garden silk tie men's formal vintage"
            },
            {
                "id": "FLOWER-002", 
                "category": "Shirt",
                "name": "Soft Cherry Blossom Dress Shirt",
                "color": "Pale Pink",
                "style": "Minimalist Floral",
                "fabric": "Cotton",
                "price": 120,
                "stock_level": 8,  # Very low stock for urgent replenishment
                "description": "Minimalist design featuring delicate, scattered cherry blossom branches with pale pink petals on crisp white background. Soft minimalism with nature touch.",
                "search_query": "cherry blossom dress shirt men's pale pink cotton"
            },
            {
                "id": "FLOWER-003",
                "category": "Shirt", 
                "name": "Botanical Fern Print Shirt",
                "color": "Olive Green",
                "style": "Nature-Inspired",
                "fabric": "Cotton",
                "price": 95,
                "stock_level": 12,  # Low stock for replenishment
                "description": "All-over print of detailed, hand-drawn style botanical ferns in olive green on cream-colored background. Understated nature-inspired elegance.",
                "search_query": "botanical fern print shirt men's olive green cotton"
            },
            {
                "id": "FLOWER-004",
                "category": "Tie",
                "name": "Sunflower Sketch Bow Tie",
                "color": "Yellow",
                "style": "Artistic Bold",
                "fabric": "Silk",
                "price": 65,
                "stock_level": 18,  # Medium stock
                "description": "Pattern of large, sketch-style sunflowers with bold black outlines and bright yellow petals on white background. Bold, artistic, and cheerful.",
                "search_query": "sunflower sketch bow tie men's yellow silk artistic"
            },
            {
                "id": "FLOWER-005",
                "category": "Accessory",
                "name": "Lavender Field Pocket Square",
                "color": "Lavender",
                "style": "Watercolor Landscape", 
                "fabric": "Silk",
                "price": 45,
                "stock_level": 22,  # Medium stock
                "description": "Silk pocket square featuring printed watercolor-style landscape of lavender field under pale blue sky. Calm and artistic nature scene.",
                "search_query": "lavender field pocket square silk watercolor men's accessory"
            },
            {
                "id": "FLOWER-006",
                "category": "Suit",
                "name": "Midnight Peony Statement Jacket",
                "color": "Black",
                "style": "Romantic Bold",
                "fabric": "Satin",
                "price": 320,
                "stock_level": 6,  # Very low stock for critical replenishment
                "description": "Satin statement jacket with large-scale print of deep pink and magenta peonies with dark green leaves on black background. Romantic and daring formalwear.",
                "search_query": "midnight peony floral jacket black satin formal statement"
            },
            {
                "id": "FLOWER-007",
                "category": "Shirt",
                "name": "Daffodil Flower Dress Shirt", 
                "color": "Yellow",
                "style": "Spring Floral",
                "fabric": "Cotton",
                "price": 110,
                "stock_level": 35,  # Good stock for display
                "description": "Elegant dress shirt featuring bright daffodil flower patterns, perfect for spring occasions and adding vibrant nature elements to formal wear.",
                "search_query": "daffodil flower dress shirt men's yellow cotton spring"
            },
            {
                "id": "FLOWER-010",
                "category": "Tie",
                "name": "Leaf Bow Tie",
                "color": "Green",
                "style": "Bow Tie",
                "fabric": "Silk",
                "price": 55,
                "stock_level": 6,
                "description": "Simple leaf bow tie for formal occasions.",
                "search_query": "tropical palm leaf bow tie green silk men's formal"
            }
        ]
        return flower_items

    def download_image(self, url: str, filename: str) -> bool:
        """
        Downloads an image from URL and saves it to filename.
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10, stream=True)
            response.raise_for_status()
            
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            return True
        except Exception as e:
            print(f"Failed to download image from {url}: {e}")
            return False

    def search_and_download_flower_images(self, flower_items: List[Dict]):
        """
        Searches for flower-themed images and downloads them for test data.
        """
        os.makedirs("data/images", exist_ok=True)
        print("Searching for and downloading flower-themed test images...")
        
        ddgs = DDGS()
        
        for item in flower_items:
            filename = f"data/images/{item['id']}.jpg"
            if os.path.exists(filename):
                print(f"Image already exists: {filename}")
                continue
                
            print(f"Searching for: {item['search_query']}")
            
            try:
                # Search for images using DuckDuckGo
                results = ddgs.images(
                    keywords=item['search_query'],
                    region="us-en",
                    safesearch="moderate",
                    size="medium",
                    max_results=5
                )
                
                # Try to download the first few results until one succeeds
                downloaded = False
                for i, result in enumerate(results):
                    if downloaded:
                        break
                    
                    try:
                        image_url = result.get('image')
                        if image_url:
                            print(f"Attempting to download: {image_url}")
                            if self.download_image(image_url, filename):
                                print(f"Successfully downloaded image for {item['name']}")
                                downloaded = True
                                break
                    except Exception as e:
                        print(f"Failed to download result {i+1}: {e}")
                        continue
                
                if not downloaded:
                    print(f"Could not download any image for {item['name']}")
                    
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"Search failed for {item['name']}: {e}")

    def generate_images(self, inventory: List[Dict]):
        """
        Generates flower-themed test images by searching and downloading real images.
        """
        print("Generating flower-themed test data with real images...")
        
        # Create custom flower items
        flower_items = self.generate_flower_test_items()
        
        # Search and download images for flower items
        self.search_and_download_flower_images(flower_items)
        
        # Add flower items to inventory and save
        updated_inventory = inventory + flower_items
        
        # Save updated inventory
        os.makedirs("data", exist_ok=True)
        with open("data/inventory_with_flowers.json", "w") as f:
            json.dump(updated_inventory, f, indent=2)
        
        print(f"Added {len(flower_items)} flower-themed items to inventory.")
        print("Updated inventory saved to data/inventory_with_flowers.json")
        
        return flower_items

generator = DataGenerator()
