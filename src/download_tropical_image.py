#!/usr/bin/env python3
"""
Script to download tropical palm leaf bow tie image for FLOWER-010
"""
import os
import sys
sys.path.append('.')
from services.generator import generator

def download_tropical_palm_leaf_image():
    """Download tropical palm leaf bow tie image"""
    
    # Create the tropical palm leaf bow tie item
    tropical_item = {
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
    
    # Download image for this item
    generator.search_and_download_flower_images([tropical_item])
    
    print("✅ Tropical Palm Leaf Bow Tie image download complete!")

if __name__ == "__main__":
    download_tropical_palm_leaf_image()