import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import vertexai
from vertexai.preview.vision_models import ImageGenerationModel

def generate_images_for_trends():
    """
    Generates images for a predefined list of fashion trends using Vertex AI.
    """
    # --- Environment Setup ---
    # Add src to path to ensure local modules can be found if needed
    src_path = Path(__file__).resolve().parent / "src"
    sys.path.insert(0, str(src_path))
    load_dotenv()

    # --- Vertex AI Initialization ---
    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    location = os.getenv("GOOGLE_CLOUD_LOCATION")

    if not project or not location:
        print("ERROR: GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION must be set in the .env file.")
        return

    print(f"Initializing Vertex AI for project '{project}' in '{location}'...")
    try:
        vertexai.init(project=project, location=location)
        model = ImageGenerationModel.from_pretrained("imagegeneration@006")
        print("Vertex AI initialized successfully.")
    except Exception as e:
        print(f"ERROR: Failed to initialize Vertex AI: {e}")
        return

    # --- Trend Data ---
    trends_to_generate = [
        {
            "name": "Luxe Velvet Dinner Jacket",
            "colors": "Deep Green, Maroon, Navy",
            "style": "Opulent evening elegance for winter weddings",
            "pattern": "Solid color with a deep, plush velvet texture that creates a subtle sheen."
        },
        {
            "name": "Heritage Flannel Suit",
            "colors": "Dark Brown, Charcoal Grey",
            "style": "Timeless academic, rooted in nature",
            "pattern": "Subtle herringbone or windowpane check woven into a rich, textured flannel fabric."
        },
        {
            "name": "Jacquard Damask Evening Suit",
            "colors": "Charcoal, Silver, Deep Navy",
            "style": "Neo-aristocratic, subtle opulence",
            "pattern": "Tone-on-tone jacquard weave featuring a large-scale, ornate damask floral pattern."
        },
        {
            "name": "Modern Heritage Plaid Trousers",
            "colors": "Brown, Green, Cream",
            "style": "Preppy intellectual with a modern twist",
            "pattern": "An oversized, deconstructed plaid pattern in brown and green on a cream background, relaxed, fuller cut."
        },
        {
            "name": "Botanical Jacquard Wedding Vest",
            "colors": "Beige, Cream, Sage Green",
            "style": "Romantic formalwear for grooms",
            "pattern": "A formal vest with a tone-on-tone jacquard weave featuring an intricate pattern of intertwined ivy vines and subtle rose blossoms."
        },
        {
            "name": "Quilted Diamond Puffer Vest",
            "colors": "Black, Olive Green, Navy",
            "style": "Streetwear meets tailored office layering",
            "pattern": "A lightweight, tailored vest with a diamond-shaped quilted pattern, designed to be layered under a suit jacket."
        },
        {
            "name": "Botanical Sketch Print Shirt",
            "colors": "Cream, Sepia Brown, Forest Green",
            "style": "Refined naturalist for business casual",
            "pattern": "Vintage-style botanical illustrations of leaves and branches, like sketches from a naturalist's journal, printed on a cream cotton."
        },
        {
            "name": "Kyoto Waves Dress Shirt",
            "colors": "Deep Blue, White, Dusty Pink",
            "style": "Artistic and serene, blending cultures",
            "pattern": "Stylized Japanese 'Seigaiha' wave pattern in white and dusty pink, printed on a deep blue, lightweight fabric."
        },
        {
            "name": "Gatsby Art Deco Fan Shirt",
            "colors": "Black, Gold, Cream",
            "style": "Roaring 20s revival, geometric luxury",
            "pattern": "Repeating geometric fan and sunburst motifs of Art Deco design, printed in metallic gold on a black shirt."
        }
    ]

    # --- Image Generation ---
    output_dir = Path("src/data/images")
    output_dir.mkdir(exist_ok=True)

    for trend in trends_to_generate:
        filename = f"{trend['name'].lower().replace(' ', '_')}.png"
        output_path = output_dir / filename
        
        if output_path.exists():
            print(f"Skipping '{trend['name']}', image already exists.")
            continue

        print(f"\nGenerating image for: {trend['name']}...")

        # Construct a detailed prompt
        prompt = (
            f"Photorealistic fashion photograph of a male model wearing a '{trend['name']}'. "
            f"The style is '{trend['style']}'. "
            f"The main colors are {trend['colors']}. "
            f"The item features a '{trend['pattern']}'. "
            "The photo is shot in a high-end studio with professional lighting, sharp focus, and a clean background. "
            "Show the full garment clearly. No text or watermarks."
        )
        
        print(f"   - Prompt: {prompt}")

        try:
            images = model.generate_images(
                prompt=prompt,
                number_of_images=1,
                aspect_ratio="9:16", # Portrait for fashion
                safety_filter_level="block_most"
            )
            
            # Save the first generated image
            images[0].save(location=str(output_path), include_generation_parameters=True)
            print(f"SUCCESS: Image saved to {output_path}")

        except Exception as e:
            print(f"ERROR: Failed to generate image for '{trend['name']}': {e}")

if __name__ == "__main__":
    generate_images_for_trends()
