from PIL import Image, ImageDraw, ImageFilter
import random
import math

def create_velvet_texture(width, height, color):
    # Create base image
    img = Image.new('RGB', (width, height), color)
    pixels = img.load()
    
    # Add noise to simulate velvet sheen/texture
    for y in range(height):
        for x in range(width):
            # Vary color slightly
            r, g, b = color
            noise = random.randint(-20, 20)
            r = max(0, min(255, r + noise))
            g = max(0, min(255, g + noise))
            b = max(0, min(255, b + noise))
            pixels[x, y] = (r, g, b)
            
    # Soften the noise
    img = img.filter(ImageFilter.GaussianBlur(radius=1))
    return img

def draw_rose(draw, cx, cy, radius, color):
    # Draw a rose-like spiral/cluster of petals
    # Central part
    draw.ellipse([cx-radius*0.2, cy-radius*0.2, cx+radius*0.2, cy+radius*0.2], fill=(150, 0, 0))
    
    # Spiral petals
    angle = 0
    dist = radius * 0.2
    for i in range(15):
        # Calculate petal position
        angle += 0.8  # radians
        dist += radius * 0.05
        
        petal_x = cx + math.cos(angle) * dist
        petal_y = cy + math.sin(angle) * dist
        
        petal_radius = radius * (0.2 + 0.02 * i)
        
        # Vary color for depth
        r = random.randint(180, 255)
        g = random.randint(0, 50)
        b = random.randint(0, 50)
        
        x0 = petal_x - petal_radius
        y0 = petal_y - petal_radius
        x1 = petal_x + petal_radius
        y1 = petal_y + petal_radius
        
        draw.ellipse([x0, y0, x1, y1], fill=(r, g, b))

def create_better_shirt():
    width, height = 800, 800
    
    # 1. Create Texture (Green Velvet)
    # Dark Green for Green Velvet: (0, 50, 0)
    print("Generating velvet texture...")
    texture_img = create_velvet_texture(width, height, (10, 60, 10))
    
    # 2. Add Rose Pattern
    print("Adding rose patterns...")
    draw = ImageDraw.Draw(texture_img)
    
    # Draw many roses in the "shirt area" (approximate)
    for _ in range(30):
        rx = random.randint(200, 600)
        ry = random.randint(100, 700)
        size = random.randint(20, 40)
        draw_rose(draw, rx, ry, size, (200, 0, 0))
        
    # 3. Cut out Shirt Shape
    # Create mask
    mask = Image.new('L', (width, height), 0)
    mask_draw = ImageDraw.Draw(mask)
    
    shirt_points = [
        (300, 100), (500, 100),  # Neck
        (650, 250), (600, 300),  # Right Sleeve
        (500, 250),              # Right Armpit
        (500, 700),              # Bottom Right
        (300, 700),              # Bottom Left
        (300, 250),              # Left Armpit
        (200, 300), (150, 250),  # Left Sleeve
    ]
    mask_draw.polygon(shirt_points, fill=255)
    
    # Composite
    final_img = Image.new('RGB', (width, height), (255, 255, 255))
    final_img.paste(texture_img, (0, 0), mask=mask)
    
    final_img.save('colored_shirt_1.jpg')
    print("Created improved colored_shirt_1.jpg")

if __name__ == "__main__":
    create_better_shirt()
