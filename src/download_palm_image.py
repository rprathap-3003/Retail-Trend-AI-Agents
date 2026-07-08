#!/usr/bin/env python3
"""
Simple script to download tropical palm leaf bow tie image
"""
import os
import requests
import time
from duckduckgo_search import DDGS

def download_image(url: str, filename: str) -> bool:
    """Download an image from URL"""
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

def download_tropical_palm_leaf_image():
    """Download tropical palm leaf bow tie image for FLOWER-010"""
    
    filename = "data/images/FLOWER-010.jpg"
    search_query = "tropical palm leaf bow tie green silk men's formal"
    
    print(f"Searching for: {search_query}")
    
    try:
        ddgs = DDGS()
        results = ddgs.images(
            keywords=search_query,
            region="us-en",
            safesearch="moderate", 
            size="medium",
            max_results=5
        )
        
        # Try to download the first few results
        downloaded = False
        for i, result in enumerate(results):
            if downloaded:
                break
                
            try:
                image_url = result.get('image')
                if image_url:
                    print(f"Attempting to download: {image_url}")
                    if download_image(image_url, filename):
                        print(f"✅ Successfully downloaded tropical palm leaf bow tie image!")
                        downloaded = True
                        break
            except Exception as e:
                print(f"Failed to download result {i+1}: {e}")
                continue
        
        if not downloaded:
            print("❌ Could not download tropical palm leaf bow tie image")
            return False
            
    except Exception as e:
        print(f"Search failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    # Ensure directory exists
    os.makedirs("data/images", exist_ok=True)
    download_tropical_palm_leaf_image()