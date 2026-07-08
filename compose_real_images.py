import requests
from PIL import Image, ImageDraw, ImageOps
import io
import random

def get_rose_image():
    # List of Wikimedia Commons thumbnails (Red Rose)
    urls = [
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/30/Red_rose_02.svg/320px-Red_rose_02.svg.png",
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e6/Rosa_rubiginosa_1.jpg/320px-Rosa_rubiginosa_1.jpg", 
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Red_rose.jpg/320px-Red_rose.jpg"
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    for url in urls:
        print(f"Trying to download rose from: {url}")
        try:
            r = requests.get(url, headers=headers, timeout=5)
            if r.status_code == 200:
                img = Image.open(io.BytesIO(r.content)).convert("RGBA")
                print("Success!")
                return img
        except Exception as e:
            print(f"Failed: {e}")
            
    return None

def create_composite_shirt():
    # 1. Base Green Shirt (Solid Color + Noise for fabric feel)
    width, height = 800, 800
    color = (34, 139, 34) # Forest Green
    
    base = Image.new('RGB', (width, height), color)
    # Add simple noise
    # ... (omitted for brevity, solid is fine if pattern is good)
    
    # 2. Get Real Rose
    rose_img = get_rose_image()
    
    if rose_img:
        # 3. Pattern the Rose onto the Base
        print("Compositing rose pattern...")
        
        # Resize rose to be a "print" size
        rose_size = 80
        rose_img.thumbnail((rose_size, rose_size))
        
        # If image is JPG/rectangular, masking it helps (circular mask)
        mask = Image.new("L", rose_img.size, 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, rose_img.size[0], rose_img.size[1]), fill=255)
        
        # Paste repeatedly
        for _ in range(30):
            x = random.randint(150, 600)
            y = random.randint(150, 600)
            
            # Random rotation?
            # rose_rotated = rose_img.rotate(random.randint(0, 360))
            
            base.paste(rose_img, (x, y), rose_img if rose_img.mode == 'RGBA' else mask)
            
    else:
        print("Could not download any rose image. Tests may fail.")
        
    # 4. Apply Shirt Cutout (Mask)
    shirt_mask = Image.new('L', (width, height), 0)
    draw_s = ImageDraw.Draw(shirt_mask)
    shirt_points = [
        (300, 100), (500, 100),  # Neck
        (650, 250), (600, 300),  # Right Sleeve
        (500, 350),              # Right Armpit
        (500, 750),              # Bottom Right
        (300, 750),              # Bottom Left
        (300, 350),              # Left Armpit
        (200, 300), (150, 250),  # Left Sleeve
    ]
    draw_s.polygon(shirt_points, fill=255)
    
    final = Image.new('RGB', (width, height), (255, 255, 255))
    final.paste(base, (0, 0), mask=shirt_mask)
    
    final.save("colored_shirt_1.jpg")
    print("Saved colored_shirt_1.jpg (Composite)")
    
    # Create plain version too
    plain_base = Image.new('RGB', (width, height), color)
    final_plain = Image.new('RGB', (width, height), (255, 255, 255))
    final_plain.paste(plain_base, (0, 0), mask=shirt_mask)
    final_plain.save("colored_shirt_2.jpg")
    print("Saved colored_shirt_2.jpg")

if __name__ == "__main__":
    create_composite_shirt()
