import os
import base64
import json
from PIL import Image
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def analyze_image(image_path, description):
    print(f"\n🔍 Analyzing: {image_path}")
    print(f"📋 Target Description: '{description}'")
    
    if not os.path.exists(image_path):
        print(f"❌ Error: Image not found at {image_path}")
        return

    try:
        # Initialize Vertex AI
        llm = ChatVertexAI(
            model="gemini-2.5-pro",
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-east4")
        )

        # Prepare Image
        with Image.open(image_path) as img:
            # Resize for efficiency
            img.thumbnail((1024, 1024))
            
            # Convert to bytes
            import io
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            img_byte_arr = img_byte_arr.getvalue()
            img_base64 = base64.b64encode(img_byte_arr).decode()

        # Construct Prompt
        message = HumanMessage(content=[
            {
                "type": "text",
                "text": f"""You are a strict fashion merchandising AI.
                Compare this image to the following description: "{description}"
                
                You must verify if the item visually matches the description features:
                - Material (e.g. Velvet vs Cotton)
                - Color (e.g. Green vs Blue)
                - Pattern (e.g. Rose/Flower vs Plain)
                
                Respond in JSON:
                {{
                    "match_score": <0-100>,
                    "reasoning": "<short explanation>"
                }}
                """
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}
            }
        ])

        # Invoke AI
        print("🤖 Sending to Gemini...")
        response = llm.invoke([message])
        
        # Parse Result
        result = json.loads(response.content.replace('```json', '').replace('```', ''))
        print(f"✅ Result: {result['match_score']}% Match")
        print(f"📝 Reasoning: {result['reasoning']}")
        return result

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    target_description = "green velvet rose flowered shirt"
    
    # NOTE: Since image generation failed, please ensure these files exist or update paths
    # Updated to use the specific test images requested
    valid_image = "green_shirt_1.png"
    invalid_image = "green_shirt_2.png"
    
    print("--- TEST CASE 1: VALID IMAGE (Green Velvet + Rose) ---")
    analyze_image(valid_image, target_description)
    
    print("\n--- TEST CASE 2: INVALID IMAGE (Green Velvet Only) ---")
    analyze_image(invalid_image, target_description)
