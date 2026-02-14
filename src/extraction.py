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
        You are an expert Knowledge Graph architect. Your task is to extract structured data from the following text chunk to build a GraphRAG-ready knowledge graph.
        
        Extract the following:
        1. **Entities**: Identify Core Entities (Company, Platform, Service, Product, Capability, Partner, etc.).
           - Include 'name', 'type', and a dictionary of 'attributes' (e.g., description, tags, years).
        2. **Relationships**: Identify relationships between these entities. 
           - Use neutral verbs like: operates, offers, enabled_by, supported_by, includes, integrated_surface, executed_via, acquired, has_event, launched, described_in.
           - If unsure, use 'related_to'.
           - Format: source, target, relation.
        3. **Events**: Identify timeline events specific to the company history.
           - Treat them as entities with type "Event" or separate event objects if preferred, but ensure they link to the company.
        
        **Output Format**:
        Return ONLY a valid JSON object with the following structure:
        {{
            "entities": [
                {{ "name": "EntityName", "type": "EntityType", "attributes": {{ "key": "value" }} }}
            ],
            "relationships": [
                {{ "source": "EntityName", "target": "TargetName", "relation": "relation_verb" }}
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
