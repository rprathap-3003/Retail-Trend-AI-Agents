from PIL import Image, ImageDraw, ImageFilter
import random
import requests
import io

def get_real_rose():
    # Try one very likely URL (GitHub raw is usually good)
    url = "https://raw.githubusercontent.com/googlecreativelab/quickdraw-dataset/master/examples/rose.png" 
    # Just a guess, probably doesn't exist.
    # Let's rely on drawing.
    return None

def draw_rose_icon(size=100):
    img = Image.new("RGBA", (size, size), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    
    # 1. Base Red Circle
    margin = 5
    draw.ellipse([margin, margin, size-margin, size-margin], fill=(200, 20, 40))
    
    # 2. Add "Petal" swirls (Lighter pink)
    center = size / 2
    
    # Draw a spiral-ish shape using arcs
    draw.arc([margin+10, margin+10, size-margin-10, size-margin-10], start=0, end=270, fill=(255, 100, 100), width=8)
    draw.arc([margin+25, margin+25, size-margin-25, size-margin-25], start=90, end=360, fill=(255, 100, 100), width=8)
    draw.ellipse([center-10, center-10, center+10, center+10], fill=(150, 0, 0)) # Centre
    
    return img

def create_final_images():
    width, height = 1000, 1000
    color = (34, 139, 34) # Forest Green
    
    # 1. Base Shirt
    base = Image.new('RGB', (width, height), color)
    
    # 2. Get Rose Stamp
    rose = draw_rose_icon(120)
    
    # 3. Create Pattern
    print("Generating pattern with high-contrast roses...")
    for _ in range(40):
        x = random.randint(100, 900)
        y = random.randint(100, 900)
        
        # Paste with transparency
        # Rotate for variety
        r_rose = rose.rotate(random.randint(0, 360))
        base.paste(r_rose, (x, y), r_rose)
        
    # 4. Cutout
    mask = Image.new('L', (width, height), 0)
    draw_m = ImageDraw.Draw(mask)
    
    # Simple T-shirt Shape
    points = [
        (250, 100), (350, 200), (200, 250), (250, 350), # Left Arm
        (250, 350), (250, 900), # Left Side
        (750, 900), (750, 350), # Right Side
        (750, 350), (800, 250), (650, 200), (750, 100), # Right Arm
        (500, 120) # Neck
    ]
    # Better shape
    shirt_poly = [
        (300, 50), (700, 50), # Top
        (850, 250), (750, 350), # R Sleeve
        (700, 300), (700, 950), # R Side
        (300, 950), (300, 300), # L Side
        (250, 350), (150, 250), # L Sleeve
    ]
    
    draw_m.polygon(shirt_poly, fill=255)
    
    final = Image.new('RGB', (width, height), (255, 255, 255))
    final.paste(base, (0, 0), mask=mask)
    
    final.save("colored_shirt_1.jpg")
    print("Saved colored_shirt_1.jpg")
    
    # Plain
    base_plain = Image.new('RGB', (width, height), color)
    final_plain = Image.new('RGB', (width, height), (255, 255, 255))
    final_plain.paste(base_plain, (0, 0), mask=mask)
    final_plain.save("colored_shirt_2.jpg")
    print("Saved colored_shirt_2.jpg")

if __name__ == "__main__":
    create_final_images()
