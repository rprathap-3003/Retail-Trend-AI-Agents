from PIL import Image, ImageDraw
import os

def create_shirt_base(width=800, height=800, color=(0, 128, 0)):
    # Create white background
    img = Image.new('RGB', (width, height), 'white')
    draw = ImageDraw.Draw(img)
    
    # Define T-shirt shape points (simple representation)
    # Center is 400, 400
    # Neck: 350,100 to 450,100
    # Sleeves: extend to sides
    
    shirt_points = [
        (300, 100), (500, 100),  # Neck top
        (650, 250), (600, 300),  # Right Sleeve
        (500, 250),              # Right Armpit
        (500, 700),              # Bottom Right
        (300, 700),              # Bottom Left
        (300, 250),              # Left Armpit
        (200, 300), (150, 250),  # Left Sleeve
    ]
    
    draw.polygon(shirt_points, fill=color, outline='black')
    return img

def add_rose_pattern(img):
    draw = ImageDraw.Draw(img)
    # Add simple "rose" patterns (red/pink spirals/circles)
    # We'll just randomly place them within a bounding box that approximates the shirt center
    import random
    
    center_x, center_y = 400, 400
    
    for _ in range(20):
        # Random position within part of the shirt
        x = random.randint(320, 480)
        y = random.randint(250, 600)
        
        # Draw a "rose" (red circle with lighter center)
        radius = random.randint(10, 20)
        draw.ellipse([x-radius, y-radius, x+radius, y+radius], fill=(220, 20, 60)) # Crimson
        draw.ellipse([x-radius/2, y-radius/2, x+radius/2, y+radius/2], fill=(255, 105, 180)) # HotPink

def create_images():
    # Image 1: Green Rose Shirt (Success Case)
    img1 = create_shirt_base(color=(34, 139, 34)) # Forest Green
    add_rose_pattern(img1)
    img1.save('colored_shirt_1.jpg')
    print("Created colored_shirt_1.jpg")

    # Image 2: Plain Green Shirt (Failed Case)
    img2 = create_shirt_base(color=(34, 139, 34)) # Same Green
    img2.save('colored_shirt_2.jpg')
    print("Created colored_shirt_2.jpg")

if __name__ == "__main__":
    create_images()
