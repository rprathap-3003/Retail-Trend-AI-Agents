from PIL import Image, ImageDraw, ImageFilter, ImageOps
import random
import math

def create_crushed_velvet(width, height, base_color):
    """
    Creates a texture resembling crushed velvet using noise and blurring.
    """
    # Base color
    img = Image.new('RGB', (width, height), base_color)
    
    # Create a noise layer
    noise = Image.effect_noise((width, height), 20) # grayscale noise
    
    # Colorize the noise
    # We want varied shades of the base color
    # Base: (0, 100, 0) -> Dark Green
    # Highlights: (50, 150, 50) -> Lighter Green
    # Shadows: (0, 50, 0) -> Very Dark Green
    
    # Convert noise to RGB map
    noise_rgb = noise.convert('RGB')
    
    # Blending
    # We'll use the noise to interpolate between shadow and highlight
    pixels = img.load()
    noise_pixels = noise_rgb.load()
    
    r0, g0, b0 = base_color
    
    for y in range(height):
        for x in range(width):
            n = noise_pixels[x, y][0] / 255.0 # 0 to 1
            
            # Contrast stretch the noise for "crushed" look
            n = (n - 0.5) * 2 + 0.5
            n = max(0, min(1, n))
            
            # Highlight factor
            h_factor = n
            
            # Mix base with highlight/shadow
            # Simple approach: modulate brightness
            # Lighter patches
            if n > 0.6:
                r = min(255, int(r0 + (50 * n)))
                g = min(255, int(g0 + (80 * n)))
                b = min(255, int(b0 + (50 * n)))
            # Darker patches
            else:
                r = max(0, int(r0 - (30 * (1-n))))
                g = max(0, int(g0 - (30 * (1-n))))
                b = max(0, int(b0 - (30 * (1-n))))
                
            pixels[x, y] = (r, g, b)
            
    # Blur to smooth out pixel noise into "fabric"
    img = img.filter(ImageFilter.GaussianBlur(radius=2))
    return img

def draw_detailed_rose(draw, cx, cy, size):
    """
    Draws a rose using overlapping arcs/petals.
    """
    # Colors
    petal_dark = (100, 0, 20)
    petal_mid = (180, 20, 50)
    petal_light = (220, 50, 80)
    
    # Center bud
    draw.ellipse([cx-size*0.2, cy-size*0.2, cx+size*0.2, cy+size*0.2], fill=petal_dark)
    
    # Spiral loops for petals
    angle = 0
    radius = size * 0.2
    
    layers = 5
    petals_per_layer = 3
    
    for layer in range(layers):
        layer_color = petal_mid if layer < layers-2 else petal_light
        # Slightly vary color
        r, g, b = layer_color
        r += random.randint(-20, 20)
        layer_color = (max(0, min(255, r)), g, b)
        
        for p in range(petals_per_layer):
            start_angle = angle
            extent = 120 # degrees
            
            # Polar to cartesian for bounding box of the arc?
            # PIL arc/chord needs bounding box.
            
            # Let's draw filled chords or polygons
            # Calculate points for a "petal" shape (curved triangle)
            petal_points = []
            steps = 10
            
            # Inner edge
            for s in range(steps + 1):
                a = math.radians(start_angle + (extent * s / steps))
                px = cx + math.cos(a) * radius
                py = cy + math.sin(a) * radius
                petal_points.append((px, py))
            
            # Outer edge (wider)
            radius_outer = radius + (size * 0.15)
            for s in range(steps, -1, -1):
                a = math.radians(start_angle + (extent * s / steps))
                px = cx + math.cos(a) * radius_outer
                py = cy + math.sin(a) * radius_outer
                petal_points.append((px, py))
                
            draw.polygon(petal_points, fill=layer_color, outline=petal_dark)
            
            angle += 140 # varying overlap
            
        radius = radius_outer

def create_best_images():
    width, height = 800, 800
    
    # 1. Create Velvet Texture (Base)
    print("Generating velvet texture...")
    velvet_green = (20, 80, 30)
    velvet_bg = create_crushed_velvet(width, height, velvet_green)
    
    # 2. Image 1: Green Velvet Rose (Success)
    img1 = velvet_bg.copy()
    draw1 = ImageDraw.Draw(img1)
    
    print("Drawing roses...")
    for _ in range(25):
        # Cluster in center area
        x = random.randint(250, 550)
        y = random.randint(200, 600)
        size = random.randint(30, 60)
        draw_detailed_rose(draw1, x, y, size)
        
    # Mask to T-Shirt Shape
    mask = Image.new('L', (width, height), 0)
    draw_mask = ImageDraw.Draw(mask)
    shirt_points = [
        (300, 100), (500, 100),  # Neck
        (650, 250), (600, 300),  # Right Sleeve (cuff)
        (500, 350),              # Right Armpit (lower)
        (500, 750),              # Bottom Right
        (300, 750),              # Bottom Left
        (300, 350),              # Left Armpit (lower)
        (200, 300), (150, 250),  # Left Sleeve (cuff)
    ]
    draw_mask.polygon(shirt_points, fill=255)
    
    final_img1 = Image.new('RGB', (width, height), (255, 255, 255))
    final_img1.paste(img1, (0, 0), mask=mask)
    final_img1.save('colored_shirt_1.jpg', quality=95)
    print("Saved colored_shirt_1.jpg")

    # 3. Image 2: Plain Green Velvet (Failure)
    img2 = velvet_bg.copy()
    # No roses
    
    final_img2 = Image.new('RGB', (width, height), (255, 255, 255))
    final_img2.paste(img2, (0, 0), mask=mask)
    final_img2.save('colored_shirt_2.jpg', quality=95)
    print("Saved colored_shirt_2.jpg")

if __name__ == "__main__":
    create_best_images()
