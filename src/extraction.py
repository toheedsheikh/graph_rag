import json
import logging
import typing
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from google import genai
from .config import LLMConfig, GOLD_STANDARD_PATH

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BaseExtractor(ABC):
    @abstractmethod
    def extract(self, chunk_text: str, chunk_id: int) -> Dict[str, Any]:
        pass

class MockExtractor(BaseExtractor):
    def __init__(self):
        try:
            with open(GOLD_STANDARD_PATH, 'r', encoding='utf-8') as f:
                self.gold_data = json.load(f)
        except FileNotFoundError:
            logger.error(f"Gold standard file not found at {GOLD_STANDARD_PATH}")
            self.gold_data = {}

    def extract(self, chunk_text: str, chunk_id: int) -> Dict[str, Any]:
        """
        Retrieves pre-defined extraction for specific chunks.
        """
        logger.info(f"MockExtractor: Retrieving gold standard data for chunk {chunk_id}")
        # The key in gold_standard.json is "chunk_{id}"
        key = f"chunk_{chunk_id}"
        if key in self.gold_data:
            return self.gold_data[key]
        else:
            logger.warning(f"No gold standard data for chunk {chunk_id}. Returning empty.")
            return {"entities": [], "relationships": [], "events": []}

class GeminiExtractor(BaseExtractor):
    def __init__(self, config: LLMConfig):
        if not config.api_key:
             logger.warning("Gemini API Key not found. Ensure GEMINI_API_KEY is set in environment or .env file.")
        else:
            self.client = genai.Client(api_key=config.api_key)
            self.model_name = config.model_name
    
    def extract(self, chunk_text: str, chunk_id: int) -> Dict[str, Any]:
        logger.info(f"GeminiExtractor: Processing chunk {chunk_id} with LLM")
        
        prompt = f"""
        You are an expert Knowledge Graph Architect. Your task is to extract structured data from the following text chunk to build a high-fidelity GraphRAG knowledge graph.
        
        **Goal**: Build a graph that captures the *structure*, *capabilities*, and *evolution* of the company described.
        
        **3-Step Extraction Rules**:

        1. **Entities**: Identify these specific types:
           - **Company** (e.g., Swiggy, Lynk)
           - **Platform** (Abstract layers like "Consumer Convenience Platform", "Unified Platform")
           - **Service** (e.g., "Food Delivery", "Instamart", "Genie")
           - **Product** (e.g., "Swiggy One", "Credit Card")
           - **Capability** (Foundational elements like "Technology", "Fulfilment", "Analytics")
           - **Partner** (Categories like "Restaurant Partners", "Delivery Partners")
           - **Event** (Major milestones: launches, acquisitions, IPOs. Name format: "Launch <Name> (<Year>)")
           
           *Attributes*: For every entity, extract rich metadata into the 'attributes' dictionary:
           - **description**: Brief summary.
           - **tags**: Keywords (e.g., "Strategy", "Culture").
           - **year**: Launch or acquisition year.
           - **scale**: Numbers (e.g., "124 cities", "500+ cities").
           - **role**: Specific function.

        2. **Relationships**: Connect entities using *only* these verbs where possible:
           - **Structure**: `operates` (Company->Platform), `encompasses` (Platform->Service), `supported_by` (Platform->Partners), `enabled_by` (Platform->Capability).
           - **Actions**: `launched` (Company->Product/Service), `acquired` (Company->Company), `has_event` (Company->Event).
           - **Hierarchy**: `offers` (Company->Service), `includes` (Membership->Benefits), `executed_via` (Service->Product).
           - **Fallback**: `related_to`.

        3. **Events**: 
           - treat Events as distinct entities (Type="Event").
           - Link them to the Company via `has_event`.
           - Link the Event to the affected entity via `launched`, `acquired`, or `milestone_for`.

        **IMPORTANT**: 
        - Capture the **intermediary "Platform" layer** if mentioned (e.g., Swiggy -> operates -> Platform -> offers -> Food Delivery). Do not just flatten everything to the Company.
        - Deduplicate similar concepts (e.g., "Food delivery business" and "Food Delivery" should be one entity).

        **Output Format**:
        Return ONLY a valid JSON object:
        {{
            "entities": [
                {{ "name": "Name", "type": "Type", "attributes": {{ "key": "value" }} }}
            ],
            "relationships": [
                {{ "source": "Name", "target": "Name", "relation": "verb" }}
            ],
            "events": []
        }}
        
        **Text Chunk**:
        {chunk_text}
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config={"response_mime_type": "application/json"}
            )
            return json.loads(response.text)
        except Exception as e:
            logger.error(f"Error invoking Gemini API or parsing response: {e}")
            return {"entities": [], "relationships": [], "events": []}

def get_extractor(config: LLMConfig) -> BaseExtractor:
    if config.mock_mode:
        return MockExtractor()
    else:
        return GeminiExtractor(config)
