import os
import json
import logging
from typing import List, Dict
from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from services.search_service import search_service
import re

logger = logging.getLogger(__name__)

def _extract_json_from_response(text: str) -> List[Dict]:
    """
    Extracts and parses a JSON array from a string, even if it's embedded in other text.
    """
    # Find the start of the JSON array
    json_start_match = re.search(r'\[', text)
    if not json_start_match:
        logger.error("No JSON array found in the LLM response.")
        return []

    json_start_index = json_start_match.start()
    
    # Find the corresponding end of the JSON array
    json_end_index = -1
    open_brackets = 0
    in_string = False
    
    for i in range(json_start_index, len(text)):
        char = text[i]
        
        if char == '"' and (i == 0 or text[i-1] != '\\'):
            in_string = not in_string
        
        if not in_string:
            if char == '[':
                open_brackets += 1
            elif char == ']':
                open_brackets -= 1
        
        if open_brackets == 0 and char == ']':
            json_end_index = i + 1
            break
            
    if json_end_index == -1:
        logger.error("Could not find the end of the JSON array.")
        return []

    json_str = text[json_start_index:json_end_index]
    
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse extracted JSON: {e}")
        logger.debug(f"Extracted JSON string: {json_str}")
        return []

class TrendAgent:
    def __init__(self):
        print("Initializing Vertex AI LLM for trend agent...")
        self.llm = ChatVertexAI(
            model="gemini-2.5-pro",
            project=os.getenv("GOOGLE_CLOUD_PROJECT"),
            location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-east4"),
            temperature=0.2,
            model_kwargs={"generation_config": {"response_mime_type": "application/json"}}
        )
        
    def get_daily_trends(self) -> List[Dict]:
        """
        Searches for latest trends and uses LLM to aggregate a top 20 list.
        """
        queries = [
            "January 2026 men's prom suit trends colors styles",
            "January 2026 men's wedding suit trends guest and groom",
            "2026 men's office wear fashion trends suits business casual",
            "trending men's accessories ties shoes January 2026",
            "men's fashion reddit January 2026 trends",
            "2026 male fashion influencer styles patterns"
        ]
        
        print("DEBUG: Searching web for trends...")
        search_results = search_service.batch_search(queries)
        print(f"DEBUG: Search Results gathered (length: {len(search_results)})")
        
        template = """
        You are a fashion trend analyst for a high-end men's suit retailer.
        Your task is to analyze the provided web search results and identify the top 20-25 fashion trends for January 2026.

        Analyze the following search results:
        ----------------
        {search_results}
        ----------------

        Based *only* on the information in the search results, identify key trends.
        Focus on:
        - Suit styles (e.g., double-breasted, slim fit)
        - Colors (e.g., emerald green, pastel pink)
        - Fabrics (e.g., velvet, linen)
        - Patterns (e.g., pinstripe, floral)
        - Specific items (e.g., wide-leg trousers, chunky loafers)

        For each trend, provide the following information in a JSON object:
        - "name": A short, catchy name for the trend (e.g., "Velvet Tuxedo").
        - "category": "Suit", "Shoes", "Tie", or "Accessory".
        - "description": A one-sentence summary of the trend.
        - "colors": A list of 2-4 relevant colors.
        - "pattern_details": A brief description of any associated patterns, if applicable.

        IMPORTANT:
        1.  Respond with ONLY a raw JSON array of objects.
        2.  Do not include any introductory text, explanations, or markdown formatting like ```json.
        3.  Ensure the output is a valid, parseable JSON array.
        4.  Synthesize information from multiple sources to create a comprehensive trend list.

        Example of a single JSON object in the array:
        {{
            "name": "Emerald Green Suit",
            "category": "Suit",
            "description": "Rich, jewel-toned emerald green suits are making a statement for formal events.",
            "colors": ["emerald", "deep green", "forest green"],
            "pattern_details": "Solid color, often in velvet or satin fabrics."
        }}

        Now, generate the JSON array based on the provided search results.
        """
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["search_results"]
        )
        
        chain = prompt | self.llm
        
        try:
            response = chain.invoke({"search_results": search_results})
            content = response.content
            
            # Use the robust JSON extraction function
            trends = _extract_json_from_response(content)
            
            if not trends:
                print("WARNING: LLM did not return a valid JSON array. Trying to parse with a less strict method.")
                # Fallback for simple cases
                try:
                    trends = json.loads(content)
                except json.JSONDecodeError:
                    print("ERROR: Fallback JSON parsing also failed.")
                    print(f"DEBUG: Raw LLM Output:\n---\n{content}\n---")
                    return []

            return trends
        except Exception as e:
            print(f"Failed to generate trends: {e}")
            # If there's an exception, log the raw response if possible
            if 'response' in locals() and hasattr(response, 'content'):
                print(f"DEBUG: Raw LLM Output on exception:\n---\n{response.content}\n---")
            return []

trend_agent = TrendAgent()
