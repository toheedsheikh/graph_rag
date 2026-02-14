import os
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

# Ontology Definitions
RELATIONSHIP_TYPES = [
    'operates', 'offers', 'enabled_by', 'supported_by',
    'includes', 'integrated_surface', 'executed_via',
    'acquired', 'has_event', 'launched', 'described_in',
    'related_to', 'benefits_across', 'feature', 'events_experiences_surface', 'expanded_surface'
]

ENTITY_TYPES = [
    'Company', 'Product', 'Service', 'Event', 'Capability', 'Partner', 'Feature', 'Acquisition Target'
]

# LLM Configuration
@dataclass
class LLMConfig:
    api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    model_name: str = "gemini-1.5-flash"
    temperature: float = 0.0
    mock_mode: bool = True # Default to Mock mode for the assignment

# Paths
import pathlib
BASE_DIR = pathlib.Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
INPUT_CHUNKS_PATH = DATA_DIR / "input_chunks.json"
GOLD_STANDARD_PATH = DATA_DIR / "gold_standard.json"
