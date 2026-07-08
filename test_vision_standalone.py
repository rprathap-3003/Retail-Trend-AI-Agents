import os
import base64
import json
from PIL import Image
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# Load environment variables (ensure .env exists with GOOGLE_CLOUD_PROJECT)
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
            img.save(img_byte_arr, format='PNG')
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
                    "reasoning": "<short explanation>",
                    "analysis_label": "AI Analysis of Image"
                }}
                """
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{img_base64}"}
            }
        ])

        # Invoke AI
        print("🤖 Sending to Gemini Vision...")
        response = llm.invoke([message])
        
        # Clean response content (remove markdown if any)
        content = response.content.strip()
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()

        # Parse Result
        result = json.loads(content)
        print(f"✅ Result: {result['analysis_label']}")
        print(f"📊 Match Score: {result['match_score']}%")
        print(f"📝 Reasoning: {result['reasoning']}")
        return result

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    target_description = "green rose flowered shirt"
    
    # These files are generated or mapped by the agent
    valid_image = "colored_shirt_1.jpg"
    invalid_image = "colored_shirt_2.jpg"
    
    print("====================================================")
    print("      RETAIL AI - VISION ACCURACY TEST")
    print("====================================================")
    
    print("\n--- TEST CASE 1: VALID MATCH (Expect High Score) ---")
    analyze_image(valid_image, target_description)
    
    print("\n--- TEST CASE 2: INVALID MATCH (Expect Low Score) ---")
    analyze_image(invalid_image, target_description)
